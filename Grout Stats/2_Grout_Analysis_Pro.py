import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import tkinter as tk
from tkinter import filedialog
import os

# 1. PARÁMETROS DE LA FICHA TÉCNICA (SikaGrout 9400 BR)
TARGETS = {1.0: 45.0, 7.0: 90.0, 28.0: 110.0}  # Requisitos mínimos en MPa
FCK_REQUIRED = 108.0  # Resistencia característica certificada


def generate_report():
    # SELECCIÓN DE ARCHIVOS
    root = tk.Tk()
    root.withdraw()
    files = filedialog.askopenfilenames(title="Seleccione archivos Excel/CSV de Grout")

    if not files:
        return

    all_data = []
    for file in files:
        try:
            print(f"Procesando: {os.path.basename(file)}...")
            # Detectar extensión
            if file.lower().endswith(".csv"):
                df = pd.read_csv(file, skiprows=5)
            else:
                df = pd.read_excel(file, skiprows=5)

            # Validar columnas
            if df.shape[1] <= 13:
                print(
                    f"  [ALERTA] Archivo {os.path.basename(file)} ignorado (formato incorrecto)."
                )
                continue

            # Selección de columnas por posición
            # 1:ID, 7:Edad, 13:MPa (Indices)
            df_clean = df.iloc[:, [1, 7, 13]].copy()
            df_clean.columns = ["ID", "Edad", "MPa"]

            # Limpieza básica
            df_clean = df_clean.dropna()
            all_data.append(df_clean)
        except Exception as e:
            print(f"  [ERROR] en {os.path.basename(file)}: {e}")
            continue

    if not all_data:
        print("No se procesaron datos validos.")
        return

    df_master = pd.concat(all_data, ignore_index=True)
    # Convertir a numérico solo las columnas necesarias para no perder datos por IDs de texto
    df_master["Edad"] = pd.to_numeric(df_master["Edad"], errors="coerce")
    df_master["MPa"] = pd.to_numeric(df_master["MPa"], errors="coerce")

    # Eliminar filas solo si faltan datos numéricos críticos
    df_master = df_master.dropna(subset=["Edad", "MPa"])

    if df_master.empty:
        print("Error: No quedaron datos validos despues de la limpieza.")
        return

    # --- ANÁLISIS ESTADÍSTICO ---
    stats_df = (
        df_master.groupby("Edad")["MPa"]
        .agg(["count", "mean", "std", "min", "max"])
        .reset_index()
    )
    stats_df["CV%"] = (stats_df["std"] / stats_df["mean"]) * 100

    # --- INFERENCIA (28 DÍAS) ---
    data_28 = df_master[df_master["Edad"] == 28.0]["MPa"]
    if not data_28.empty:
        t_stat, p_val = stats.ttest_1samp(data_28, TARGETS[28.0])
        # Resistencia Característica (f'ck) real del proyecto
        mean_28 = data_28.mean()
        std_28 = data_28.std()
        fck_project = mean_28 - (1.645 * std_28)
    else:
        p_val = 1.0
        fck_project = 0.0

    # --- GENERACIÓN DEL REPORTE TEXTUAL ---
    report_path = "Reporte_Control_Calidad_Grout.txt"
    with open(report_path, "w") as f:
        f.write("=" * 100 + "\n")
        f.write(" REPORTE DE CONTROL ESTATÍSTICO: SIKAGROUT 9400 BR\n")
        f.write("=" * 100 + "\n\n")

        f.write(f"PROBETAS ANALIZADAS: {len(df_master)}\n")
        f.write(f"CUMPLIMIENTO DE RESISTENCIA MEDIA Y DISPERSIÓN:\n")
        f.write("-" * 100 + "\n")
        # Encabezados alineados
        f.write(
            f"{'Edad':<6} {'N°':<5} {'Media':<10} {'Desv':<10} {'Mín':<10} {'Máx':<10} {'CV%':<8} {'Meta':<10} {'Estado'}\n"
        )

        for _, row in stats_df.iterrows():
            target = TARGETS.get(row["Edad"], "N/A")
            status = (
                "PASA"
                if (isinstance(target, float) and row["mean"] >= target)
                else "---"
            )
            target_str = f"{target}" if isinstance(target, float) else "-"

            f.write(
                f"{row['Edad']:<6.0f} {int(row['count']):<5} {row['mean']:<10.2f} {row['std']:<10.2f} {row['min']:<10.2f} {row['max']:<10.2f} {row['CV%']:<8.2f} {target_str:<10} {status}\n"
            )

        f.write("\n" + "=" * 100 + "\n")
        f.write(" ANÁLISIS DE INFERENCIA ESTADÍSTICA (28 Días)\n")
        f.write("=" * 100 + "\n")
        f.write(f"1. Prueba T (vs {TARGETS[28.0]} MPa): p-value = {p_val:.4e}\n")
        f.write(
            f"   Interpretación: {'Éxito Estadístico' if p_val < 0.05 else 'No Concluyente'}\n\n"
        )

        f.write(f"2. Resistencia Característica (f'ck) del Proyecto:\n")
        f.write(f"   Calculada (Percentil 5): {fck_project:.2f} MPa\n")
        f.write(f"   Requerida (Ficha Técnica): {FCK_REQUIRED} MPa\n")
        f.write(
            f"   RESULTADO FINAL: {'APROBADO' if fck_project >= FCK_REQUIRED else 'REVISAR'}\n"
        )
        f.write("=" * 60 + "\n")

    print(f"Análisis completado. Reporte emitido en: {os.path.abspath(report_path)}")

    # --- GENERACIÓN DE GRÁFICOS ---
    # Gráfico 1: Boxplot
    plt.figure(figsize=(10, 6))
    sns.boxplot(x="Edad", y="MPa", data=df_master, palette="viridis")
    plt.title("Distribución de Resistencia SikaGrout 9400 (Control Pro)")
    plt.xlabel("Edad (Días)")
    plt.ylabel("Resistencia (MPa)")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.savefig("boxplot_resistencia_pro.png")

    # Gráfico 2: Densidad (KDE)
    plt.figure(figsize=(10, 6))
    for age in sorted(df_master["Edad"].unique()):
        subset = df_master[df_master["Edad"] == age]
        if len(subset) > 1:
            sns.kdeplot(subset["MPa"], label=f"{int(age)} días", fill=True)

    plt.title("Cinética de Resistencia: Densidad de Probabilidad")
    plt.xlabel("Resistencia (MPa)")
    plt.legend()
    plt.savefig("densidad_resistencia_pro.png")

    print("Gráficos generados y mostrados en pantalla.")
    plt.show()


generate_report()
