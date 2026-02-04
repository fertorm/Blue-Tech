import requests
from bs4 import BeautifulSoup
import csv


def inspeccionar_terreno(url):
    print(f"📡 Escaneando código fuente de: {url}")
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        respuesta = requests.get(url, headers=headers)
        sopa = BeautifulSoup(respuesta.text, "html.parser")

        # Buscamos todos los campos donde se puede escribir (inputs)
        inputs = sopa.find_all("input")

        print(f"🔎 Se encontraron {len(inputs)} entradas de texto posibles:")

        # Guardamos en CSV
        nombre_archivo = "reporte_inputs.csv"
        with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            # Escribimos encabezado
            writer.writerow(["Nombre", "ID", "Clase"])

            for i in inputs:
                nombre = i.get("name")
                id_elemento = i.get("id")
                clase = i.get(
                    "class"
                )  # Esto devuelve una lista si hay múltiples clases

                # Mostramos en consola
                print(f"   - Nombre: {nombre} | ID: {id_elemento} | Clase: {clase}")

                # Escribimos en el CSV
                writer.writerow([nombre, id_elemento, clase])

        print(f"✅ Reporte guardado exitosamente en: {nombre_archivo}")

    except Exception as e:
        print(f"❌ Fallo en el escaneo: {e}")


# --- PROBEMOS ---
inspeccionar_terreno("https://es.wikipedia.org/")
