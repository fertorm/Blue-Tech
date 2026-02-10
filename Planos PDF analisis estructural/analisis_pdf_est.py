import fitz  # PyMuPDF
import pandas as pd
import os

try:
    import pytesseract
    from pdf2image import convert_from_path
except ImportError:
    pytesseract = None
    convert_from_path = None


class BlueTechAnalyzer:
    def __init__(self):
        self.pdf_path = ""
        self.doc = None
        self.keywords = [
            "COL",
            "POST",
            "F30",
            "F35",
        ]  # Basado en tus tablas de cimentación [cite: 811]
        self._configurar_tesseract()

    def _configurar_tesseract(self):
        """Configura la ruta de Tesseract automáticamente o pide ayuda al usuario."""
        if not pytesseract:
            return

        # 1. Verificar si ya está en el PATH
        try:
            pytesseract.get_tesseract_version()
            print("✅ Tesseract detectado en el sistema.")
            return
        except pytesseract.TesseractNotFoundError:
            pass

        # 2. Buscar en rutas comunes
        rutas_comunes = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe"),
            os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
        ]

        for ruta in rutas_comunes:
            if os.path.exists(ruta):
                pytesseract.pytesseract.tesseract_cmd = ruta
                print(f"✅ Tesseract encontrado en: {ruta}")
                return

        # 3. Si falla, pedir ruta al usuario (solo si vamos a usar OCR)
        # Lo dejamos pendiente hasta que se requiera OCR para no molestar al inicio.
        self.tesseract_manual = True

    def configurar_proyecto(self):
        """Solicita la ruta y carga el documento"""
        while True:
            ruta = input(
                "\n[Blue Tech] Introduce la ruta del PDF estructural: "
            ).strip()
            # Limpiar comillas si el usuario arrastra el archivo a la terminal
            ruta = ruta.replace('"', "").replace("'", "")

            if os.path.exists(ruta):
                self.pdf_path = ruta
                self.doc = fitz.open(ruta)
                print(f"✅ Archivo cargado: {len(self.doc)} páginas detectadas.")
                break
            print("❌ Error: No se encuentra el archivo. Intenta de nuevo.")

    def seleccionar_hojas(self):
        """Muestra las páginas y solicita cuáles analizar"""
        print("\n--- Selección de Hojas para Análisis ---")
        # Mostramos un resumen de las páginas para ayudar al usuario
        for i in range(len(self.doc)):
            # Extraemos el inicio del texto para identificar el título del plano
            preview = self.doc[i].get_text("text")[:50].replace("\n", " ")
            print(f"[{i}] {preview}...")

            print(f"[{i}] {preview}...")

        while True:
            try:
                entrada = input(
                    "\nIntroduce los índices de las hojas (ejemplo: 17,18,19): "
                )
                indices = [int(x.strip()) for x in entrada.split(",")]
                return indices
            except ValueError:
                print("❌ Entrada inválida. Usa números separados por comas.")

    def ejecutar_mapeo(self, paginas):
        """Realiza el escaneo de coordenadas en las páginas elegidas"""
        resultados = []
        print("\n🔍 Escaneando elementos estructurales...")

        for p_idx in paginas:
            if p_idx >= len(self.doc):
                continue

            page = self.doc[p_idx]
            # Usamos el diccionario de objetos para obtener coordenadas exactas [x0, y0, x1, y1]
            words = page.get_text("words")

            for w in words:
                contenido = w[4].upper()
                if any(key in contenido for key in self.keywords):
                    resultados.append(
                        {
                            "Página": p_idx,
                            "Etiqueta": w[4],
                            "X_Centro": round((w[0] + w[2]) / 2, 2),
                            "Y_Centro": round((w[1] + w[3]) / 2, 2),
                            "BBox": (w[0], w[1], w[2], w[3]),
                        }
                    )

        df = pd.DataFrame(resultados)
        return df

    def extraer_con_ocr(self, paginas):
        """
        OPCIÓN 2: Motor de OCR (Fallback).
        Intenta leer texto de imágenes rasterizadas.
        """
        if not pytesseract or not convert_from_path:
            print(
                "❌ Error: Faltan librerías. Ejecuta: pip install pytesseract pdf2image"
            )
            return pd.DataFrame()

        print("\n[INFO] Iniciando motor OCR... (Esto puede tardar unos segundos)")
        print("💡 Nota: Asegúrate de tener Tesseract-OCR instalado en tu sistema.")

        resultados = []

        # Asumiendo 200 DPI por defecto para pdf2image si no se especifica.
        # Coordenadas PDF suelen ser 72 DPI.
        DPI_OCR = 200
        SCALE_FACTOR = 72 / DPI_OCR

        for p_idx in paginas:
            print(f"   > Procesando página {p_idx} con OCR...")
            try:
                # convert_from_path usa first_page/last_page base-1
                images = convert_from_path(
                    self.pdf_path,
                    first_page=p_idx + 1,
                    last_page=p_idx + 1,
                    dpi=DPI_OCR,
                )
                if not images:
                    continue

                img = images[0]
                # Obtenemos datos detallados (cajas, confianza, texto)
                data = pytesseract.image_to_data(
                    img, output_type=pytesseract.Output.DICT
                )

                n_boxes = len(data["text"])
                for i in range(n_boxes):
                    # Filtramos confianza y textos vacíos
                    if int(data["conf"][i]) > 40:
                        texto = data["text"][i].upper().strip()
                        if any(k in texto for k in self.keywords):
                            x_px = data["left"][i]
                            y_px = data["top"][i]
                            w_px = data["width"][i]
                            h_px = data["height"][i]

                            # Convertir px a pt
                            x_pt = (x_px + w_px / 2) * SCALE_FACTOR
                            y_pt = (y_px + h_px / 2) * SCALE_FACTOR

                            resultados.append(
                                {
                                    "Página": p_idx,
                                    "Etiqueta": texto,
                                    "X_Centro": round(x_pt, 2),
                                    "Y_Centro": round(y_pt, 2),
                                    "BBox": (x_px, y_px, w_px, h_px),
                                }
                            )
                            print(
                                f"     -> Encontrado: {texto} en ({round(x_pt,1)}, {round(y_pt,1)})"
                            )

            except Exception as e:
                print(f"❌ Error en OCR pág {p_idx}: {e}")
                if "tesseract is not installed" in str(e).lower():
                    print("❗ CRÍTICO: Tesseract no está en el PATH.")
                    print(
                        "Descárgalo aquí: https://github.com/UB-Mannheim/tesseract/wiki"
                    )
                    return pd.DataFrame()

        return pd.DataFrame(resultados)


# --- FLUJO PRINCIPAL ---
if __name__ == "__main__":
    print("========================================")
    print("      BLUE TECH - STRUCTURAL AI         ")
    print("========================================")

    app = BlueTechAnalyzer()
    app.configurar_proyecto()

    hojas_a_revisar = app.seleccionar_hojas()
    df_final = app.ejecutar_mapeo(hojas_a_revisar)

    if df_final.empty:
        print("\n⚠️  No se detectaron etiquetas de texto (Metadatos vacíos).")
        resp = (
            input("¿El plano es una imagen escaneada? ¿Intentar con OCR? (s/n): ")
            .strip()
            .lower()
        )

        if resp == "s":
            df_final = app.extraer_con_ocr(hojas_a_revisar)

    if not df_final.empty:
        print("\n✅ Mapeo de Coordenadas Completado:")
        print(df_final.to_string(index=False))

        # Guardar resultado para análisis de continuidad
        df_final.to_csv("mapeo_columnas_bluetech.csv", index=False)
        print("\n💾 Datos exportados a 'mapeo_columnas_bluetech.csv'")
    else:
        print("\n❌ No se extrajo información. Verifica el PDF o instala Tesseract.")
