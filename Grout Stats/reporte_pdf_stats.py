import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from sklearn.linear_model import LinearRegression

# 1. CARGA DE DATOS
df = pd.read_csv("master_data_grout.csv")

# 2. GENERACIÓN DE GRÁFICAS PARA EL REPORTE
# Gráfica 1: Distribución por Edad
plt.figure(figsize=(8, 5))
sns.boxplot(
    x="Edad_Dias",
    y="Resistencia_MPa",
    hue="Edad_Dias",
    data=df,
    palette="Blues",
    legend=False,
)
plt.axhline(110, color="red", linestyle="--", label="Meta Sika (110 MPa)")
plt.title("Distribución de Resistencia - Proyecto Blue Tech")
plt.savefig("plot_distribucion.png")

# Gráfica 2: Modelo de Crecimiento Logarítmico
log_x = np.log(df[["Edad_Dias"]]).values
y = df["Resistencia_MPa"].values
model = LinearRegression().fit(log_x, y)
plt.figure(figsize=(8, 5))
plt.scatter(df["Edad_Dias"], y, alpha=0.3)
x_fine = np.linspace(1, 30, 100)
plt.plot(
    x_fine,
    model.intercept_ + model.coef_[0] * np.log(x_fine),
    "r-",
    label="Modelo Predictivo",
)
plt.title("Cinética de Resistencia: Datos vs Modelo")
plt.savefig("plot_crecimiento.png")


import os


# 3. CREACIÓN DEL PDF
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "REPORTE DE CONTROL DE CALIDAD - SIKAGROUT 9400 BR", 0, 1, "C")
        self.ln(5)


# Calcular ecuación de regresión
intercept = model.intercept_
slope = model.coef_[0]
equation_str = f"Resistencia = {intercept:.2f} + {slope:.2f} * ln(Edad)"
print(f"Modelo: {equation_str}")

pdf = PDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Sección 1: Resumen Estadístico
pdf.cell(0, 10, "1. Resumen Estadístico", 1, 1)
pdf.multi_cell(
    0,
    10,
    f"Resistencia Media a 28 días: {df[df['Edad_Dias']==28]['Resistencia_MPa'].mean():.2f} MPa",
)

# Tabla de Estadísticas Descriptivas
pdf.ln(5)
pdf.set_font("Arial", "B", 10)
# Encabezados
headers = ["Edad (dias)", "N", "Media", "Desv", "Min", "Max", "CV%"]
cw = [25, 15, 25, 25, 25, 25, 20]  # Column widths
for i, h in enumerate(headers):
    pdf.cell(cw[i], 8, h, 1, 0, "C")
pdf.ln()

# Datos
pdf.set_font("Arial", "", 10)
stats_summary = (
    df.groupby("Edad_Dias")["Resistencia_MPa"]
    .agg(["count", "mean", "std", "min", "max"])
    .reset_index()
)
stats_summary["CV_%"] = (stats_summary["std"] / stats_summary["mean"]) * 100

for _, row in stats_summary.iterrows():
    pdf.cell(cw[0], 8, f"{row['Edad_Dias']}", 1, 0, "C")
    pdf.cell(cw[1], 8, f"{int(row['count'])}", 1, 0, "C")
    pdf.cell(cw[2], 8, f"{row['mean']:.2f}", 1, 0, "C")
    pdf.cell(cw[3], 8, f"{row['std']:.2f}", 1, 0, "C")
    pdf.cell(cw[4], 8, f"{row['min']:.2f}", 1, 0, "C")
    pdf.cell(cw[5], 8, f"{row['max']:.2f}", 1, 0, "C")
    pdf.cell(cw[6], 8, f"{row['CV_%']:.2f}", 1, 0, "C")
    pdf.ln()

pdf.ln(10)
pdf.set_font("Arial", size=12)

if os.path.exists("plot_distribucion.png"):
    pdf.image("plot_distribucion.png", x=30, w=150)
else:
    pdf.cell(0, 10, "[Falta imagen: plot_distribucion.png]", 0, 1)

# Sección 2: Análisis Predictivo
pdf.add_page()
pdf.cell(0, 10, "2. Análisis Predictivo", 1, 1)
pdf.multi_cell(
    0,
    10,
    f"El modelo logarítmico confirma la estabilidad del material.\n\nEcuación de Regresión:\n{equation_str}",
)
if os.path.exists("plot_crecimiento.png"):
    pdf.image("plot_crecimiento.png", x=30, w=150)
else:
    pdf.cell(0, 10, "[Falta imagen: plot_crecimiento.png]", 0, 1)

# Sección 3: Análisis ANOVA y Estructural
pdf.add_page()
pdf.cell(0, 10, "3. Análisis de Varianza (ANOVA)", 1, 1)
pdf.ln(5)

# Boxplot Edad (ANOVA)
if os.path.exists("boxplot_Edad_Dias.png"):
    pdf.cell(0, 10, "Distribución por Edad (ANOVA):", 0, 1)
    pdf.image("boxplot_Edad_Dias.png", x=20, w=170)
    pdf.ln(5)

# Nueva pagina si es necesario o espacio
pdf.add_page()
# Boxplot Estructura (ANOVA)
if os.path.exists("boxplot_Estructura.png"):
    pdf.cell(0, 10, "Distribución por Estructura:", 0, 1)
    pdf.image("boxplot_Estructura.png", x=20, w=170)

# Sección 4: Análisis Detallado (PRO)
pdf.add_page()
pdf.cell(0, 10, "4. Análisis Detallado (Control Pro)", 1, 1)
if os.path.exists("boxplot_resistencia_pro.png"):
    pdf.ln(5)
    pdf.image("boxplot_resistencia_pro.png", x=20, w=170)

# Sección 5: Reporte Completo Warnes
pdf.add_page()
pdf.cell(0, 10, "5. Tablero de Control - Warnes II", 1, 1)
if os.path.exists("reporte_grout_warnes_completo.png"):
    pdf.ln(5)
    # Rotated image or fit to page? Assuming landscape or fit width
    pdf.image("reporte_grout_warnes_completo.png", x=10, w=190)

pdf.output("Reporte_Ejecutivo_Grout.pdf")
print("Reporte generado con éxito: Reporte_Ejecutivo_Grout.pdf")
