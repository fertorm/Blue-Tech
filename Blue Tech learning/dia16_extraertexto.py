from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import textwrap  # 📏 La herramienta para ajustar el ancho del texto


# --- CLASE DE REPORTE (El Molde) ---
class ReporteMaterial:
    def __init__(self, titulo, contenido):
        self.titulo = titulo
        self.contenido = contenido

    def generar_txt(self):
        # 1. Definimos el nombre del archivo basado en el título
        nombre_archivo = f"BlueTech_Reporte_{self.titulo.replace(' ', '_')}.txt"

        # 2. Aplicamos el ajuste de ancho a 80 caracteres (estándar de lectura)
        texto_ordenado = textwrap.fill(self.contenido, width=80)

        # 3. Escritura con formato de "Hoja de Ingeniería"
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write("=" * 50 + "\n")
            f.write("        SISTEMA DE INTELIGENCIA BLUE TECH\n")
            f.write("=" * 50 + "\n")
            f.write(f"TEMA:       {self.titulo.upper()}\n")
            f.write(f"SOLICITADO: Ingeniero Luis Fernando\n")
            f.write(f"FECHA:      {time.strftime('%d/%m/%Y %H:%M')}\n")
            f.write("-" * 50 + "\n\n")
            f.write(texto_ordenado)  # Aquí va el párrafo ya bien cortado
            f.write("\n\n" + "-" * 50 + "\n")
            f.write("Fin del reporte automatizado.\n")

        print(f"✅ ¡Reporte generado con éxito!: {nombre_archivo}")


# --- MOTOR DE NAVEGACIÓN ---
def ejecutar_estudio_mercado(termino):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    try:
        print(f"🚀 Blue Tech: Analizando '{termino}'...")
        driver.get("https://es.wikipedia.org/")

        # Buscamos el ID que ya conocemos de nuestro reporte CSV
        id_busqueda = "searchInput"
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, id_busqueda))
        )

        # Inyección JavaScript v4 (La que no falla)
        script = f"var i = document.getElementById('{id_busqueda}'); i.value = '{termino}'; i.form.submit();"
        driver.execute_script(script)

        # Extraemos Título y el Primer Párrafo real (saltando párrafos vacíos)
        titulo_web = (
            WebDriverWait(driver, 10)
            .until(EC.presence_of_element_located((By.ID, "firstHeading")))
            .text
        )
        parrafo_web = driver.find_element(
            By.CSS_SELECTOR, "#mw-content-text p:not(.mw-empty-elt)"
        ).text

        # Creamos el objeto y ejecutamos el método de guardado
        nuevo_reporte = ReporteMaterial(titulo_web, parrafo_web)
        nuevo_reporte.generar_txt()

    except Exception as e:
        print(f"❌ Error en la fase de extracción: {e}")
    finally:
        driver.quit()


# --- EJECUCIÓN ---
if __name__ == "__main__":
    ejecutar_estudio_mercado("Hormigón")
