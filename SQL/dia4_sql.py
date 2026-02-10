import sqlite3
import pandas as pd

conexion = sqlite3.connect("BlueTech_Grout.db")

print("--- DÍA 4: FUNCIONES DE AGREGACIÓN ---")

# CONSULTA A: El Resumen Global
# Queremos saber el total de probetas, el promedio, la peor y la mejor
query_resumen = """
    SELECT 
        COUNT(*) AS Total_Probetas,
        AVG(Resistencia_MPa) AS Promedio_Global,
        MIN(Resistencia_MPa) AS Resistencia_Minima,
        MAX(Resistencia_MPa) AS Resistencia_Maxima
    FROM Roturas
"""
res_resumen = pd.read_sql(query_resumen, conexion)
print(f"\n1. Estadísticas Globales del Proyecto:\n{res_resumen}")

# CONSULTA B: Análisis de Seguridad a 28 Días
# ¿Cuál es la peor probeta que tenemos a los 28 días?
# Esto es vital para el cálculo de riesgo que vimos antes.
query_critica = """
    SELECT MIN(Resistencia_MPa) AS Peor_Caso_28d
    FROM Roturas 
    WHERE Edad_Dias = 28
"""
res_critica = pd.read_sql(query_critica, conexion)
print(f"\n2. Valor más bajo registrado a 28 días: {res_critica.iloc[0,0]} MPa")

conexion.close()
