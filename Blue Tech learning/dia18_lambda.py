import pandas as pd


class BlueTechDataProcessor:
    def __init__(self, df):
        self.df = df

    def normalizar_coordenadas(self, anchor_x, anchor_y):
        """
        Aquí usamos LAMBDA para aplicar una transformación matemática
        a toda una columna de forma científica y rápida.
        """
        # Restamos el anclaje a cada X y Y usando lambdas
        self.df["X_Norm"] = self.df["X_Centro"].apply(lambda x: x - anchor_x)
        self.df["Y_Norm"] = self.df["Y_Centro"].apply(lambda y: y - anchor_y)

        # Limpieza de etiquetas: Quitamos espacios y pasamos a mayúsculas
        self.df["Etiqueta"] = self.df["Etiqueta"].apply(
            lambda txt: str(txt).strip().upper()
        )


# Este será el corazón de nuestro pipeline de datos
