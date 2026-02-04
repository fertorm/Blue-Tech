import requests
from bs4 import BeautifulSoup
import pandas as pd


# 1. Ahora la función pide DOS cosas para trabajar
def extraer_productos(url_tienda, nombre_empresa):
    headers = {"User-Agent": "Mozilla/5.0"}
    respuesta = requests.get(url_tienda, headers=headers)
    sopa = BeautifulSoup(respuesta.text, "html.parser")

    productos = sopa.find_all("article", class_="product_pod")
    datos_materiales = []

    for item in productos:
        nombre = item.h3.a["title"]
        precio = item.find("p", class_="price_color").text

        # 2. Usamos la variable que entró por los paréntesis
        datos_materiales.append(
            {"Material": nombre, "Precio": precio, "Empresa": nombre_empresa}
        )

    return datos_materiales


# --- EJECUCIÓN ---
url = "http://books.toscrape.com/catalogue/category/books/business_35/index.html"

# 3. Aquí es donde definimos los valores reales
mi_empresa_real = "Ferretería El Cóndor - Bolivia"
materiales_encontrados = extraer_productos(url, mi_empresa_real)

df_blue = pd.DataFrame(materiales_encontrados)
print(df_blue.head())
