import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

from urllib.parse import urljoin

# Configuración de fuentes (Mapa de selectores)
# Nota: Los selectores CSS deben verificarse periódicamente ya que los sitios cambian
# Configuración de fuentes (Mapa de selectores)
# Nota: Los selectores CSS deben verificarse periódicamente ya que los sitios cambian
FUENTES = [
    # --- EUROPA (General) ---
    {
        "pais": "España",
        "url": "https://elpais.com",
        "selector": "h2",
        "code": "ESP",
        "category": "General",
    },
    {
        "pais": "Reino Unido",
        "url": "https://www.bbc.com/news",
        "selector": "h2",
        "code": "GBR",
        "category": "General",
    },
    {
        "pais": "Francia",
        "url": "https://www.lemonde.fr",
        "selector": "h3",
        "code": "FRA",
        "category": "General",
    },
    {
        "pais": "Alemania",
        "url": "https://www.spiegel.de",
        "selector": "h2",
        "code": "DEU",
        "category": "General",
    },
    {
        "pais": "Italia",
        "url": "https://www.repubblica.it",
        "selector": "h2",
        "code": "ITA",
        "category": "General",
    },
    {
        "pais": "Rusia",
        "url": "https://www.themoscowtimes.com",
        "selector": "h3",
        "code": "RUS",
        "category": "General",
    },
    # --- AMERICAS (General) ---
    {
        "pais": "México",
        "url": "https://www.eluniversal.com.mx",
        "selector": "h2",
        "code": "MEX",
        "category": "General",
    },
    {
        "pais": "USA",
        "url": "https://www.nytimes.com",
        "selector": "p.indicate-hover",
        "code": "USA",
        "category": "General",
    },
    {
        "pais": "Brasil",
        "url": "https://www.globo.com",
        "selector": "h2",
        "code": "BRA",
        "category": "General",
    },
    {
        "pais": "Argentina",
        "url": "https://www.lanacion.com.ar",
        "selector": "h2",
        "code": "ARG",
        "category": "General",
    },
    {
        "pais": "Bolivia",
        "url": "https://www.eldeber.com.bo",
        "selector": "h2",
        "code": "BOL",
        "category": "General",
    },
    {
        "pais": "Chile",
        "url": "https://www.latercera.com",
        "selector": "h3",
        "code": "CHL",
        "category": "General",
    },
    {
        "pais": "Colombia",
        "url": "https://www.eltiempo.com",
        "selector": "h3",
        "code": "COL",
        "category": "General",
    },
    {
        "pais": "Perú",
        "url": "https://elcomercio.pe",
        "selector": "h2",
        "code": "PER",
        "category": "General",
    },
    {
        "pais": "Ecuador",
        "url": "https://www.eluniverso.com",
        "selector": "h2",
        "code": "ECU",
        "category": "General",
    },
    {
        "pais": "Venezuela",
        "url": "https://www.elnacional.com",
        "selector": "h2",
        "code": "VEN",
        "category": "General",
    },
    {
        "pais": "Uruguay",
        "url": "https://www.elpais.com.uy",
        "selector": "h2",
        "code": "URY",
        "category": "General",
    },
    {
        "pais": "Paraguay",
        "url": "https://www.abc.com.py",
        "selector": "h2",
        "code": "PRY",
        "category": "General",
    },
    {
        "pais": "Panamá",
        "url": "https://www.prensa.com",
        "selector": "h2",
        "code": "PAN",
        "category": "General",
    },
    {
        "pais": "Costa Rica",
        "url": "https://www.nacion.com",
        "selector": "h2",
        "code": "CRI",
        "category": "General",
    },
    # --- ASIA / OCEANIA (General) ---
    {
        "pais": "Japón",
        "url": "https://www.asahi.com/ajw/",
        "selector": ".Title",
        "code": "JPN",
        "category": "General",
    },
    {
        "pais": "China",
        "url": "https://www.chinadaily.com.cn",
        "selector": "h2",
        "code": "CHN",
        "category": "General",
    },
    {
        "pais": "India",
        "url": "https://timesofindia.indiatimes.com",
        "selector": "figcaption",
        "code": "IND",
        "category": "General",
    },
    {
        "pais": "Australia",
        "url": "https://www.smh.com.au",
        "selector": "h3",
        "code": "AUS",
        "category": "General",
    },
    # --- AFRICA (General) ---
    {
        "pais": "Sudáfrica",
        "url": "https://www.news24.com",
        "selector": "h4",
        "code": "ZAF",
        "category": "General",
    },
    {
        "pais": "Marruecos",
        "url": "https://en.hespress.com",
        "selector": "h3",
        "code": "MAR",
        "category": "General",
    },
    {
        "pais": "Argelia",
        "url": "https://www.aps.dz/en",
        "selector": "h3",
        "code": "DZA",
        "category": "General",
    },
    {
        "pais": "Camerún",
        "url": "https://www.cameroon-tribune.cm",
        "selector": "h3",
        "code": "CMR",
        "category": "General",
    },
    # --- DEPORTES (Nuevas Fuentes) ---
    {
        "pais": "España",
        "url": "https://www.marca.com",
        "selector": "h2",
        "code": "ESP",
        "category": "Deportes",
    },
    {
        "pais": "USA",
        "url": "https://www.espn.com",
        "selector": "h2",
        "code": "USA",
        "category": "Deportes",
    },
    {
        "pais": "Francia",
        "url": "https://www.lequipe.fr",
        "selector": "h2",
        "code": "FRA",
        "category": "Deportes",
    },
    {
        "pais": "Argentina",
        "url": "https://www.ole.com.ar",
        "selector": "h2",
        "code": "ARG",
        "category": "Deportes",
    },
    {
        "pais": "Reino Unido",
        "url": "https://www.skysports.com",
        "selector": "h3",
        "code": "GBR",
        "category": "Deportes",
    },
    {
        "pais": "Brasil",
        "url": "https://ge.globo.com",
        "selector": "h2",
        "code": "BRA",
        "category": "Deportes",
    },
]


def scrapear_noticias():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    data_global = []

    for fuente in FUENTES:
        try:
            response = requests.get(fuente["url"], headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            # Buscamos los primeros 5 titulares
            titulares = soup.select(fuente["selector"])[:5]

            if not titulares:
                # Si no se encuentran titulares, lo consideramos un error de scraping (selector inválido o cambio en web)
                raise ValueError(
                    "No se encontraron titulares con el selector proporcionado."
                )

            for t in titulares:
                enlace = None
                if t.name == "a" and t.has_attr("href"):
                    enlace = t["href"]
                else:
                    child_a = t.find("a", href=True)
                    if child_a:
                        enlace = child_a["href"]
                    else:
                        parent_a = t.find_parent("a", href=True)
                        if parent_a:
                            enlace = parent_a["href"]

                # Normalizar URL
                url_completa = (
                    urljoin(fuente["url"], enlace) if enlace else "No encontrado"
                )

                data_global.append(
                    {
                        "pais": fuente["pais"],
                        "iso_alpha": fuente["code"],
                        "titular": t.get_text(strip=True),
                        "enlace": url_completa,
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "category": fuente.get("category", "General"),
                        "status": "ok",
                    }
                )
            print(
                f"[OK] {fuente['pais']} ({fuente.get('category', 'General')}) procesado correctamente."
            )

        except Exception as e:
            print(
                f"[ERROR] Error en {fuente['pais']} ({fuente.get('category', 'General')}): {e}"
            )
            # Registrar el error en el dataset para visualizarlo en Rojo
            data_global.append(
                {
                    "pais": fuente["pais"],
                    "iso_alpha": fuente["code"],
                    "titular": f"Error al cargar datos: {str(e)}",
                    "enlace": fuente["url"],
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "category": fuente.get("category", "General"),
                    "status": "error",
                }
            )

    return pd.DataFrame(data_global)


# Ejecución
if __name__ == "__main__":
    df_noticias = scrapear_noticias()
    df_noticias.to_csv("noticias_mundo.csv", index=False)
