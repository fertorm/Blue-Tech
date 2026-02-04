import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://quotes.toscrape.com/"
respuesta = requests.get(url)
sopa = BeautifulSoup(respuesta.text, "html.parser")
citas_html = sopa.find_all("div", class_="quote")

lista_filtrada = []

# Aquí definimos quién es nuestro "Invitado Especial"
autor_objetivo = "Albert Einstein"

for item in citas_html:
    autor = item.find("small", class_="author").text
    texto = item.find("span", class_="text").text

    # EL CEREBRO: ¿El autor de esta cita es el que buscamos?
    # Si autor_objetivo es None, guardamos todo. Si tiene valor, filtramos.
    if autor_objetivo is None or autor == autor_objetivo:
        print(f"✅ ¡Encontrada! Cita de {autor}")
        lista_filtrada.append({"Frase": texto, "Autor": autor})
    else:
        print(f"❌ Descartada cita de: {autor}")

# Guardamos solo lo que pasó el filtro
df = pd.DataFrame(lista_filtrada)
import os

os.makedirs("../data", exist_ok=True)
df.to_csv("../data/citas_filtradas.csv", index=False)

print(f"\nProceso terminado. Se guardaron {len(lista_filtrada)} frases.")
