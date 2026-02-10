import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import tkinter as tk
from tkinter import filedialog
import sys
import os

# 1. SELECCIÓN DE ARCHIVOS
print("Abriendo ventana de selección de archivos...")
root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)

files = filedialog.askopenfilenames(
    title="Seleccione archivos de Rotura de Grout",
    filetypes=[("Archivos de Datos", "*.xlsx *.xls *.csv"), ("Todos", "*.*")],
)

if not files:
    print("No se seleccionaron archivos. Saliendo.")
    sys.exit()

all_data = []

# 2. PROCESAMIENTO Y LIMPIEZA
for file in files:
    try:
        # Cargamos el archivo (CSV o Excel)
        if file.lower().endswith(".csv"):
            df = pd.read_csv(file, skiprows=5)
        else:
            df = pd.read_excel(file, skiprows=5)

        # Selección de columnas por índice (robusto ante cambios de nombre)
        # ID, Estructura, Fecha Vaciado, Fecha Rotura, Edad, Resistencia
        cols = [1, 2, 5, 6, 7, 13]
        df_clean = df.iloc[:, cols].copy()
        df_clean.columns = [
            "ID_Probeta",
            "Estructura",
            "Fecha_Vaciado",
            "Fecha_Rotura",
            "Edad_Dias",
            "Resistencia_MPa",
        ]

        # Limpieza de metadatos de Excel
        df_clean = df_clean.dropna(subset=["ID_Probeta", "Resistencia_MPa"])
        all_data.append(df_clean)
    except Exception as e:
        print(f"Error procesando {os.path.basename(file)}: {e}")

# 3. CONSOLIDACIÓN
master_df = pd.concat(all_data, ignore_index=True)
master_df["Edad_Dias"] = pd.to_numeric(master_df["Edad_Dias"], errors="coerce")
master_df["Resistencia_MPa"] = pd.to_numeric(
    master_df["Resistencia_MPa"], errors="coerce"
)
master_df = master_df.dropna(subset=["Edad_Dias", "Resistencia_MPa"])

# 4. GENERACIÓN DE RESULTADOS ESTADÍSTICOS
stats_summary = (
    master_df.groupby("Edad_Dias")["Resistencia_MPa"]
    .agg(["count", "mean", "std", "min", "max"])
    .reset_index()
)
stats_summary["CV_%"] = (stats_summary["std"] / stats_summary["mean"]) * 100

# 5. IMPRESIÓN DE TABLAS (Como las del informe)
print("\n" + "=" * 80)
print("INFORME CONSOLIDADO DE CONTROL DE CALIDAD - SIKAGROUT 9400 BR")
print(f"Total de archivos procesados: {len(files)}")
print(f"Total de probetas analizadas: {len(master_df)}")
print("=" * 80)
print("\nESTADÍSTICA DESCRIPTIVA POR EDAD DE ROTURA:")
pd.options.display.float_format = "{:,.2f}".format
print(stats_summary.to_string(index=False))
print("\n" + "=" * 80)

# 6. EXPORTAR Y GRAFICAR
master_df.to_csv("master_data_grout.csv", index=False)

plt.figure(figsize=(10, 6))
sns.boxplot(
    x="Edad_Dias",
    y="Resistencia_MPa",
    hue="Edad_Dias",
    data=master_df,
    palette="viridis",
    legend=False,
)
plt.title("Distribución de Resistencia SikaGrout 9400")
plt.savefig("boxplot_resistencia.png")

plt.figure(figsize=(10, 6))
for age in sorted(master_df["Edad_Dias"].unique()):
    subset = master_df[master_df["Edad_Dias"] == age]
    if len(subset) > 1:
        sns.kdeplot(subset["Resistencia_MPa"], label=f"{int(age)} días", fill=True)
plt.title("Cinética de Resistencia: Densidad de Probabilidad")
plt.legend()
plt.savefig("densidad_resistencia.png")

print("\nProceso finalizado. Gráficos y CSV generados.")
