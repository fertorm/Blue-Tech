import pandas as pd
import os


class DatabaseManager:
    def __init__(
        self, filename="Base_Datos_BlueTech.xlsx", csv_filename="precios_escolares.csv"
    ):
        self.filename = filename
        self.csv_filename = csv_filename

    def save_data(self, data_list):
        """
        Guarda una lista de diccionarios en el Excel maestro y en un CSV.
        Schema esperado: {'Fuente', 'Material', 'Precio_BS', 'Fecha_Consulta'}
        """
        try:
            df_nuevos = pd.DataFrame(data_list)

            # Asegurar orden de columnas
            cols_deseadas = ["Fuente", "Material", "Precio_BS", "Fecha_Consulta"]
            # Rellenar si falta alguna
            for col in cols_deseadas:
                if col not in df_nuevos.columns:
                    df_nuevos[col] = "N/A"

            df_nuevos = df_nuevos[cols_deseadas]

            if os.path.exists(self.filename):
                # Leemos todo el histórico del Excel para añadir lo nuevo
                df_existente = pd.read_excel(self.filename)
                df_final = pd.concat([df_existente, df_nuevos], ignore_index=True)
            else:
                df_final = df_nuevos

            # Verificar tipos para evitar errores en streamlit
            df_final["Precio_BS"] = pd.to_numeric(
                df_final["Precio_BS"], errors="coerce"
            ).fillna(0)

            # Guardar Excel
            df_final.to_excel(self.filename, index=False)

            # Guardar CSV (Separador decimal punto)
            df_final.to_csv(self.csv_filename, index=False, decimal=".")

            return (
                True,
                f"Guardados {len(df_nuevos)} registros en {self.filename} y {self.csv_filename}",
            )
        except Exception as e:
            return False, str(e)

    @staticmethod
    def clean_price(price_str, decimal_separator="."):
        """
        Limpia el precio basándose en el separador decimal esperado.
        - Si decimal_separator es ',': Asume formato Europeo/Sudamericano (1.000,00 o 18,50).
          Elimina puntos (miles) y reemplaza coma por punto.
        - Si decimal_separator es '.': Asume formato US (1,000.00 o 38.50).
          Elimina comas (miles) y mantiene el punto.
        """
        if isinstance(price_str, (int, float)):
            return float(price_str)

        # Eliminar símbolo de moneda y espacios
        text = str(price_str).replace("Bs.", "").replace("Bs", "").strip()

        if decimal_separator == ",":
            # Formato: 1.250,50 -> 1250.50
            # Formato: 18,50 -> 18.50
            text = text.replace(".", "")  # Eliminar separador de miles si existe
            text = text.replace(",", ".")  # Coma a punto
        else:
            # Formato: 1,250.50 -> 1250.50
            # Formato: 38.50 -> 38.50
            text = text.replace(",", "")  # Eliminar separador de miles si existe
            # El punto ya es el separador decimal correcto para Python

        try:
            return float(text)
        except:
            return 0.0
