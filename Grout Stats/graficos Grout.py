import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import textwrap

# 1. Carga de Datos Reales
# Leemos el CSV con los datos maestros
try:
    df = pd.read_csv(
        r"c:\Users\Usuario\Documents\Blue Tech\Grout Stats\master_data_grout.csv"
    )
except FileNotFoundError:
    print(
        "Error: No se encontró el archivo 'master_data_grout.csv'. Asegúrate de que la ruta sea correcta."
    )
    exit()

# Aseguramos que la columna de edad sea numérica y filtramos datos vacíos
df["Edad_Dias"] = pd.to_numeric(df["Edad_Dias"], errors="coerce")
df["Resistencia_MPa"] = pd.to_numeric(df["Resistencia_MPa"], errors="coerce")
df = df.dropna(subset=["Edad_Dias", "Resistencia_MPa"])

# Filtramos solo las edades de interés: 1, 3, 7, 28 días
edades_interes = [1, 3, 7, 28]
df_filtrado = df[df["Edad_Dias"].isin(edades_interes)].copy()

# Ordenamos por edad para que los gráficos salgan en orden
df_filtrado = df_filtrado.sort_values(by="Edad_Dias")

# 2. Configuración de estilo profesional
sns.set_theme(style="whitegrid")
plt.figure(figsize=(18, 12))  # Aumentamos el tamaño para acomodar mejor los gráficos

# --- GRÁFICA A: EVOLUCIÓN TEMPORAL (CURVA DE CRECIMIENTO PROMEDIO) ---
# Calculamos el promedio de resistencia por día
resistencia_promedio = df.groupby("Edad_Dias")["Resistencia_MPa"].mean().reset_index()
# Filtramos también el promedio para asegurar que solo graficamos los días de interés en la línea principal
resistencia_promedio = resistencia_promedio[
    resistencia_promedio["Edad_Dias"].isin(edades_interes)
]

plt.subplot(2, 2, 1)
sns.lineplot(
    data=resistencia_promedio,
    x="Edad_Dias",
    y="Resistencia_MPa",
    marker="o",
    color="darkblue",
    linewidth=2,
    label="Promedio Real",
)

# Línea de referencia de diseño (ejemplo 100 MPa, ajustar según necesidad real o eliminar si no aplica a todos)
plt.axhline(100, color="red", linestyle="--", label="Ref. Diseño (100 MPa)")

# Puntos individuales dispersos para ver la variabilidad real
sns.scatterplot(
    data=df_filtrado,
    x="Edad_Dias",
    y="Resistencia_MPa",
    color="skyblue",
    alpha=0.6,
    label="Muestras Individuales",
)

plt.title("Curva de Desarrollo de Resistencia (Grout)")
plt.xlabel("Edad (Días)")
plt.ylabel("Resistencia (MPa)")
plt.xticks(edades_interes)  # Asegurar que el eje X muestre solo estos días
plt.legend()


# --- GRÁFICA B: BOXPLOT COMPARATIVO POR EDAD ---
plt.subplot(2, 2, 2)
sns.boxplot(x="Edad_Dias", y="Resistencia_MPa", data=df_filtrado, palette="Blues")
sns.swarmplot(
    x="Edad_Dias", y="Resistencia_MPa", data=df_filtrado, color=".25", alpha=0.5, size=4
)
plt.title("Distribución de Resistencia por Edad")
plt.xlabel("Edad (Días)")
plt.ylabel("Resistencia (MPa)")


# --- GRÁFICA C: HISTOGRAMAS POR CADA EDAD ---
# Usamos los subplots restantes (3 y 4) para dividir las 4 edades en 2 grupos o hacemos una visualización compacta.
# Para mejor detalle, usaremos una figura aparte o una estructura diferente.
# Aquí optaremos por superponer histogramas (kde) o hacer pequeños múltiplos si el espacio lo permite.
# Dado el layout 2x2, usaremos los dos de abajo para detallar.

# Gráfica C1: Histogramas Edad Temprana (1 y 3 días)
plt.subplot(2, 2, 3)
sns.histplot(
    data=df_filtrado[df_filtrado["Edad_Dias"].isin([1, 3])],
    x="Resistencia_MPa",
    hue="Edad_Dias",
    kde=True,
    palette="viridis",
    element="step",
)
plt.title("Histogramas: Edades Tempranas (1 y 3 días)")
plt.xlabel("Resistencia (MPa)")


# Gráfica C2: Histogramas Edad Madura (7 y 28 días)
plt.subplot(2, 2, 4)
sns.histplot(
    data=df_filtrado[df_filtrado["Edad_Dias"].isin([7, 28])],
    x="Resistencia_MPa",
    hue="Edad_Dias",
    kde=True,
    palette="magma",
    element="step",
)
plt.title("Histogramas: Edades Maduras (7 y 28 días)")
plt.xlabel("Resistencia (MPa)")

plt.tight_layout()
output_path = r"c:\Users\Usuario\Documents\Blue Tech\Grout Stats\reporte_grout_warnes_completo.png"
plt.savefig(output_path)
print(f"Gráfico generado exitosamente en: {output_path}")

# Opcional: Mostrar estadísticas básicas en consola
print("\n--- Estadísticas Descriptivas por Edad ---")
print(df_filtrado.groupby("Edad_Dias")["Resistencia_MPa"].describe())
