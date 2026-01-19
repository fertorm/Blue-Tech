import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from urllib.parse import urljoin, urlparse


class WebScraper:
    def __init__(self, url):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

    def obtener_noticias(self):
        """
        Extrae titulares y enlaces de la página web proporcionada.
        Busca etiquetas h2 y h3 que suelen contener titulares.
        """
        try:
            print(f"🔬 Iniciando extracción en: {self.url}...")
            response = requests.get(self.url, headers=self.headers, timeout=15)
            response.raise_for_status()

            # Intentar detectar la codificación correcta
            if response.encoding.lower() != "utf-8":
                response.encoding = response.apparent_encoding

            soup = BeautifulSoup(response.text, "html.parser")
            lista_noticias = []

            # Buscamos elementos h2 y h3 que tengan texto y un enlace cercano
            for item in soup.find_all(["h2", "h3"]):
                titulo = item.get_text(strip=True)
                enlace_tag = item.find("a") or item.find_parent("a")

                if titulo and enlace_tag and "href" in enlace_tag.attrs:
                    url_relativa = enlace_tag["href"]
                    # Convertir enlace relativo a absoluto
                    url_completa = urljoin(self.url, url_relativa)

                    # Evitar duplicados y filtrar ruidos (textos muy cortos)
                    if len(titulo) > 15 and url_completa not in [
                        n["Enlace"] for n in lista_noticias
                    ]:
                        lista_noticias.append(
                            {
                                "Fecha_Captura": datetime.now().strftime(
                                    "%Y-%m-%d %H:%M"
                                ),
                                "Titular": titulo,
                                "Enlace": url_completa,
                            }
                        )

            return lista_noticias

        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return []

    def exportar_datos(self, datos):
        """Almacena los resultados en un archivo CSV."""
        if not datos:
            print("⚠️ No se encontraron datos para exportar.")
            return

        # Extraer el nombre del dominio para el nombre del archivo
        parsed_url = urlparse(self.url)
        dominio = parsed_url.netloc.replace("www.", "").replace(".", "_")

        df = pd.DataFrame(datos)
        nombre_archivo = (
            f"noticias_{dominio}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        )

        try:
            df.to_csv(nombre_archivo, index=False, encoding="utf-8-sig")
            print(
                f"✅ Éxito: Se han guardado {len(df)} noticias en '{nombre_archivo}'."
            )
        except Exception as e:
            print(f"❌ Error al guardar el archivo: {e}")


# --- Ejecución del Programa ---
if __name__ == "__main__":
    print("--- Web Scraper Genérico ---")
    url_input = input(
        "Ingrese la URL del sitio web a analizar (ej. https://eldeber.com.bo): "
    ).strip()

    if url_input:
        if not url_input.startswith("http"):
            url_input = "https://" + url_input

        app = WebScraper(url_input)
        noticias = app.obtener_noticias()

        # Mostrar resultados en consola
        print(f"\n--- Resultados encontrados: {len(noticias)} ---")
        for i, n in enumerate(noticias[:5], 1):  # Mostrar las primeras 5
            print(f"{i}. {n['Titular']}")

        app.exportar_datos(noticias)
    else:
        print("⚠️ Debe ingresar una URL válida.")
