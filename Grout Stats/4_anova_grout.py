import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# --- Configuración ---
# --- Configuración ---
DATA_FILE = r"c:\Users\Usuario\Documents\Blue Tech\master_data_grout.csv"
OUTPUT_DIR = os.path.dirname(DATA_FILE)


def load_and_prepare_data(filepath):
    """Carga y limpia los datos."""
    try:
        df = pd.read_csv(filepath)
        print(f"Datos cargados exitosamente: {len(df)} registros.")
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        return None

    # Asegurar tipos de datos correctos
    df["Resistencia_MPa"] = pd.to_numeric(df["Resistencia_MPa"], errors="coerce")
    df.dropna(subset=["Resistencia_MPa"], inplace=True)

    # Convertir a categórico para análisis
    df["Edad_Dias"] = df["Edad_Dias"].astype(str)  # Tratar dias como categorias
    df["Estructura"] = df["Estructura"].astype(str)

    return df


def perform_anova(df, factor, response="Resistencia_MPa"):
    """Realiza ANOVA de un factor."""
    print(f"\n{'='*20} Análisis ANOVA para Factor: {factor} {'='*20}")

    # 1. Ajustar el modelo
    model = ols(f"{response} ~ C({factor})", data=df).fit()

    # 2. Tabla ANOVA
    anova_table = sm.stats.anova_lm(model, typ=2)
    print("\nTabla ANOVA:")
    print(anova_table)

    # 3. Comprobación de supuestos
    # Normalidad de los residuos
    shapiro_test = stats.shapiro(model.resid)
    print(f"\nTest de Normalidad (Shapiro-Wilk) p-value: {shapiro_test.pvalue:.4f}")
    if shapiro_test.pvalue < 0.05:
        print(
            "  -> ¡Advertencia! Los residuos no parecen seguir una distribución normal (p < 0.05)."
        )
    else:
        print("  -> Los residuos parecen normales.")

    # Homogeneidad de varianzas (Levene)
    groups = [group[response].values for name, group in df.groupby(factor)]
    levene_test = stats.levene(*groups)
    print(
        f"Test de Homogeneidad de Varianzas (Levene) p-value: {levene_test.pvalue:.4f}"
    )
    if levene_test.pvalue < 0.05:
        print("  -> ¡Advertencia! Las varianzas no son homogéneas (p < 0.05).")
    else:
        print("  -> Las varianzas son homogéneas.")

    # 4. Post-hoc (Tukey) si hay significancia
    if anova_table["PR(>F)"][0] < 0.05:
        print(
            f"\nEl factor '{factor}' es significativo. Realizando prueba Post-hoc (Tukey's HSD)..."
        )
        tukey = pairwise_tukeyhsd(endog=df[response], groups=df[factor], alpha=0.05)
        print(tukey)

        # Guardar resultados de Tukey en CSV si se desea
        # tukey_df = pd.DataFrame(data=tukey._results_table.data[1:], columns=tukey._results_table.data[0])
        # tukey_df.to_csv(os.path.join(OUTPUT_DIR, f'tukey_{factor}.csv'), index=False)
    else:
        print(f"\nEl factor '{factor}' NO es estadísticamente significativo.")

    return model


def visualize_results(df, factor, response="Resistencia_MPa"):
    """Genera boxplots para visualizar los grupos."""
    plt.figure(figsize=(10, 6))
    sns.boxplot(x=factor, y=response, data=df, palette="Set2")

    # Añadir puntos individuales para ver la distribución real
    sns.stripplot(x=factor, y=response, data=df, color="black", alpha=0.3, jitter=True)

    plt.title(f"Distribución de {response} por {factor}")
    plt.grid(True, linestyle="--", alpha=0.7)

    filename = f"boxplot_{factor}.png"
    save_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(save_path)
    print(f"Gráfico guardado en: {save_path}")
    plt.close()


def main():
    df = load_and_prepare_data(DATA_FILE)
    if df is not None:
        # Analisis por Edad (Dias)
        perform_anova(df, "Edad_Dias")
        visualize_results(df, "Edad_Dias")

        # Analisis por Estructura
        perform_anova(df, "Estructura")
        visualize_results(df, "Estructura")


if __name__ == "__main__":
    main()
