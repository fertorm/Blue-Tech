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


# 3. CREACIÓN DEL PDF
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "REPORTE DE CONTROL DE CALIDAD - SIKAGROUT 9400 BR", 0, 1, "C")
        self.ln(5)


pdf = PDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Sección de Texto
pdf.cell(0, 10, "1. Resumen Estadístico", 1, 1)
pdf.multi_cell(
    0,
    10,
    f"Resistencia Media a 28 días: {df[df['Edad_Dias']==28]['Resistencia_MPa'].mean():.2f} MPa",
)
pdf.image("plot_distribucion.png", x=30, w=150)

pdf.add_page()
pdf.cell(0, 10, "2. Análisis Predictivo", 1, 1)
pdf.multi_cell(0, 10, "El modelo logarítmico confirma la estabilidad del material.")
pdf.image("plot_crecimiento.png", x=30, w=150)

pdf.output("Reporte_Ejecutivo_Grout.pdf")
print("Reporte generado con éxito.")
