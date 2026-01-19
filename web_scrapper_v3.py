import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

from urllib.parse import urljoin

# Configuración de fuentes (Mapa de selectores)
# Nota: Los selectores CSS deben verificarse periódicamente ya que los sitios cambian
FUENTES = [
    # --- EUROPA ---
    {
        "pais": "España",
        "url": "https://elpais.com",
        "selector": "h2",
        "code": "ESP",
    },
    {
        "pais": "Reino Unido",
        "url": "https://www.bbc.com/news",
        "selector": "h2",
        "code": "GBR",
    },
    {
        "pais": "Francia",
        "url": "https://www.lemonde.fr",
        "selector": "h3",
        "code": "FRA",
    },
    {
        "pais": "Alemania",
        "url": "https://www.spiegel.de",
        "selector": "h2",
        "code": "DEU",
    },
    {
        "pais": "Italia",
        "url": "https://www.repubblica.it",
        "selector": "h2",
        "code": "ITA",
    },
    # --- NORTH AMERICA ---
    {
        "pais": "México",
        "url": "https://www.eluniversal.com.mx",
        "selector": "h2",
        "code": "MEX",
    },
    {
        "pais": "USA",
        "url": "https://www.nytimes.com",
        "selector": "p.indicate-hover",  # Ajustado para NYT
        "code": "USA",
    },
    # --- LATAM ---
    {
        "pais": "Brasil",
        "url": "https://www.globo.com",
        "selector": "h2",
        "code": "BRA",
    },
    {
        "pais": "Argentina",
        "url": "https://www.lanacion.com.ar",
        "selector": "h2",
        "code": "ARG",
    },
    {
        "pais": "Bolivia",
        "url": "https://www.eldeber.com.bo",
        "selector": "h2",
        "code": "BOL",
    },
    {
        "pais": "Chile",
        "url": "https://www.latercera.com",
        "selector": "h3",
        "code": "CHL",
    },
    {
        "pais": "Colombia",
        "url": "https://www.eltiempo.com",
        "selector": "h3",
        "code": "COL",
    },
    {
        "pais": "Perú",
        "url": "https://elcomercio.pe",
        "selector": "h2",
        "code": "PER",
    },
    {
        "pais": "Ecuador",
        "url": "https://www.eluniverso.com",
        "selector": "h2",
        "code": "ECU",
    },
    {
        "pais": "Venezuela",
        "url": "https://www.elnacional.com",
        "selector": "h2",
        "code": "VEN",
    },
    {
        "pais": "Uruguay",
        "url": "https://www.elpais.com.uy",
        "selector": "h2",
        "code": "URY",
    },
    {
        "pais": "Paraguay",
        "url": "https://www.abc.com.py",
        "selector": "h2",
        "code": "PRY",
    },
    # --- ASIA ---
    {
        "pais": "Japón",
        "url": "https://www.asahi.com/ajw/",
        "selector": ".Title",  # Selector especifico para Asahi English
        "code": "JPN",
    },
    {
        "pais": "China",
        "url": "https://www.chinadaily.com.cn",
        "selector": "h2",
        "code": "CHN",
    },
    {
        "pais": "India",
        "url": "https://timesofindia.indiatimes.com",
        "selector": "figcaption",
        "code": "IND",
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

            # Buscamos los primeros 5 titulares para no saturar el dashboard
            titulares = soup.select(fuente["selector"])[:5]

            for t in titulares:
                # Estrategia para encontrar el enlace:
                # 1. El propio elemento es un <a>
                # 2. El elemento contiene un <a>
                # 3. El elemento está dentro de un <a>
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

                # Normalizar URL (convertir relativa a absoluta)
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
                    }
                )
            print(f"[OK] {fuente['pais']} procesado correctamente.")
        except Exception as e:
            print(f"[ERROR] Error en {fuente['pais']}: {e}")

    return pd.DataFrame(data_global)


# Ejecución
df_noticias = scrapear_noticias()
df_noticias.to_csv("noticias_mundo.csv", index=False)
