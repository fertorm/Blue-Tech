from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options  # <--- ¡ESTA ES LA QUE FALTA!
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

# ... (mantén tus importaciones iguales)


def scraper_blue_tech_final(url):
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    print(f"🚀 Iniciando exploración profunda en Leroy Merlin...")
    driver.get(url)

    # Tiempo extra para que el JavaScript cargue todo
    time.sleep(8)

    # Scroll para activar la carga de productos (Lazy Load)
    driver.execute_script("window.scrollTo(0, 1000);")
    time.sleep(3)

    sopa = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    # ESTRATEGIA NUEVA: Buscamos artículos o bloques que contengan 'product' en sus clases
    productos = sopa.find_all("article") or sopa.select("div[class*='product']")

    lista_materiales = []
    print(f"📦 Se detectaron {len(productos)} posibles productos. Analizando...")

    for item in productos:
        try:
            # Buscamos el texto más grande (título) y el que tenga el símbolo de Euro/Moneda
            nombre = (
                item.find("p").text.strip()
                if item.find("p")
                else item.find("h3").text.strip()
            )
            # Buscamos cualquier texto que contenga un número y el símbolo de moneda
            precio = item.select_one(
                "span[class*='price'], div[class*='price']"
            ).text.strip()

            if nombre and precio:
                lista_materiales.append({"Material": nombre, "Precio": precio})
        except:
            continue

    return pd.DataFrame(lista_materiales)


# --- EJECUCIÓN ---
url_cemento = "https://www.leroymerlin.es/construccion/cementos-morteros-yesos-escayola/cementos-morteros/"
df_final = scraper_blue_tech_final(url_cemento)

if not df_final.empty:
    print(f"✅ ¡MISIÓN CUMPLIDA! Se capturaron {len(df_final)} materiales.")
    print(df_final.head(10))
    # Guardar en carpeta data (subir un nivel)
    import os

    os.makedirs("../data", exist_ok=True)
    df_final.to_csv("../data/datos_reales_espana.csv", index=False)
else:
    print(
        "⚠️ El sitio es muy complejo. ¿Te parece si probamos con una tienda un poco más sencilla para asegurar la base antes de volver a este 'Jefe Final'?"
    )
