import pdfplumber

def analyze_pdf(pdf_path, output_path):
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("--- RAW TEXT CONTENT ---\n")
            f.write(text if text else "NO TEXT FOUND")
            f.write("\n------------------------\n")
            
            # Also try to print tables if any
            tables = first_page.extract_tables()
            if tables:
                f.write(f"--- FOUND {len(tables)} TABLES ---\n")
                for i, table in enumerate(tables):
                    f.write(f"Table {i+1}:\n")
                    for row in table:
                        f.write(str(row) + "\n")

if __name__ == "__main__":
    pdf_path = r"c:\Users\Usuario\Documents\Blue Tech\Ejemplo PDF plano\218-ENDE-WII-PCZ-D-CI-PL-020=0.pdf"
    output_path = r"c:\Users\Usuario\Documents\Blue Tech\analysis_output.txt"
    analyze_pdf(pdf_path, output_path)
