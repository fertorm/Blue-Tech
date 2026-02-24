import sqlite3
import os
import pandas as pd


class BlueTechDatabase:
    def __init__(self, db_name="BlueTech_Proyectos.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def crear_tablas(self):
        """Crea la estructura para almacenar elementos estructurales"""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS elementos_verticales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proyecto TEXT,
                plano TEXT,
                etiqueta TEXT,
                x_local REAL,
                y_local REAL,
                fecha_analisis TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        self.conn.commit()

    def cargar_csv(self, csv_path, nombre_proyecto):
        """Migra los datos del CSV a la tabla SQL"""
        df = pd.read_csv(csv_path)
        # Añadimos columna de proyecto para escalabilidad
        df["proyecto"] = nombre_proyecto

        # Renombramos columnas para que coincidan con la tabla SQL
        df = df.rename(
            columns={
                "Página": "plano",
                "Etiqueta": "etiqueta",
                "X_Centro": "x_local",
                "Y_Centro": "y_local",
            }
        )

        # Eliminamos columnas que no están en la tabla SQL
        df = df.drop(columns=["BBox"], errors="ignore")

        # Cargamos usando pandas (muy eficiente)
        df.to_sql("elementos_verticales", self.conn, if_exists="append", index=False)
        print(f"✅ {len(df)} registros migrados a la base de datos.")


# Ejecución
db = BlueTechDatabase()
db.crear_tablas()
# Usaremos el reporte que generamos ayer para la casa de Gustavo y María
# El CSV está en el directorio raíz del proyecto (Blue Tech)
csv_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "mapeo_columnas_bluetech.csv"
)
db.cargar_csv(csv_path, "Casa_Gustavo_Maria_R2")
