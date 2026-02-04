import requests
from bs4 import BeautifulSoup
import pandas as pd  # El "Organizador Mágico"

url = "https://quotes.toscrape.com/"
respuesta = requests.get(url)
sopa = BeautifulSoup(respuesta.text, "html.parser")
citas_html = sopa.find_all("div", class_="quote")

# Creamos una lista vacía para guardar nuestros datos
lista_datos = []

for item in citas_html:
    texto = item.find("span", class_="text").text
    autor = item.find("small", class_="author").text
    # Guardamos como un pequeño diccionario
    lista_datos.append({"Frase": texto, "Autor": autor})

# Convertimos la lista en una Tabla de Pandas (DataFrame)
df = pd.DataFrame(lista_datos)

# Mostramos los primeros 5 renglones
print(df.head())

# ¡Lo guardamos en un archivo para Excel!
import os

os.makedirs("../data", exist_ok=True)
df.to_csv("../data/citas_bolivia.csv", index=False)
print("\nArchivo '../data/citas_bolivia.csv' creado con éxito.")
