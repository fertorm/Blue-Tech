import pandas as pd
from generador_dashboard_noticias import procesar_datos_mapa
import os

csv_path = "noticias_mundo.csv"
if not os.path.exists(csv_path):
    print("CSV not found!")
    exit()

df = pd.read_csv(csv_path)

# Fill missing cols as per original script
if "category" not in df.columns:
    df["category"] = "General"
if "status" not in df.columns:
    df["status"] = "ok"

df_general = df[df["category"] == "General"]
df_agg = procesar_datos_mapa(df_general)

if df_agg.empty:
    print("Aggregated DataFrame is empty.")
else:
    print("Columns:", df_agg.columns)
    print("\nFirst 3 rows:")
    print(df_agg[["pais", "titulares_resumen", "cantidad_noticias"]].head(3))

    print("\nSample Headline Content (first row):")
    print(df_agg["titulares_resumen"].iloc[0])
