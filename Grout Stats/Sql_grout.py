import sqlite3
import pandas as pd

# 1. CONEXIÓN (Si no existe, SQL lo crea automáticamente)
# Imagina que estás abriendo un nuevo cuaderno de bitácora
conexion = sqlite3.connect("BlueTech_Grout.db")

# 2. CARGAR TUS DATOS DE INGENIERÍA
df = pd.read_csv("master_data_grout.csv")

# 3. CREAR LA TABLA SQL
# Aquí pasamos los datos del "papel" (CSV) al "sistema" (SQL)
df.to_sql("Roturas", conexion, if_exists="replace", index=False)

# 4. TU PRIMERA CONSULTA SQL (Día 1)
query = "SELECT Estructura, Resistencia_MPa FROM Roturas WHERE Edad_Dias = 28"
resultados = pd.read_sql(query, conexion)

print("--- RESULTADOS EXTRAÍDOS CON SQL ---")
print(resultados.head())

conexion.close()
