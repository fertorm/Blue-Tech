import pandas as pd
import matplotlib.pyplot as plt


# 🛠️ MI NUEVA HERRAMIENTA: Función para graficar
def generar_grafico_bolivia(datos, titulo_grafico):
    print(f"📊 Generando: {titulo_grafico}...")
    conteo = datos["Autor"].value_counts().head(10)

    conteo.plot(kind="bar", color="orange", edgecolor="black")
    plt.title(titulo_grafico)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


# --- FLUJO PRINCIPAL ---
# Cargamos el archivo de 100 frases que sacaste ayer
try:
    df_completo = pd.read_csv("citas_completas.csv")

    # ¡USAMOS NUESTRA HERRAMIENTA CON UN SOLO COMANDO!
    generar_grafico_bolivia(df_completo, "Top 10 Autores - Reporte Blue Tech")

except FileNotFoundError:
    print("❌ No encontré el archivo. Asegúrate de haber corrido el script del Día 09.")
