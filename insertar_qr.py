import fitz  # PyMuPDF
import sys
import os


def insertar_qr_en_pdf(
    pdf_path, qr_path, output_path=None, posicion="bottom-right-corner"
):
    """
    Inserta una imagen QR en un archivo PDF.

    Args:
        pdf_path (str): Ruta al archivo PDF original.
        qr_path (str): Ruta a la imagen del código QR.
        output_path (str, optional): Ruta de salida para el nuevo PDF. Si es None, añade '_con_qr' al nombre original.
        posicion (str or tuple): Posición de inserción.
                                 'bottom-right-corner' para ubicarlo cerca del carimbo automáticamente.
                                 O una tupla (x0, y0, x1, y1) para coordenadas manuales.
    """
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"El archivo PDF no existe: {pdf_path}")
        if not os.path.exists(qr_path):
            raise FileNotFoundError(f"El archivo QR no existe: {qr_path}")

        # Abrir el documento
        doc = fitz.open(pdf_path)
        page = doc[0]  # Trabajamos con la primera página por defecto

        # Obtener dimensiones de la página
        page_width = page.rect.width
        page_height = page.rect.height

        # Configuración de tamaño y posición del QR
        qr_size = 100  # Tamaño del cuadrado del QR en puntos (aprox 3.5 cm)
        margin = 20  # Margen desde los bordes

        # Calcular el rectángulo de inserción (Rect)
        if posicion == "bottom-right-corner":
            # Posicionarlo en la esquina inferior derecha, pero arriba del carimbo
            # Asumimos una altura de carimbo de aprox 300 puntos (ajustable)
            # y mantenemos el margen derecho

            margin_right = 20
            margin_bottom = 300  # Aumentado para estar encima del carimbo

            x1 = page_width - margin_right
            x0 = x1 - qr_size
            y1 = page_height - margin_bottom
            y0 = y1 - qr_size

            rect = fitz.Rect(x0, y0, x1, y1)

        elif isinstance(posicion, (tuple, list)) and len(posicion) == 4:
            rect = fitz.Rect(*posicion)
        else:
            # Fallback a posición por defecto si el argumento no es válido
            print("Posición no válida, usando esquina inferior derecha.")
            x1 = page_width - margin
            x0 = x1 - qr_size
            y1 = page_height - margin
            y0 = y1 - qr_size
            rect = fitz.Rect(x0, y0, x1, y1)

        print(f"Insertando QR en: {rect}")

        # Insertar la imagen del QR
        page.insert_image(rect, filename=qr_path)

        # Determinar ruta de salida
        if not output_path:
            base, ext = os.path.splitext(pdf_path)
            output_path = f"{base}_con_qr{ext}"

        # Guardar el documento
        doc.save(output_path)
        doc.close()

        print(f"¡Éxito! Nuevo PDF guardado en: {output_path}")
        return output_path

    except Exception as e:
        print(f"Error al procesar el PDF: {e}")
        return None


def main():
    if len(sys.argv) < 3:
        print("Uso: python insertar_qr.py <ruta_pdf> <ruta_qr> [ruta_salida]")
        # Ejemplo de uso para pruebas rápidas si no se pasan argumentos
        print("\n--- Ejecutando modo prueba con archivos por defecto (si existen) ---")
        base_dir = r"c:\Users\Usuario\Documents\Blue Tech"
        default_pdf = os.path.join(
            base_dir, r"Ejemplo PDF plano\218-ENDE-WII-PCZ-D-CI-PL-020=0.pdf"
        )

        # Intentar buscar el último QR generado
        # (Esto es un helper simple para facilitar la prueba)
        qr_file = None
        for file in os.listdir(os.path.join(base_dir, "Ejemplo PDF plano")):
            if file.startswith("QR_") and file.endswith(".png"):
                qr_file = os.path.join(base_dir, "Ejemplo PDF plano", file)
                break

        if qr_file and os.path.exists(default_pdf):
            print(f"PDF: {default_pdf}")
            print(f"QR: {qr_file}")
            insertar_qr_en_pdf(default_pdf, qr_file)
        else:
            print("No se encontraron archivos de prueba por defecto.")
        return

    pdf_path = sys.argv[1]
    qr_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None

    insertar_qr_en_pdf(pdf_path, qr_path, output_path)


if __name__ == "__main__":
    main()
