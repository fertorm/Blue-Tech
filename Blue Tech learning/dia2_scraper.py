import requests
from bs4 import BeautifulSoup

# 1. Definimos la dirección de la "casa" (la web) a la que enviaremos al cartero
url = "https://quotes.toscrape.com/"

# 2. Enviamos al cartero (requests) a pedir la información
print("Enviando cartero a la web...")
respuesta = requests.get(url)

# 3. Usamos la lupa mágica (BeautifulSoup) para entender el idioma de la casa (HTML)
sopa = BeautifulSoup(respuesta.text, "html.parser")

# 4. Buscamos todas las "cajas" de citas en la página
citas = sopa.find_all("div", class_="quote")

# 5. Recorremos todas las cajas y extraemos la información
print(f"\nSe encontraron {len(citas)} citas:\n")

for cita in citas:
    texto = cita.find("span", class_="text").text
    autor = cita.find("small", class_="author").text

    print("--- Cita encontrada ---")
    print(f"Cita: {texto}")
    print(f"Autor: {autor}")
    print("-----------------------")
