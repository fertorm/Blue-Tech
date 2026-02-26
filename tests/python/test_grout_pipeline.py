"""
test_grout_pipeline.py — Pytest suite for grout_pipeline.py
==============================================================
Blue Tech | SikaGrout 9400 BR

Tests cover:
  - Data loading and schema validation
  - Date validation (future date rejection)
  - Statistical analysis (ANOVA, t-test)
  - Regression model quality
  - SQLite persistence
  - Full pipeline integration

Run:
  pytest tests/python/test_grout_pipeline.py -v
"""

from __future__ import annotations

import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# ── Path setup ────────────────────────────────────────────────────────────────
# Allow importing grout_pipeline from "Grout Stats/" regardless of cwd
REPO_ROOT = Path(__file__).parent.parent.parent
GROUT_DIR = REPO_ROOT / "Grout Stats"
sys.path.insert(0, str(GROUT_DIR))

import grout_pipeline as gp  # noqa: E402


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_sample_df(n: int = 30) -> pd.DataFrame:
    """Create a synthetic grout DataFrame that mimics real data."""
    rng = np.random.default_rng(42)
    ages = np.repeat([1.0, 7.0, 28.0], n // 3)
    # Realistic MPa values per age group
    mpa = np.where(
        ages == 1.0,  rng.normal(55,  5, len(ages)),
        np.where(
            ages == 7.0,  rng.normal(95,  6, len(ages)),
            rng.normal(118, 7, len(ages)),
        ),
    )
    today = date.today()
    vaciado = [str(today - timedelta(days=int(a) + 5)) for a in ages]
    rotura  = [str(today - timedelta(days=5))           for _ in ages]

    df = pd.DataFrame({
        "ID_Probeta":     [f"P{i:03d}" for i in range(len(ages))],
        "Estructura":     np.tile(["Pilar", "Viga", "Losa"], len(ages) // 3),
        "Fecha_Vaciado":  vaciado,
        "Fecha_Rotura":   rotura,
        "Edad_Dias":      ages,
        "Resistencia_MPa": mpa,
        "Origen_Archivo": "test_fixture.csv",
        "Origen_Hoja":    "Sheet1",
    })
    return df


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return _make_sample_df()


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    """Write a minimal CSV that load_files() can parse (skiprows=5, 14 cols)."""
    df = _make_sample_df()
    csv_path = tmp_path / "test_data.csv"

    # Build a raw CSV with 5 header rows and 14+ columns so load_files parses correctly
    # Column indices used: [1,2,5,6,7,13] → ID_Probeta, Estructura, Fecha_Vaciado,
    #                                         Fecha_Rotura, Edad_Dias, Resistencia_MPa
    rows = [[""] * 14 for _ in range(5)]  # 5 skip rows
    header = ["col0", "ID_Probeta", "Estructura", "col3", "col4",
              "Fecha_Vaciado", "Fecha_Rotura", "Edad_Dias", "col8",
              "col9", "col10", "col11", "col12", "Resistencia_MPa"]
    rows.append(header)
    for _, row in df.iterrows():
        data_row = [""] * 14
        data_row[1]  = row["ID_Probeta"]
        data_row[2]  = row["Estructura"]
        data_row[5]  = row["Fecha_Vaciado"]
        data_row[6]  = row["Fecha_Rotura"]
        data_row[7]  = str(row["Edad_Dias"])
        data_row[13] = str(row["Resistencia_MPa"])
        rows.append(data_row)

    with open(csv_path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(",".join(r) + "\n")

    return csv_path


# ── Test 1: Data Loading ───────────────────────────────────────────────────────

class TestLoadData:
    def test_load_data_schema(self, sample_csv: Path):
        """load_files() returns a DataFrame with all expected columns."""
        df = gp.load_files([sample_csv])

        expected_cols = {"ID_Probeta", "Estructura", "Fecha_Vaciado",
                         "Fecha_Rotura", "Edad_Dias", "Resistencia_MPa",
                         "Origen_Archivo", "Origen_Hoja"}
        assert expected_cols.issubset(set(df.columns)), (
            f"Missing columns: {expected_cols - set(df.columns)}"
        )

    def test_load_data_row_count(self, sample_csv: Path):
        """load_files() returns the expected number of rows."""
        df = gp.load_files([sample_csv])
        assert len(df) == 30

    def test_load_data_numeric_types(self, sample_csv: Path):
        """Edad_Dias and Resistencia_MPa are numeric after loading."""
        df = gp.load_files([sample_csv])
        assert pd.api.types.is_numeric_dtype(df["Edad_Dias"])
        assert pd.api.types.is_numeric_dtype(df["Resistencia_MPa"])

    def test_load_data_no_nulls_in_key_cols(self, sample_csv: Path):
        """No null values remain in key columns after loading."""
        df = gp.load_files([sample_csv])
        assert df["Edad_Dias"].isna().sum() == 0
        assert df["Resistencia_MPa"].isna().sum() == 0

    def test_load_data_raises_on_empty(self, tmp_path: Path):
        """load_files() raises ValueError when no valid data is found."""
        empty_csv = tmp_path / "empty.csv"
        empty_csv.write_text("a,b\n1,2\n")  # Only 2 columns, no valid data
        with pytest.raises(ValueError, match="No se procesaron datos"):
            gp.load_files([empty_csv])


# ── Test 2: Date Validation ────────────────────────────────────────────────────

class TestDateValidation:
    def test_validate_dates_accepts_past_dates(self, sample_df: pd.DataFrame):
        """validate_dates() does not raise for rows with past dates."""
        # All dates in sample_df are in the past — should pass silently
        warnings_found = gp.validate_dates(sample_df)
        assert warnings_found == 0

    def test_validate_dates_detects_future_rotura(self, sample_df: pd.DataFrame):
        """validate_dates() detects rows where Fecha_Rotura is in the future."""
        future_date = str(date.today() + timedelta(days=10))
        df_bad = sample_df.copy()
        df_bad.loc[0, "Fecha_Rotura"] = future_date

        warnings_found = gp.validate_dates(df_bad)
        assert warnings_found >= 1

    def test_validate_dates_detects_future_vaciado(self, sample_df: pd.DataFrame):
        """validate_dates() detects rows where Fecha_Vaciado is in the future."""
        future_date = str(date.today() + timedelta(days=3))
        df_bad = sample_df.copy()
        df_bad.loc[1, "Fecha_Vaciado"] = future_date

        warnings_found = gp.validate_dates(df_bad)
        assert warnings_found >= 1

    def test_validate_dates_handles_non_date_strings(self, sample_df: pd.DataFrame):
        """validate_dates() does not crash on non-parseable date strings."""
        df_bad = sample_df.copy()
        df_bad.loc[0, "Fecha_Rotura"] = "not-a-date"
        # Should not raise — just skip or log
        try:
            gp.validate_dates(df_bad)
        except Exception as exc:
            pytest.fail(f"validate_dates() raised unexpectedly: {exc}")


# ── Test 3: Statistical Analysis ───────────────────────────────────────────────

class TestStatisticalAnalysis:
    def test_t_test_returns_numeric(self, sample_df: pd.DataFrame):
        """compute_inference() returns numeric t-stat and p-value."""
        result = gp.compute_inference(sample_df)
        assert isinstance(result.t_stat_28d, float)
        assert isinstance(result.p_value_28d, float)
        assert not np.isnan(result.t_stat_28d)
        assert not np.isnan(result.p_value_28d)

    def test_p_value_in_valid_range(self, sample_df: pd.DataFrame):
        """p-value is between 0 and 1."""
        result = gp.compute_inference(sample_df)
        assert 0.0 <= result.p_value_28d <= 1.0

    def test_anova_returns_valid_table(self, sample_df: pd.DataFrame):
        """perform_anova() returns a DataFrame with expected ANOVA columns."""
        result = gp.perform_anova(sample_df, "Edad_Dias")
        assert result.anova_table is not None
        assert "PR(>F)" in result.anova_table.columns
        assert isinstance(result.shapiro_stat, float)
        assert isinstance(result.levene_stat, float)

    def test_anova_structure_returns_valid_table(self, sample_df: pd.DataFrame):
        """perform_anova() works for the Estructura factor."""
        result = gp.perform_anova(sample_df, "Estructura")
        assert result.factor == "Estructura"
        assert 0.0 <= result.shapiro_p <= 1.0
        assert 0.0 <= result.levene_p <= 1.0

    def test_fck_is_numeric(self, sample_df: pd.DataFrame):
        """f'ck characteristic resistance is a valid float."""
        result = gp.compute_inference(sample_df)
        assert isinstance(result.fck_project, float)
        assert result.fck_project > 0


# ── Test 4: Regression Model ───────────────────────────────────────────────────

class TestRegressionModel:
    def test_r2_above_threshold(self, sample_df: pd.DataFrame):
        """Logarithmic model achieves R² > 0.5 on synthetic data."""
        model = gp.PredictiveModel()
        model.train(sample_df)
        assert model.r2_score > 0.5, f"R² too low: {model.r2_score:.4f}"

    def test_slope_is_positive(self, sample_df: pd.DataFrame):
        """Model slope is positive (resistance increases with age)."""
        model = gp.PredictiveModel()
        model.train(sample_df)
        assert model.slope > 0, f"Slope should be positive, got {model.slope:.4f}"

    def test_intercept_is_numeric(self, sample_df: pd.DataFrame):
        """Model intercept is a valid float."""
        model = gp.PredictiveModel()
        model.train(sample_df)
        assert isinstance(model.intercept, float)
        assert not np.isnan(model.intercept)

    def test_predict_at_28d(self, sample_df: pd.DataFrame):
        """predict_at_28d() returns a reasonable MPa projection."""
        model = gp.PredictiveModel()
        model.train(sample_df)
        pred = model.predict_at_28d(mpa_at_age=95.0, age_days=7.0)
        # Prediction should be higher than 7-day value (logarithmic growth)
        assert pred > 95.0
        # And should not be unrealistically high
        assert pred < 300.0

    def test_predict_raises_before_training(self):
        """predict_at_28d() raises RuntimeError if model is not trained."""
        model = gp.PredictiveModel()
        with pytest.raises(RuntimeError, match="no entrenado"):
            model.predict_at_28d(95.0, 7.0)


# ── Test 5: Database Persistence ───────────────────────────────────────────────

class TestDatabasePersistence:
    def test_persist_creates_table(self, sample_df: pd.DataFrame, tmp_path: Path):
        """persist_to_database() creates the Roturas table in SQLite."""
        db_path = tmp_path / "test.db"
        gp.persist_to_database(sample_df, db_path)

        conn = sqlite3.connect(db_path)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        conn.close()
        assert any("Roturas" in str(t) for t in tables)

    def test_persist_record_count(self, sample_df: pd.DataFrame, tmp_path: Path):
        """persist_to_database() inserts the correct number of records."""
        db_path = tmp_path / "test.db"
        count = gp.persist_to_database(sample_df, db_path)
        assert count == len(sample_df)

    def test_persist_data_integrity(self, sample_df: pd.DataFrame, tmp_path: Path):
        """Records in SQLite match the source DataFrame."""
        db_path = tmp_path / "test.db"
        gp.persist_to_database(sample_df, db_path)

        conn = sqlite3.connect(db_path)
        db_df = pd.read_sql("SELECT * FROM Roturas", conn)
        conn.close()

        assert set(db_df.columns) == set(sample_df.columns)
        assert len(db_df) == len(sample_df)


# ── Test 6: Pipeline Integration ───────────────────────────────────────────────

class TestPipelineIntegration:
    def test_pipeline_full_flow(self, sample_csv: Path, tmp_path: Path):
        """run_pipeline() completes without error and returns expected keys."""
        db_path = tmp_path / "test.db"
        result = gp.run_pipeline(
            files=[sample_csv],
            output_dir=tmp_path,
            db_path=db_path,
            skip_pdf=True,
        )

        assert "df" in result
        assert "inference" in result
        assert "anova_edad" in result
        assert "anova_estructura" in result
        assert "pred_model" in result

    def test_pipeline_creates_master_csv(self, sample_csv: Path, tmp_path: Path):
        """run_pipeline() writes master_data_grout.csv to output_dir."""
        db_path = tmp_path / "test.db"
        gp.run_pipeline(
            files=[sample_csv],
            output_dir=tmp_path,
            db_path=db_path,
            skip_pdf=True,
        )
        assert (tmp_path / "master_data_grout.csv").exists()

    def test_pipeline_persists_to_sqlite(self, sample_csv: Path, tmp_path: Path):
        """run_pipeline() writes records to the SQLite database."""
        db_path = tmp_path / "test.db"
        gp.run_pipeline(
            files=[sample_csv],
            output_dir=tmp_path,
            db_path=db_path,
            skip_pdf=True,
        )
        assert db_path.exists()
        conn = sqlite3.connect(db_path)
        count = conn.execute("SELECT COUNT(*) FROM Roturas").fetchone()[0]
        conn.close()
        assert count > 0

    def test_pipeline_model_quality(self, sample_csv: Path, tmp_path: Path):
        """Predictive model from run_pipeline() achieves R² > 0.5."""
        db_path = tmp_path / "test.db"
        result = gp.run_pipeline(
            files=[sample_csv],
            output_dir=tmp_path,
            db_path=db_path,
            skip_pdf=True,
        )
        assert result["pred_model"].r2_score > 0.5
