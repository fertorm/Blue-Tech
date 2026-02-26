#!/usr/bin/env python3
"""
grout_pipeline.py — Pipeline Unificado de Control de Calidad
=============================================================
Blue Tech | SikaGrout 9400 BR

Consolida en un único flujo de trabajo modular lo que antes estaba
distribuido en 7 scripts independientes:

  1_Grout_stats.py        → Carga, consolidación y estadística básica
  2_Grout_Analysis_Pro.py → Análisis estadístico avanzado + inferencia
  3_Grout_Master_Predictor→ Modelo predictivo logarítmico
  4_anova_grout.py        → ANOVA + Shapiro-Wilk + Levene + Tukey HSD
  5_Sql_grout.py          → Persistencia en SQLite
  6_reporte_pdf_stats.py  → Reporte PDF ejecutivo
  7_count.data.py         → Conteo de registros

Uso:
  python grout_pipeline.py                              # GUI para elegir archivos
  python grout_pipeline.py -f ensayo_01.xlsx            # Archivo directo
  python grout_pipeline.py -f e1.xlsx e2.xlsx           # Múltiples archivos
  python grout_pipeline.py -f datos.xlsx --no-pdf       # Sin PDF
  python grout_pipeline.py -f datos.xlsx --predict 92 7 # Predicción 28d
"""

from __future__ import annotations

import argparse
import logging
import os
import sqlite3
import sys
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # Sin ventanas de GUI para matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
import seaborn as sns
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN Y CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR   = Path(__file__).parent          # .../Grout Stats/
PROJECT_ROOT = SCRIPT_DIR.parent              # .../Blue Tech/

# Columnas a extraer por índice (base-0) de los archivos fuente
COL_INDICES = [1, 2, 5, 6, 7, 13]
COL_NAMES   = [
    "ID_Probeta", "Estructura",
    "Fecha_Vaciado", "Fecha_Rotura",
    "Edad_Dias", "Resistencia_MPa",
]

# Requisitos mínimos SikaGrout 9400 BR (Ficha Técnica)
TARGETS: dict[float, float] = {1.0: 45.0, 7.0: 90.0, 28.0: 110.0}
FCK_REQUIRED = 108.0  # MPa — resistencia característica certificada

# ─────────────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────────────

def _setup_logging() -> logging.Logger:
    # Forzar UTF-8 en la consola Windows para evitar errores de codificación
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    log_path = PROJECT_ROOT / "grout_pipeline.log"
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    try:
        handlers.append(logging.FileHandler(log_path, encoding="utf-8"))
    except OSError:
        pass  # Si no se puede crear el log file, solo usar stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        handlers=handlers,
    )
    return logging.getLogger(__name__)

log = _setup_logging()


# ─────────────────────────────────────────────────────────────────────────────
# PASO 1 — CARGA Y CONSOLIDACIÓN DE ARCHIVOS
# ─────────────────────────────────────────────────────────────────────────────

def load_files(files: list[str | Path]) -> pd.DataFrame:
    """
    Carga y consolida múltiples archivos Excel/CSV.

    Espera datos a partir de la fila 6 (skiprows=5) con las columnas
    definidas en COL_INDICES. Soporta múltiples hojas por archivo Excel.

    Returns:
        DataFrame unificado con columnas estándar + Origen_Archivo / Origen_Hoja.

    Raises:
        ValueError: Si ningún archivo produce datos válidos.
    """
    all_data: list[pd.DataFrame] = []

    for raw_file in files:
        file = Path(raw_file)
        try:
            if file.suffix.lower() == ".csv":
                raw_dfs: dict[str, pd.DataFrame] = {
                    file.name: pd.read_csv(file, skiprows=5)
                }
            else:
                raw_dfs = pd.read_excel(file, skiprows=5, sheet_name=None)

            for sheet_name, df in raw_dfs.items():
                if df.shape[1] < 14:
                    log.warning(
                        "Hoja '%s' en %s: solo %d columnas (mínimo 14). Saltando.",
                        sheet_name, file.name, df.shape[1],
                    )
                    continue

                df_clean = df.iloc[:, COL_INDICES].copy()
                df_clean.columns = COL_NAMES
                df_clean = df_clean.dropna(subset=["ID_Probeta", "Resistencia_MPa"])
                df_clean["Origen_Archivo"] = file.name
                df_clean["Origen_Hoja"] = sheet_name
                all_data.append(df_clean)
                log.info("  %s / %s → %d probetas.", file.name, sheet_name, len(df_clean))

        except Exception as exc:
            log.error("Error procesando %s: %s", file.name, exc)

    if not all_data:
        raise ValueError(
            "No se procesaron datos válidos. "
            "Verifique que los archivos tengan el formato correcto (14+ columnas, skiprows=5)."
        )

    master = pd.concat(all_data, ignore_index=True)
    master["Edad_Dias"]       = pd.to_numeric(master["Edad_Dias"], errors="coerce")
    master["Resistencia_MPa"] = pd.to_numeric(master["Resistencia_MPa"], errors="coerce")
    master = master.dropna(subset=["Edad_Dias", "Resistencia_MPa"])

    log.info(
        "Consolidación completa: %d probetas válidas de %d archivo(s).",
        len(master), len(files),
    )
    return master


# ─────────────────────────────────────────────────────────────────────────────
# PASO 1b — VALIDACIÓN DE FECHAS
# ─────────────────────────────────────────────────────────────────────────────

def validate_dates(df: pd.DataFrame) -> int:
    """
    Detecta y alerta sobre filas con fechas futuras en Fecha_Vaciado o Fecha_Rotura.

    Una fecha futura indica un error de ingreso de datos (la probeta no puede
    haberse vaciado o roto en el futuro).

    Args:
        df: DataFrame con columnas Fecha_Vaciado y/o Fecha_Rotura.

    Returns:
        Número de filas con al menos una fecha futura detectada.
    """
    today = pd.Timestamp.today().normalize()
    warnings_count = 0

    for col in ("Fecha_Vaciado", "Fecha_Rotura"):
        if col not in df.columns:
            continue
        try:
            parsed = pd.to_datetime(df[col], errors="coerce")
            future_mask = parsed > today
            n_future = int(future_mask.sum())
            if n_future > 0:
                warnings_count += n_future
                log.warning(
                    "VALIDACION DE FECHAS: %d fila(s) con %s en el futuro. "
                    "Verifique los datos de entrada.",
                    n_future, col,
                )
                for idx in df[future_mask].index:
                    log.warning(
                        "  → Fila %d | ID_Probeta=%s | %s=%s",
                        idx,
                        df.loc[idx, "ID_Probeta"] if "ID_Probeta" in df.columns else "?",
                        col,
                        df.loc[idx, col],
                    )
        except Exception as exc:
            log.warning("No se pudo validar columna %s: %s", col, exc)

    return warnings_count


# ─────────────────────────────────────────────────────────────────────────────
# PASO 2 — ESTADÍSTICA DESCRIPTIVA
# ─────────────────────────────────────────────────────────────────────────────

def compute_descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Estadística descriptiva agrupada por edad (días)."""
    stats_df = (
        df.groupby("Edad_Dias")["Resistencia_MPa"]
        .agg(["count", "mean", "std", "min", "max"])
        .reset_index()
    )
    stats_df["CV_%"] = (stats_df["std"] / stats_df["mean"]) * 100
    stats_df.rename(
        columns={"count": "N", "mean": "Media", "std": "Desv", "min": "Min", "max": "Max"},
        inplace=True,
    )
    return stats_df


# ─────────────────────────────────────────────────────────────────────────────
# PASO 3 — INFERENCIA ESTADÍSTICA
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class InferenceResults:
    """Resultados de la inferencia estadística sobre el dataset."""
    n_total:       int
    stats_summary: pd.DataFrame
    t_stat_28d:    float = 0.0
    p_value_28d:   float = 1.0
    fck_project:   float = 0.0
    fck_required:  float = FCK_REQUIRED
    target_28d:    float = TARGETS[28.0]

    @property
    def passes_ttest(self) -> bool:
        return self.p_value_28d < 0.05

    @property
    def passes_fck(self) -> bool:
        return self.fck_project >= self.fck_required


def compute_inference(df: pd.DataFrame) -> InferenceResults:
    """
    Calcula inferencia estadística:
      - T-test de una muestra a 28 días vs. target del fabricante.
      - Resistencia característica f'ck (percentil 5, método ACI 318).
    """
    stats_summary = compute_descriptive_stats(df)
    data_28 = df[df["Edad_Dias"] == 28.0]["Resistencia_MPa"]

    if len(data_28) >= 2:
        t_stat, p_val = stats.ttest_1samp(data_28, TARGETS[28.0])
        fck = data_28.mean() - 1.645 * data_28.std(ddof=1)
    else:
        log.warning("Datos insuficientes a 28 días (n=%d). Inferencia no calculada.", len(data_28))
        t_stat, p_val, fck = 0.0, 1.0, 0.0

    return InferenceResults(
        n_total=len(df),
        stats_summary=stats_summary,
        t_stat_28d=float(t_stat),
        p_value_28d=float(p_val),
        fck_project=float(fck),
    )


# ─────────────────────────────────────────────────────────────────────────────
# PASO 4 — ANÁLISIS ANOVA
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AnovaResults:
    """Resultados del análisis ANOVA + supuestos + post-hoc."""
    factor:        str
    anova_table:   pd.DataFrame
    shapiro_stat:  float
    shapiro_p:     float
    levene_stat:   float
    levene_p:      float
    tukey_results: Optional[object] = None
    is_significant: bool = False

    @property
    def residuals_normal(self) -> bool:
        """True si los residuos pasan Shapiro-Wilk (p ≥ 0.05)."""
        return self.shapiro_p >= 0.05

    @property
    def variances_homogeneous(self) -> bool:
        """True si las varianzas pasan Levene (p ≥ 0.05)."""
        return self.levene_p >= 0.05


def perform_anova(df: pd.DataFrame, factor: str) -> AnovaResults:
    """
    ANOVA de un factor con validación de supuestos y post-hoc Tukey HSD.

    Args:
        df:     DataFrame con columnas Resistencia_MPa y la columna `factor`.
        factor: Nombre de la columna categórica ("Edad_Dias" o "Estructura").

    Returns:
        AnovaResults con tabla ANOVA, estadísticas de supuestos y Tukey.
    """
    df_anova = df.copy()
    df_anova[factor] = df_anova[factor].astype(str)

    model = ols(f"Resistencia_MPa ~ C({factor})", data=df_anova).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    is_significant = bool(anova_table["PR(>F)"].iloc[0] < 0.05)

    # Supuesto de normalidad
    shapiro_stat, shapiro_p = stats.shapiro(model.resid)

    # Supuesto de homogeneidad de varianzas
    groups = [g["Resistencia_MPa"].values for _, g in df_anova.groupby(factor)]
    levene_stat, levene_p = stats.levene(*groups)

    # Post-hoc Tukey HSD (solo si ANOVA es significativo)
    tukey = None
    if is_significant:
        tukey = pairwise_tukeyhsd(
            endog=df_anova["Resistencia_MPa"],
            groups=df_anova[factor],
            alpha=0.05,
        )
        log.info("ANOVA [%s]: SIGNIFICATIVO → Post-hoc Tukey aplicado.", factor)
    else:
        p_val = anova_table["PR(>F)"].iloc[0]
        log.info("ANOVA [%s]: No significativo (p=%.4f).", factor, p_val)

    return AnovaResults(
        factor=factor,
        anova_table=anova_table,
        shapiro_stat=float(shapiro_stat),
        shapiro_p=float(shapiro_p),
        levene_stat=float(levene_stat),
        levene_p=float(levene_p),
        tukey_results=tukey,
        is_significant=is_significant,
    )


# ─────────────────────────────────────────────────────────────────────────────
# PASO 5 — MODELO PREDICTIVO LOGARÍTMICO
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PredictiveModel:
    """
    Regresión logarítmica: MPa = a + b·ln(Edad_Dias)
    Permite proyectar la resistencia a 28 días desde una medición temprana.
    """
    model:      LinearRegression = field(default_factory=LinearRegression)
    r2_score:   float = 0.0
    intercept:  float = 0.0
    slope:      float = 0.0
    n_samples:  int   = 0
    is_trained: bool  = False

    def train(self, df: pd.DataFrame) -> None:
        """Entrena el modelo sobre el DataFrame consolidado."""
        X = np.log(df[["Edad_Dias"]].values)
        y = df["Resistencia_MPa"].values

        self.model.fit(X, y)
        self.intercept = float(self.model.intercept_)
        self.slope     = float(self.model.coef_[0])
        self.r2_score  = float(self.model.score(X, y))
        self.n_samples = len(df)
        self.is_trained = True

        log.info(
            "Modelo logaritmico entrenado: R2=%.4f | %s",
            self.r2_score, self.equation_str,
        )

    def predict_at_28d(self, mpa_at_age: float, age_days: float) -> float:
        """
        Proyecta la resistencia a 28 días usando la pendiente del modelo.

        Formula: MPa_28 = MPa_actual + b·(ln(28) - ln(edad_actual))
        """
        if not self.is_trained:
            raise RuntimeError("Modelo no entrenado. Llame a train() primero.")
        return mpa_at_age + self.slope * (np.log(28) - np.log(age_days))

    @property
    def equation_str(self) -> str:
        return f"Resistencia = {self.intercept:.2f} + {self.slope:.2f} x ln(Edad)"


# ─────────────────────────────────────────────────────────────────────────────
# PASO 6 — PERSISTENCIA EN SQLITE
# ─────────────────────────────────────────────────────────────────────────────

def persist_to_database(df: pd.DataFrame, db_path: Path) -> int:
    """
    Guarda el DataFrame en la tabla 'Roturas' de la base de datos SQLite.
    Reemplaza los datos anteriores (if_exists='replace').

    Returns:
        Número de registros insertados.
    """
    with sqlite3.connect(db_path) as conn:
        df.to_sql("Roturas", conn, if_exists="replace", index=False)
        count = pd.read_sql("SELECT COUNT(*) AS total FROM Roturas", conn).iloc[0, 0]

    log.info("BD actualizada: %s → %d registros en tabla 'Roturas'.", db_path.name, count)
    return int(count)


# ─────────────────────────────────────────────────────────────────────────────
# PASO 7 — VISUALIZACIONES
# ─────────────────────────────────────────────────────────────────────────────

def generate_plots(
    df: pd.DataFrame,
    pred_model: PredictiveModel,
    anova_edad: AnovaResults,
    anova_estructura: AnovaResults,
    output_dir: Path,
) -> dict[str, Path]:
    """
    Genera todos los gráficos del pipeline y los guarda como PNG.

    Returns:
        Diccionario {nombre: Path} con las rutas de los archivos generados.
    """
    sns.set_theme(style="whitegrid")
    # Capture matplotlib/seaborn UserWarnings and route them to the log file
    # instead of letting them appear on stderr unfiltered.
    warnings.filterwarnings("error", category=UserWarning, module="matplotlib")
    paths: dict[str, Path] = {}
    ages_sorted = sorted(df["Edad_Dias"].unique())

    # ── Gráfico 1: Boxplot distribución por edad ──────────────────────────
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(
            x="Edad_Dias", y="Resistencia_MPa", hue="Edad_Dias",
            data=df, palette="Blues", legend=False, ax=ax, order=ages_sorted,
        )
        sns.stripplot(
            x="Edad_Dias", y="Resistencia_MPa", data=df,
            color="#333333", alpha=0.25, jitter=True, ax=ax, order=ages_sorted,
        )
        ax.axhline(
            TARGETS[28.0], color="red", linestyle="--", linewidth=1.5,
            label=f"Meta 28d ({TARGETS[28.0]} MPa)",
        )
        for age, target in TARGETS.items():
            if age != 28.0:
                ax.axhline(target, color="orange", linestyle=":", linewidth=1, alpha=0.7)
        ax.set_title("Distribucion de Resistencia por Edad - SikaGrout 9400 BR", fontsize=13, fontweight="bold")
        ax.set_xlabel("Edad (dias)"); ax.set_ylabel("Resistencia (MPa)")
        ax.legend()
        p = output_dir / "plot_distribucion.png"
        fig.savefig(p, dpi=150, bbox_inches="tight"); plt.close(fig)
        paths["distribucion"] = p
    except UserWarning as w:
        log.warning("Matplotlib warning (plot_distribucion): %s", w)
        plt.close("all")

    # ── Gráfico 2: KDE por edad ───────────────────────────────────────────
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        for age in ages_sorted:
            subset = df[df["Edad_Dias"] == age]
            if len(subset) > 1:
                sns.kdeplot(subset["Resistencia_MPa"], label=f"{int(age)} dias", fill=True, alpha=0.4, ax=ax)
        ax.set_title("Densidad de Probabilidad de Resistencia por Edad", fontsize=13, fontweight="bold")
        ax.set_xlabel("Resistencia (MPa)"); ax.legend()
        p = output_dir / "plot_kde.png"
        fig.savefig(p, dpi=150, bbox_inches="tight"); plt.close(fig)
        paths["kde"] = p
    except UserWarning as w:
        log.warning("Matplotlib warning (plot_kde): %s", w)
        plt.close("all")

    # ── Gráfico 3: Modelo de crecimiento logarítmico ──────────────────────
    if pred_model.is_trained:
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.scatter(df["Edad_Dias"], df["Resistencia_MPa"], alpha=0.3, label="Mediciones")
            x_fine = np.linspace(0.5, 35, 200)
            y_fit  = pred_model.intercept + pred_model.slope * np.log(x_fine)
            ax.plot(x_fine, y_fit, "r-", linewidth=2, label=f"Modelo: {pred_model.equation_str}")
            ax.axhline(TARGETS[28.0], color="green", linestyle="--", label=f"Meta 28d ({TARGETS[28.0]} MPa)")
            ax.set_title("Cinetica de Resistencia: Datos vs Modelo Logaritmico", fontsize=13, fontweight="bold")
            ax.set_xlabel("Edad (dias)"); ax.set_ylabel("Resistencia (MPa)")
            ax.legend(); ax.grid(True, alpha=0.3)
            p = output_dir / "plot_crecimiento.png"
            fig.savefig(p, dpi=150, bbox_inches="tight"); plt.close(fig)
            paths["crecimiento"] = p
        except UserWarning as w:
            log.warning("Matplotlib warning (plot_crecimiento): %s", w)
            plt.close("all")

    # ── Gráficos 4 & 5: Boxplots ANOVA ───────────────────────────────────
    anova_configs = [
        (anova_edad,       "boxplot_Edad_Dias.png"),
        (anova_estructura, "boxplot_Estructura.png"),
    ]
    for result, fname in anova_configs:
        try:
            df_plot = df.copy()
            df_plot[result.factor] = df_plot[result.factor].astype(str)
            order = sorted(df_plot[result.factor].unique())
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.boxplot(
                x=result.factor, y="Resistencia_MPa", hue=result.factor,
                data=df_plot, palette="Set2", legend=False, ax=ax, order=order,
            )
            sns.stripplot(
                x=result.factor, y="Resistencia_MPa",
                data=df_plot, color="black", alpha=0.3, jitter=True, ax=ax, order=order,
            )
            sig_label = "SIGNIFICATIVO" if result.is_significant else "No significativo"
            ax.set_title(
                f"ANOVA - Resistencia por {result.factor} [{sig_label}]",
                fontsize=12, fontweight="bold",
            )
            ax.set_xlabel(result.factor); ax.set_ylabel("Resistencia (MPa)")
            ax.tick_params(axis="x", rotation=90)
            ax.grid(True, linestyle="--", alpha=0.4)
            p = output_dir / fname
            fig.savefig(p, dpi=150, bbox_inches="tight"); plt.close(fig)
            paths[f"anova_{result.factor.lower()}"] = p
        except UserWarning as w:
            log.warning("Matplotlib warning (%s): %s", fname, w)
            plt.close("all")

    # Restore default warning filter after plotting
    warnings.resetwarnings()
    log.info("Graficos generados en: %s", output_dir)
    return paths


# ─────────────────────────────────────────────────────────────────────────────
# PASO 8 — REPORTE DE TEXTO
# ─────────────────────────────────────────────────────────────────────────────

def generate_text_report(
    inference:        InferenceResults,
    anova_edad:       AnovaResults,
    anova_estructura: AnovaResults,
    pred_model:       PredictiveModel,
    output_path:      Path,
) -> str:
    """
    Genera y guarda el reporte de texto completo.

    Returns:
        Contenido del reporte como string.
    """
    SEP = "=" * 100
    sep = "-" * 100
    lines: list[str] = []

    def section(title: str) -> None:
        lines.extend(["", SEP, f"  {title}", SEP, ""])

    section("REPORTE DE CONTROL ESTADISTICO - SIKAGROUT 9400 BR | Blue Tech")
    lines.append(f"Probetas analizadas: {inference.n_total}")
    lines.append(f"Fecha de generacion: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n")

    # ── Tabla descriptiva ─────────────────────────────────────────────────
    section("1. ESTADISTICA DESCRIPTIVA POR EDAD DE ROTURA")
    header = f"{'Edad':>6} {'N':>5} {'Media':>10} {'Desv':>10} {'Min':>10} {'Max':>10} {'CV%':>8} {'Meta':>10} {'Estado':>10}"
    lines.append(header)
    lines.append(sep)
    for _, row in inference.stats_summary.iterrows():
        target = TARGETS.get(float(row["Edad_Dias"]))
        if target:
            estado = "PASA" if row["Media"] >= target else "REVISAR"
        else:
            estado = "---"
        target_str = f"{target:.0f}" if target else "-"
        lines.append(
            f"{row['Edad_Dias']:>6.0f} {int(row['N']):>5} {row['Media']:>10.2f} "
            f"{row['Desv']:>10.2f} {row['Min']:>10.2f} {row['Max']:>10.2f} "
            f"{row['CV_%']:>8.2f} {target_str:>10} {estado:>10}"
        )

    # ── Inferencia a 28 días ──────────────────────────────────────────────
    section("2. INFERENCIA ESTADISTICA (28 DIAS)")
    lines.append(
        f"  Prueba T vs {TARGETS[28.0]} MPa:  "
        f"t = {inference.t_stat_28d:+.4f},  p = {inference.p_value_28d:.4e}"
    )
    lines.append(
        f"  Resultado T-test: "
        f"{'SIGNIFICATIVO (p < 0.05)' if inference.passes_ttest else 'No concluyente (p >= 0.05)'}"
    )
    lines.append(
        f"\n  Resistencia Caracteristica f'ck calculada (Percentil 5): {inference.fck_project:.2f} MPa"
    )
    lines.append(
        f"  Resistencia Caracteristica f'ck requerida (Ficha Tecnica): {inference.fck_required:.2f} MPa"
    )
    lines.append(f"  RESULTADO FINAL: {'APROBADO' if inference.passes_fck else 'REVISAR'}\n")

    # ── ANOVA ─────────────────────────────────────────────────────────────
    for i, anova in enumerate([anova_edad, anova_estructura], start=3):
        section(f"{i}. ANALISIS ANOVA — Factor: {anova.factor}")
        lines.append(anova.anova_table.to_string())
        norm_status = "Normal" if anova.residuals_normal else "No normal (ADVERTENCIA)"
        hom_status  = "Homogeneo" if anova.variances_homogeneous else "No homogeneo (ADVERTENCIA)"
        lines.append(f"\n  Shapiro-Wilk (normalidad residuos):  p = {anova.shapiro_p:.4f} -> {norm_status}")
        lines.append(f"  Levene (homogeneidad de varianzas):  p = {anova.levene_p:.4f} -> {hom_status}")
        if anova.tukey_results:
            lines.append(f"\n  Post-hoc Tukey HSD (alfa=0.05):\n{anova.tukey_results}\n")
        else:
            lines.append(f"\n  Factor NO significativo -> Post-hoc Tukey no aplicable.\n")

    # ── Modelo predictivo ─────────────────────────────────────────────────
    section("5. MODELO PREDICTIVO LOGARITMICO")
    if pred_model.is_trained:
        lines.append(f"  Ecuacion: {pred_model.equation_str}")
        lines.append(f"  R2 = {pred_model.r2_score:.4f}  |  n = {pred_model.n_samples} probetas")
        lines.append(
            f"  Uso: MPa_28d = MPa_actual + {pred_model.slope:.4f} x (ln(28) - ln(edad_actual))"
        )
        lines.append(f"  Meta a 28d: {TARGETS[28.0]} MPa (Ficha Tecnica SikaGrout 9400 BR)\n")
    else:
        lines.append("  Modelo no disponible.\n")

    content = "\n".join(lines)
    output_path.write_text(content, encoding="utf-8")
    log.info("Reporte de texto guardado: %s", output_path.name)
    return content


# ─────────────────────────────────────────────────────────────────────────────
# PASO 9 — REPORTE PDF
# ─────────────────────────────────────────────────────────────────────────────

def _safe_str(text: str) -> str:
    """Convierte texto UTF-8 a latin-1 para compatibilidad con fpdf1."""
    return text.encode("latin-1", "replace").decode("latin-1")


def generate_pdf_report(
    inference:         InferenceResults,
    anova_edad:        AnovaResults,
    anova_estructura:  AnovaResults,
    pred_model:        PredictiveModel,
    plot_paths:        dict[str, Path],
    text_report_path:  Path,
    output_path:       Path,
) -> bool:
    """
    Genera el reporte PDF ejecutivo completo.

    Returns:
        True si el PDF fue generado correctamente, False en caso de error.
    """
    try:
        from fpdf import FPDF
    except ImportError:
        log.error("fpdf no esta instalado. Ejecute: pip install fpdf2")
        return False

    BLUE = (0, 71, 133)
    COL_WIDTHS = [22, 12, 22, 22, 20, 20, 18, 18, 22]

    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 11)
            self.set_fill_color(*BLUE)
            self.set_text_color(255, 255, 255)
            self.cell(0, 10, "  CONTROL DE CALIDAD - SIKAGROUT 9400 BR | Blue Tech", 0, 1, "L", True)
            self.set_text_color(0, 0, 0)
            self.ln(2)

        def footer(self):
            self.set_y(-12)
            self.set_font("Arial", "I", 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f"Pagina {self.page_no()} - Generado por Blue Tech Pipeline", 0, 0, "C")

        def section_title(self, title: str):
            self.set_font("Arial", "B", 13)
            self.set_fill_color(230, 240, 255)
            self.cell(0, 8, _safe_str(f"  {title}"), 1, 1, "L", True)
            self.ln(3)

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Sección 1: Resumen ejecutivo ──────────────────────────────────────
    pdf.section_title("1. Resumen Ejecutivo")
    pdf.set_font("Arial", size=10)

    row_28 = inference.stats_summary[inference.stats_summary["Edad_Dias"] == 28.0]
    media_28 = f"{row_28['Media'].values[0]:.2f} MPa" if not row_28.empty else "N/D"

    for line in [
        f"Probetas analizadas:           {inference.n_total}",
        f"Resistencia Media (28d):       {media_28}",
        f"f'ck proyecto (Percentil 5):   {inference.fck_project:.2f} MPa",
        f"f'ck requerido (Ficha):        {inference.fck_required:.2f} MPa",
        f"Resultado final:               {'APROBADO' if inference.passes_fck else 'REVISAR'}",
    ]:
        pdf.cell(0, 7, _safe_str(line), 0, 1)
    pdf.ln(3)

    # Tabla estadística descriptiva
    pdf.set_font("Arial", "B", 9)
    for h_txt, w in zip(["Edad (d)", "N", "Media", "Desv.", "Min", "Max", "CV%", "Meta", "Estado"], COL_WIDTHS):
        pdf.cell(w, 8, h_txt, 1, 0, "C")
    pdf.ln()
    pdf.set_font("Arial", size=9)
    for _, row in inference.stats_summary.iterrows():
        target = TARGETS.get(float(row["Edad_Dias"]))
        estado = ("PASA" if target and row["Media"] >= target else ("REVISAR" if target else "---"))
        for val, w in zip(
            [
                f"{row['Edad_Dias']:.0f}", str(int(row["N"])),
                f"{row['Media']:.2f}", f"{row['Desv']:.2f}",
                f"{row['Min']:.2f}",   f"{row['Max']:.2f}",
                f"{row['CV_%']:.2f}",  f"{target:.0f}" if target else "-",
                estado,
            ],
            COL_WIDTHS,
        ):
            pdf.cell(w, 7, val, 1, 0, "C")
        pdf.ln()
    pdf.ln(5)

    if "distribucion" in plot_paths and plot_paths["distribucion"].exists():
        pdf.image(str(plot_paths["distribucion"]), x=15, w=175)
    pdf.ln(5)

    # ── Sección 2: Inferencia estadística ────────────────────────────────
    pdf.add_page()
    pdf.section_title("2. Inferencia Estadistica (28 dias)")
    pdf.set_font("Arial", size=10)
    for line in [
        f"Prueba T vs {TARGETS[28.0]} MPa:  t = {inference.t_stat_28d:+.4f},  p = {inference.p_value_28d:.4e}",
        f"Resultado T-test: {'SIGNIFICATIVO (p < 0.05)' if inference.passes_ttest else 'No concluyente'}",
        f"",
        f"f'ck calculado (Percentil 5): {inference.fck_project:.2f} MPa",
        f"f'ck requerido:               {inference.fck_required:.2f} MPa",
        f"RESULTADO FINAL:              {'APROBADO' if inference.passes_fck else 'REVISAR'}",
    ]:
        pdf.cell(0, 7, _safe_str(line), 0, 1)
    pdf.ln(3)

    # ── Sección 3: Modelo predictivo ──────────────────────────────────────
    pdf.section_title("3. Modelo Predictivo Logaritmico")
    pdf.set_font("Arial", size=10)
    if pred_model.is_trained:
        pdf.multi_cell(
            0, 7,
            _safe_str(
                f"Ecuacion: {pred_model.equation_str}\n"
                f"R2 = {pred_model.r2_score:.4f}  |  n = {pred_model.n_samples} probetas\n"
                f"Meta: >= {TARGETS[28.0]} MPa a 28 dias"
            ),
        )
    pdf.ln(3)
    if "crecimiento" in plot_paths and plot_paths["crecimiento"].exists():
        pdf.image(str(plot_paths["crecimiento"]), x=15, w=175)
    if "kde" in plot_paths and plot_paths["kde"].exists():
        pdf.ln(3)
        pdf.image(str(plot_paths["kde"]), x=15, w=175)

    # ── Sección 4: ANOVA ──────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("4. Analisis de Varianza (ANOVA)")
    pdf.set_font("Arial", size=10)
    for anova in [anova_edad, anova_estructura]:
        pdf.set_font("Arial", "B", 10)
        sig = "SIGNIFICATIVO" if anova.is_significant else "No significativo"
        pdf.cell(0, 7, _safe_str(f"Factor: {anova.factor}  ->  {sig}"), 0, 1)
        pdf.set_font("Arial", size=9)
        norm = "Normal" if anova.residuals_normal else "No normal (ADVERTENCIA)"
        hom  = "Homogeneo" if anova.variances_homogeneous else "No homogeneo (ADVERTENCIA)"
        pdf.cell(0, 6, _safe_str(f"  Shapiro-Wilk: p={anova.shapiro_p:.4f} ({norm})  |  Levene: p={anova.levene_p:.4f} ({hom})"), 0, 1)
        pdf.ln(2)
        fname_key = f"anova_{anova.factor.lower()}"
        if fname_key in plot_paths and plot_paths[fname_key].exists():
            pdf.image(str(plot_paths[fname_key]), x=15, w=175)
        pdf.ln(5)

    # ── Sección 5: Reporte de texto completo ─────────────────────────────
    if text_report_path.exists():
        pdf.add_page()
        pdf.section_title("5. Detalle del Reporte de Control de Calidad")
        try:
            text = text_report_path.read_text(encoding="utf-8")
            pdf.set_font("Courier", size=7)
            pdf.multi_cell(0, 4, _safe_str(text))
        except Exception as exc:
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 8, _safe_str(f"Error leyendo reporte: {exc}"), 0, 1)

    pdf.output(str(output_path))
    log.info("Reporte PDF generado: %s", output_path.name)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# ORQUESTADOR PRINCIPAL — run_pipeline()
# ─────────────────────────────────────────────────────────────────────────────

def run_pipeline(
    files:        list[str | Path],
    output_dir:   Path = PROJECT_ROOT,
    db_path:      Optional[Path] = None,
    skip_pdf:     bool = False,
    predict_args: Optional[tuple[float, float]] = None,
) -> dict:
    """
    Ejecuta el pipeline completo de control de calidad del grout.

    Pasos:
      1. Carga y consolidación de archivos Excel/CSV
      2. Estadística descriptiva
      3. Inferencia estadística (t-test, f'ck)
      4. ANOVA por Edad_Dias
      5. ANOVA por Estructura
      6. Modelo predictivo logarítmico
      7. Persistencia en SQLite
      8. Generación de gráficos
      9. Reporte de texto
      10. Reporte PDF

    Args:
        files:        Lista de rutas a archivos Excel/CSV.
        output_dir:   Directorio para master_data_grout.csv y reportes de texto.
        db_path:      Ruta al archivo SQLite (default: BlueTech_Grout.db en PROJECT_ROOT).
        skip_pdf:     Si True, omite la generación del PDF.
        predict_args: (mpa_actual, edad_actual) para predicción puntual a 28d.

    Returns:
        Diccionario con todos los resultados del pipeline.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if db_path is None:
        db_path = PROJECT_ROOT / "BlueTech_Grout.db"

    log.info("=" * 65)
    log.info("BLUE TECH — PIPELINE GROUT — INICIO")
    log.info("Archivos: %d  |  Salida: %s", len(files), output_dir)
    log.info("=" * 65)

    # ── Paso 1: Carga ──────────────────────────────────────────────────────
    log.info("[1/9] Cargando y consolidando datos...")
    df = load_files(files)
    validate_dates(df)

    csv_path = output_dir / "master_data_grout.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    log.info("Master CSV guardado: %s (%d registros).", csv_path.name, len(df))
    log.info("Total de probetas: %d", len(df))

    # ── Paso 2 & 3: Estadística + Inferencia ──────────────────────────────
    log.info("[2/9] Estadistica descriptiva e inferencia estadistica...")
    inference = compute_inference(df)

    # ── Paso 4 & 5: ANOVA ─────────────────────────────────────────────────
    log.info("[3/9] ANOVA por Edad_Dias...")
    anova_edad = perform_anova(df, "Edad_Dias")

    log.info("[4/9] ANOVA por Estructura...")
    anova_estructura = perform_anova(df, "Estructura")

    # ── Paso 6: Modelo predictivo ──────────────────────────────────────────
    log.info("[5/9] Entrenando modelo predictivo logaritmico...")
    pred_model = PredictiveModel()
    pred_model.train(df)

    if predict_args:
        mpa_now, age_now = predict_args
        pred_28 = pred_model.predict_at_28d(mpa_now, age_now)
        status  = "CUMPLE (>= 110 MPa)" if pred_28 >= TARGETS[28.0] else "RIESGO (< 110 MPa)"
        log.info(
            "Prediccion: %.1f MPa a %.0f dias -> %.2f MPa a 28d [%s]",
            mpa_now, age_now, pred_28, status,
        )
        print(f"\n  Proyeccion a 28d: {pred_28:.2f} MPa  [{status}]\n")

    # ── Paso 7: SQLite ────────────────────────────────────────────────────
    log.info("[6/9] Persistiendo en base de datos SQLite...")
    persist_to_database(df, db_path)

    # ── Paso 8: Gráficos ─────────────────────────────────────────────────
    log.info("[7/9] Generando visualizaciones...")
    plot_paths = generate_plots(df, pred_model, anova_edad, anova_estructura, SCRIPT_DIR)

    # ── Paso 9: Reporte de texto ──────────────────────────────────────────
    log.info("[8/9] Generando reporte de texto...")
    txt_path    = PROJECT_ROOT / "Reporte_Control_Calidad_Grout.txt"
    report_text = generate_text_report(
        inference, anova_edad, anova_estructura, pred_model, txt_path
    )
    print(f"\n{report_text}\n")

    # ── Paso 10: PDF ──────────────────────────────────────────────────────
    if not skip_pdf:
        log.info("[9/9] Generando reporte PDF...")
        pdf_path = SCRIPT_DIR / "Reporte_Ejecutivo_Grout.pdf"
        generate_pdf_report(
            inference, anova_edad, anova_estructura,
            pred_model, plot_paths, txt_path, pdf_path,
        )
    else:
        log.info("[9/9] Generacion de PDF omitida (--no-pdf).")

    log.info("=" * 65)
    log.info("BLUE TECH — PIPELINE GROUT — COMPLETADO")
    log.info("=" * 65)

    return {
        "df":               df,
        "inference":        inference,
        "anova_edad":       anova_edad,
        "anova_estructura": anova_estructura,
        "pred_model":       pred_model,
        "plot_paths":       plot_paths,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SELECCIÓN DE ARCHIVOS VÍA GUI (FALLBACK)
# ─────────────────────────────────────────────────────────────────────────────

def select_files_gui() -> list[str]:
    """Abre un diálogo de selección de archivos usando Tkinter."""
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    files = filedialog.askopenfilenames(
        title="Seleccione archivos de Rotura de Grout",
        filetypes=[
            ("Archivos de Datos", "*.xlsx *.xls *.csv"),
            ("Excel", "*.xlsx *.xls"),
            ("CSV",   "*.csv"),
            ("Todos", "*.*"),
        ],
    )
    root.destroy()
    return list(files)


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT — CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pipeline unificado de Control de Calidad - SikaGrout 9400 BR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python grout_pipeline.py
      Abre dialogo GUI para seleccionar archivos.

  python grout_pipeline.py -f ensayo_01.xlsx ensayo_02.xlsx
      Procesa archivos especificados directamente.

  python grout_pipeline.py -f datos.xlsx --no-pdf
      Pipeline completo sin generar PDF.

  python grout_pipeline.py -f datos.xlsx --predict 92 7
      Ejecuta pipeline + proyecta 92 MPa (medidos a 7 dias) a 28 dias.

  python grout_pipeline.py -f datos.xlsx --output-dir ./resultados
      Guarda master CSV y reportes en carpeta personalizada.
        """,
    )
    parser.add_argument(
        "-f", "--files", nargs="+", metavar="ARCHIVO",
        help="Archivos Excel/CSV a procesar (omitir para usar dialogo GUI).",
    )
    parser.add_argument(
        "--no-pdf", action="store_true",
        help="Omitir la generacion del reporte PDF.",
    )
    parser.add_argument(
        "--predict", nargs=2, metavar=("MPa", "EDAD"), type=float,
        help="Proyectar resistencia a 28d. Ejemplo: --predict 92 7",
    )
    parser.add_argument(
        "--output-dir", metavar="DIR", default=str(PROJECT_ROOT),
        help=f"Directorio de salida para CSV y reportes (default: raiz del proyecto).",
    )
    parser.add_argument(
        "--db", metavar="RUTA_DB", default=None,
        help="Ruta al archivo SQLite (default: BlueTech_Grout.db en raiz del proyecto).",
    )

    args = parser.parse_args()

    # Obtener archivos: CLI o GUI
    if args.files:
        files = args.files
    else:
        log.info("No se especificaron archivos. Abriendo dialogo de seleccion...")
        files = select_files_gui()

    if not files:
        log.error("No se seleccionaron archivos. Cancelando.")
        sys.exit(1)

    run_pipeline(
        files=files,
        output_dir=Path(args.output_dir),
        db_path=Path(args.db) if args.db else None,
        skip_pdf=args.no_pdf,
        predict_args=tuple(args.predict) if args.predict else None,
    )


if __name__ == "__main__":
    main()
