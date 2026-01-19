import pdfplumber
import re
import qrcode
from PIL import Image
import os
import sys


def extract_metadata(pdf_path):
    """
    Extracts metadata from the first page of the PDF.
    Returns a dictionary with the extracted fields.
    """
    metadata = {
        "proyecto": "NO ENCONTRADO",
        "titulo": "NO ENCONTRADO",
        "codigo": "NO ENCONTRADO",
        "revision": "NO ENCONTRADO",
        "fecha": "NO ENCONTRADO",
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            tables = first_page.extract_tables()

            # --- 1. Extract Project Name ---
            # Pattern: "PROYECTO:\n<Name>"
            match_proyecto = re.search(r"PROYECTO:\s*\n(.+)", text)
            if match_proyecto:
                metadata["proyecto"] = match_proyecto.group(1).strip()

            # --- 2. Extract Code ---
            # Pattern: "CÓDIGO DE PLANO: ... \n<Code>" or finding the code pattern directly
            # Code format seen: 218-ENDE-WII-PCZ-D-CI-PL-020
            match_codigo = re.search(r"(\d{3}-ENDE-[\w-]+)", text)
            if match_codigo:
                metadata["codigo"] = match_codigo.group(1).strip()

            # --- 3. Extract Title ---
            # Pattern: "TÍTULO DE PLANO: ... \n<Title Content>\nHOJA:"
            # We look for the line containing "TÍTULO DE PLANO:", skip it (and "Nº PLANO:" if present),
            # and capture everything until "HOJA:" or end of section.
            match_titulo = re.search(
                r"TÍTULO DE PLANO:.*?\n(.*?)(?=\nHOJA:|\nESCALA:|\nPROYECTO:)",
                text,
                re.DOTALL,
            )

            if match_titulo:
                metadata["titulo"] = match_titulo.group(1).replace("\n", " ").strip()
            else:
                # Fallback: Try looking for the old pattern if the new one fails (e.g. different layout)
                match_titulo_old = re.search(
                    r"TÍTULO DE PLANO:\s*(.+?)(?=\nNº PLANO|\nHOJA)", text, re.DOTALL
                )
                if match_titulo_old:
                    metadata["titulo"] = (
                        match_titulo_old.group(1).replace("\n", " ").strip()
                    )

            # --- 4. Extract Revision and Date ---
            # Strategy: Look for the revision table structure in the extracted text or tables.
            # Text based regex for revision lines: Rev Date Desc...
            # We see lines like: "B 03/11/23 TEPSI ..." or "0 08/11/23 ..."
            # We want the latest one (by date or top position).
            # From raw text lines 265-267, they appear in some order.

            rev_pattern = re.compile(r"\b([A-Z0-9])\s+(\d{2}/\d{2}/\d{2})\s+")
            matches_rev = rev_pattern.findall(text)

            if matches_rev:
                # Matches is a list of tuples [('B', '03/11/23'), ('A', '22/09/23'), ...]
                # We need to sort by date to find the latest.
                try:
                    from datetime import datetime

                    # Sort by date descending
                    sorted_revs = sorted(
                        matches_rev,
                        key=lambda x: datetime.strptime(x[1], "%d/%m/%y"),
                        reverse=True,
                    )
                    latest_rev = sorted_revs[0]
                    metadata["revision"] = latest_rev[0]
                    metadata["fecha"] = latest_rev[1]
                except Exception as e:
                    print(f"Error sorting revisions: {e}")
                    # Fallback to the first found or last found depending on assumption
                    metadata["revision"] = matches_rev[0][0]
                    metadata["fecha"] = matches_rev[0][1]

    except Exception as e:
        print(f"Error processing PDF: {e}")

    return metadata


def generate_qr(metadata, output_path):
    """
    Generates a QR code image from the metadata.
    """
    # Format the data string
    # data_str = f"""PROYECTO: {metadata['proyecto']}
    # TITULO: {metadata['titulo']}
    # CODIGO: {metadata['codigo']}
    # REV: {metadata['revision']}
    # FECHA: {metadata['fecha']}"""

    # Or JSON format if preferred, but simple text is readable
    data_str = "|".join(
        [
            metadata["proyecto"],
            metadata["titulo"],
            metadata["codigo"],
            metadata["revision"],
            metadata["fecha"],
        ]
    )

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data_str)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    print(f"QR Generated at: {output_path}")
    print(f"Content: {data_str}")


def main():
    # Use the hardcoded path for now as per previous context or argument
    pdf_path = r"c:\Users\Usuario\Documents\Blue Tech\Ejemplo PDF plano\218-ENDE-WII-PCZ-D-CI-PL-020=0.pdf"

    # If arguments provided
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]

    print(f"Processing: {pdf_path}")

    if not os.path.exists(pdf_path):
        print("File not found.")
        return

    metadata = extract_metadata(pdf_path)

    print("\n--- Extracted Data ---")
    for k, v in metadata.items():
        print(f"{k.upper()}: {v}")
    print("----------------------\n")

    # Generate QR
    qr_filename = f"QR_{metadata['codigo']}_Rev{metadata['revision']}.png"
    # Santize filename
    qr_filename = re.sub(r'[<>:"/\\|?*]', "_", qr_filename)
    output_qr_path = os.path.join(os.path.dirname(pdf_path), qr_filename)

    generate_qr(metadata, output_qr_path)


if __name__ == "__main__":
    main()
