from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
from datetime import datetime


def registrar_error(mensaje):
    archivo_errores = "errores.csv"
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(archivo_errores, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([fecha_hora, mensaje])


def buscar_en_wikipedia_blindado_v4(termino):
    options = Options()
    # Camuflaje para evitar ser detectado
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    try:
        print(f"🚀 Blue Tech: Iniciando Protocolo de Envío Directo para '{termino}'...")
        driver.get("https://es.wikipedia.org/")

        # 1. Esperamos solo a que el buscador esté presente en el código (no hace falta que sea visible)
        id_busqueda = "searchInput"
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, id_busqueda))
        )

        # 2. ⚡ COMANDO MAESTRO JAVASCRIPT:
        # - Escribe el texto
        # - Busca el formulario y lo envía (submit)
        # Esto ignora cualquier obstáculo visual o "interactividad"
        print("💉 Inyectando texto y activando el envío del formulario...")
        script_maestro = f"""
            var input = document.getElementById('{id_busqueda}');
            input.value = '{termino}';
            input.form.submit();
        """
        driver.execute_script(script_maestro)

        # 3. Esperar el resultado final
        titulo = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "firstHeading"))
        )
        print(f"✅ ¡ÉXITO TOTAL! Hemos llegado a: {titulo.text}")
        return titulo.text

    except Exception as e:
        error_msg = f"Falla en v4: {str(e)}"
        print(f"❌ El sistema volvió a fallar. Registrando en CSV...")
        registrar_error(error_msg)
    finally:
        driver.quit()


if __name__ == "__main__":
    buscar_en_wikipedia_blindado_v4("Ingeniería Civil")
