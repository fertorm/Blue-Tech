import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt

base_url = "https://quotes.toscrape.com"
url_actual = "/page/1/"
lista_final = []
autor_objetivo = None  # Usa None para traer todo, o un nombre para filtrar

print("🚀 Iniciando motor de búsqueda masiva...")

while url_actual:
    print(f"📄 Procesando: {base_url}{url_actual}")
    respuesta = requests.get(base_url + url_actual)
    sopa = BeautifulSoup(respuesta.text, "html.parser")

    citas_html = sopa.find_all("div", class_="quote")

    for item in citas_html:
        autor = item.find("small", class_="author").text
        texto = item.find("span", class_="text").text

        # Usando tu mejora lógica del Día 08
        if autor_objetivo is None or autor == autor_objetivo:
            lista_final.append({"Frase": texto, "Autor": autor})

    # BUSCADOR DE "PÁGINA SIGUIENTE"
    # Buscamos la etiqueta <li> con clase 'next' y luego el link <a>
    boton_siguiente = sopa.find("li", class_="next")

    if boton_siguiente:
        url_actual = boton_siguiente.find("a")["href"]
    else:
        url_actual = None  # Aquí el caracol se detiene porque ya no hay más páginas

# Guardado final
df = pd.DataFrame(lista_final)
import os

os.makedirs("../data", exist_ok=True)
df.to_csv("../data/citas_completas.csv", index=False)

print(f"\n✅ ¡Misión cumplida! Recolectadas {len(lista_final)} frases en total.")

# --- NUEVO: Análisis y Gráfico ---
print("\n📊 Generando reporte de autores...")
conteo_autores = df["Autor"].value_counts()
print(conteo_autores)

# Configuración del gráfico (estilo Blue Tech learning)
conteo_autores.head(10).plot(
    kind="bar", color="orange", edgecolor="black"
)  # Top 10 para que sea legible

plt.title("Top Autores por Cantidad de Citas")
plt.ylabel("Cantidad de Citas")
plt.xlabel("Autor")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

print("🎨 Abriendo gráfico...")
plt.show()
