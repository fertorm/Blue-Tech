import pandas as pd
import matplotlib.pyplot as plt
import os

# Tu lógica de GPS mejorada
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "citas_bolivia.csv")

if not os.path.exists(csv_path):
    csv_path = input("⚠️ Ruta no encontrada. Pégala aquí: ").strip('"')

try:
    df = pd.read_csv(csv_path)
    ranking = df["Autor"].value_counts()

    # --- El Dibujante (Matplotlib) ---
    ranking.plot(kind="bar", color="orange", edgecolor="black")

    plt.title("Ranking de Autores - Blue Tech")
    plt.ylabel("Citas")
    plt.xticks(rotation=45)
    plt.tight_layout()

    print("🎨 Abriendo el lienzo...")
    plt.show()

except Exception as e:
    print(f"❌ Error al graficar: {e}")
