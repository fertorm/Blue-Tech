import pandas as pd
import os

# 1. Intento de ruta automática (GPS por defecto)
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "citas_bolivia.csv")

# 2. Verificación de existencia del archivo
if not os.path.exists(csv_path):
    print(
        "⚠️ ¡Atención! No encontré el archivo 'citas_bolivia.csv' en la carpeta del script."
    )
    # Pedimos la ruta manualmente al usuario
    csv_path = input(
        "Por favor, pega la ruta completa del archivo (incluyendo el nombre y .csv): "
    )
    # Quitamos comillas si el usuario copio como ruta de Windows
    csv_path = csv_path.strip('"')

    if not csv_path.lower().endswith(".csv"):
        print("⚠️ Advertencia: El archivo no parece ser un CSV.")

# 3. Intento de carga final con manejo de errores
try:
    df = pd.read_csv(csv_path)
    print("\n✅ Archivo cargado con éxito desde:", csv_path)

    # Análisis rápido (Día 04)
    print("\n--- RANKING DE AUTORES ---")
    print(df["Autor"].value_counts())

except Exception as e:
    print(f"❌ Error fatal: No se pudo leer el archivo. Detalles: {e}")
