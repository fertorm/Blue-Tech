import sqlite3
import pandas as pd

conexion = sqlite3.connect("BlueTech_Grout.db")

print("--- DÍA 3: LIMPIEZA Y ORGANIZACIÓN ---")

# CONSULTA A: ¿Cuántos aerogeneradores únicos tenemos? (DISTINCT)
# Útil para saber exactamente cuántos frentes de trabajo están activos
query_unicos = "SELECT DISTINCT Estructura FROM Roturas"
res_unicos = pd.read_sql(query_unicos, conexion)
print(f"\n1. Lista única de Estructuras (Sin repetidos):\n{res_unicos}")

# CONSULTA B: Ordenar por Resistencia (ORDER BY)
# Queremos ver las roturas a 28 días desde la más fuerte a la más débil (DESC)
query_ranking = """
    SELECT Estructura, Resistencia_MPa 
    FROM Roturas 
    WHERE Edad_Dias = 28 
    ORDER BY Resistencia_MPa DESC
"""
res_ranking = pd.read_sql(query_ranking, conexion)
print(f"\n2. Ranking de Resistencia a 28 días (Mayor a Menor):\n{res_ranking.head()}")

# CONSULTA C: Orden Combinado (Cronológico y por Edad)
query_cronologico = """
    SELECT Fecha_Vaciado, Edad_Dias, Resistencia_MPa 
    FROM Roturas 
    ORDER BY Fecha_Vaciado ASC, Edad_Dias ASC
"""
res_cronologico = pd.read_sql(query_cronologico, conexion)
print(f"\n3. Historial Cronológico de Vaciados:\n{res_cronologico.head()}")

conexion.close()
