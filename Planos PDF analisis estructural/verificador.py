import pandas as pd
import numpy as np


class BlueTechCalibrator:
    def __init__(self, df_mapeo):
        self.df = df_mapeo
        self.anchors = {}  # {pagina: (x, y)}

    def definir_anclaje(self, pagina, x, y):
        """Establece el origen (0,0) para una página específica"""
        self.anchors[pagina] = np.array([x, y])
        print(f"📍 Origen calibrado para Página {pagina}: ({x}, {y})")

    def normalizar(self):
        """Transforma todas las coordenadas globales a locales"""
        df_norm = self.df.copy()
        for pag, anchor in self.anchors.items():
            mask = df_norm["Página"] == pag
            df_norm.loc[mask, "X_Local"] = df_norm.loc[mask, "X_Centro"] - anchor[0]
            df_norm.loc[mask, "Y_Local"] = df_norm.loc[mask, "Y_Centro"] - anchor[1]
        return df_norm


class BlueTechContinuityExpert:
    def __init__(
        self, tolerance=15.0
    ):  # Tolerancia reducida gracias a la normalización
        self.tolerance = tolerance

    def verificar(self, df_local):
        paginas = sorted(df_local["Página"].unique())
        reporte = []

        for i in range(len(paginas) - 1):
            p_inf, p_sup = paginas[i], paginas[i + 1]
            df_inf = df_local[df_local["Página"] == p_inf]
            df_sup = df_local[df_local["Página"] == p_sup]

            for _, col_b in df_inf.iterrows():
                # Cálculo de distancia en espacio normalizado
                distancias = np.sqrt(
                    (df_sup["X_Local"] - col_b["X_Local"]) ** 2
                    + (df_sup["Y_Local"] - col_b["Y_Local"]) ** 2
                )

                match = df_sup[distancias <= self.tolerance]

                if not match.empty:
                    idx_match = distancias.idxmin()
                    reporte.append(
                        {
                            "Niveles": f"{p_inf} -> {p_sup}",
                            "Elemento": col_b["Etiqueta"],
                            "Estado": "✅ CONTINUO",
                            "Error_Relativo": round(distancias.min(), 2),
                        }
                    )
                else:
                    reporte.append(
                        {
                            "Niveles": f"{p_inf} -> {p_sup}",
                            "Elemento": col_b["Etiqueta"],
                            "Estado": "❌ DISCONTINUO",
                            "Error_Relativo": "-",
                        }
                    )
        return pd.DataFrame(reporte)


# --- FLUJO DE TRABAJO EN LA LENOVO ---
if __name__ == "__main__":
    # 1. Cargar datos del mapeo anterior
    df_raw = pd.read_csv("mapeo_columnas_bluetech.csv")

    # 2. Fase de Calibración
    # NOTA: Debes buscar un punto común en los planos (ej. Esquina Eje A-1)
    # Ejemplo con datos hipotéticos basados en tu PDF:
    calibrador = BlueTechCalibrator(df_raw)

    print("\n--- FASE DE CALIBRACIÓN DE EJES ---")
    # Para la página 17 (S101), supongamos que el origen es (1980, 1267)
    calibrador.definir_anclaje(17, 1980.36, 1267.56)
    # Para la página 18 (S201), ajustamos el desfase detectado
    calibrador.definir_anclaje(18, 1168.02, 388.62)

    # 3. Normalizar y Analizar
    df_normalizado = calibrador.normalizar()
    experto = BlueTechContinuityExpert(tolerance=20.0)
    resultado_final = experto.verificar(df_normalizado)

    print("\n" + "=" * 50)
    print("ANALISIS DE CONTINUIDAD NORMALIZADO")
    print("=" * 50)

    # Generar string con formato de tabla
    reporte_str = resultado_final.to_string(index=False)
    print(reporte_str)

    # Guardar en archivo de texto
    with open("reporte_continuidad.txt", "w", encoding="utf-8") as f:
        f.write("=" * 50 + "\n")
        f.write("ANALISIS DE CONTINUIDAD NORMALIZADO\n")
        f.write("=" * 50 + "\n")
        f.write(reporte_str)

    print("\n💾 Resultado guardado en 'reporte_continuidad.txt'")
