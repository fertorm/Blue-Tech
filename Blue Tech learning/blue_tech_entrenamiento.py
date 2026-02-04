from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By  # 📍 Nueva herramienta para buscar
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time


def scraper_interactivo():
    options = Options()
    # Mantén la ventana abierta para que veas al robot trabajar
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    print("🚀 Iniciando entrenamiento interactivo...")
    driver.get("http://books.toscrape.com/")
    time.sleep(2)

    try:
        # 1. Buscamos el botón de la categoría 'Travel' y le damos CLIC
        print("🖱️ El robot está buscando la sección 'Travel'...")
        boton_travel = driver.find_element(By.LINK_TEXT, "Travel")
        boton_travel.click()

        # 2. Esperamos a que la página cambie
        time.sleep(3)
        print("📖 ¡Sección cargada! Extrayendo datos...")

        # 3. Extraemos los nombres de los libros de esa sección
        libros = driver.find_elements(By.TAG_NAME, "h3")
        lista_nombres = [libro.text for libro in libros]

        print(f"✅ Se encontraron {len(lista_nombres)} libros en Travel.")
        return lista_nombres

    except Exception as e:
        print(f"❌ Error en el entrenamiento: {e}")
    finally:
        driver.quit()


# --- EJECUCIÓN ---
libros_viaje = scraper_interactivo()
if libros_viaje:
    print("\n📚 Catálogo de Viajes:")
    for l in libros_viaje:
        print(f"- {l}")
