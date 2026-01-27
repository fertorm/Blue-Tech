"""
Material Price Scraper
======================

Script para recolectar precios de materiales de construcción de múltiples fuentes.

Características:
- Scraping de múltiples fuentes de datos
- Validación de datos recolectados
- Backup automático de datos anteriores
- Logging detallado
- Manejo robusto de errores

Uso:
    python material_scraper.py

Autor: Blue Tech
Fecha: Enero 2026
"""

import os
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path
from sources.static_data import StaticDataSource
from sources.numbeo_global import NumbeoGlobalScraper

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/scraper.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# --- Configuration ---
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = DATA_DIR / "backups"
OUTPUT_FILE = DATA_DIR / "material_prices.csv"

# Asegurar que existan los directorios
DATA_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)


# --- Validation Functions ---
def validate_data(data_list):
    """
    Valida los datos recolectados antes de guardarlos.

    Args:
        data_list: Lista de diccionarios con datos de precios

    Returns:
        list: Lista de datos validados
    """
    required_fields = ["material", "country", "price", "currency", "unit"]
    validated = []
    invalid_count = 0

    for item in data_list:
        # Verificar campos requeridos
        if not all(field in item for field in required_fields):
            logger.warning(f"Missing required fields in item: {item}")
            invalid_count += 1
            continue

        # Validar precio positivo
        try:
            price = float(item["price"])
            if price <= 0:
                logger.warning(
                    f"Invalid price (<=0) for {item.get('material')}: {price}"
                )
                invalid_count += 1
                continue
        except (ValueError, TypeError):
            logger.warning(
                f"Invalid price format for {item.get('material')}: {item.get('price')}"
            )
            invalid_count += 1
            continue

        # Validar que los strings no estén vacíos
        if not item["material"].strip() or not item["country"].strip():
            logger.warning(f"Empty material or country in item: {item}")
            invalid_count += 1
            continue

        validated.append(item)

    if invalid_count > 0:
        logger.warning(f"Total invalid records: {invalid_count}")

    logger.info(
        f"Validation complete: {len(validated)} valid records out of {len(data_list)}"
    )
    return validated


def deduplicate_data(df):
    """
    Elimina registros duplicados del DataFrame.

    Args:
        df: DataFrame con datos de precios

    Returns:
        pd.DataFrame: DataFrame sin duplicados
    """
    initial_count = len(df)

    # Eliminar duplicados exactos
    df = df.drop_duplicates()

    # Eliminar duplicados basados en material + país + fuente
    # (mantener el más reciente si hay diferencias en precio)
    df = df.sort_values("extraction_date", ascending=False)
    df = df.drop_duplicates(subset=["material", "country", "source"], keep="first")

    removed = initial_count - len(df)
    if removed > 0:
        logger.info(f"Removed {removed} duplicate records")

    return df


# --- Data Management Functions ---
def save_data_with_backup(df, output_file):
    """
    Guarda los datos y crea un backup de la versión anterior.

    Args:
        df: DataFrame a guardar
        output_file: Path del archivo de salida
    """
    try:
        # Crear backup si existe archivo anterior
        if output_file.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = BACKUP_DIR / f"material_prices_backup_{timestamp}.csv"

            # Copiar archivo existente a backup
            import shutil

            shutil.copy2(output_file, backup_file)
            logger.info(f"✅ Previous data backed up to: {backup_file}")

            # Limpiar backups antiguos (mantener solo los últimos 10)
            cleanup_old_backups()

        # Guardar nuevo archivo
        df.to_csv(output_file, index=False, encoding="utf-8")
        logger.info(f"✅ Data saved successfully to: {output_file}")

    except Exception as e:
        logger.error(f"❌ Error saving data: {e}", exc_info=True)
        raise


def cleanup_old_backups(max_backups=10):
    """
    Limpia backups antiguos, manteniendo solo los más recientes.

    Args:
        max_backups: Número máximo de backups a mantener
    """
    try:
        backup_files = sorted(BACKUP_DIR.glob("material_prices_backup_*.csv"))

        if len(backup_files) > max_backups:
            files_to_remove = backup_files[:-max_backups]
            for file in files_to_remove:
                file.unlink()
                logger.info(f"Removed old backup: {file.name}")

            logger.info(f"Cleaned up {len(files_to_remove)} old backup(s)")

    except Exception as e:
        logger.warning(f"Error cleaning up backups: {e}")


def display_statistics(df):
    """
    Muestra estadísticas sobre los datos recolectados.

    Args:
        df: DataFrame con los datos
    """
    logger.info("\n" + "=" * 60)
    logger.info("📊 DATA COLLECTION STATISTICS")
    logger.info("=" * 60)
    logger.info(f"Total records: {len(df)}")
    logger.info(f"Unique materials: {df['material'].nunique()}")
    logger.info(f"Materials: {', '.join(df['material'].unique())}")
    logger.info(f"Countries covered: {df['country'].nunique()}")
    logger.info(f"Countries: {', '.join(sorted(df['country'].unique()))}")
    logger.info(f"Data sources: {df['source'].nunique()}")
    logger.info(f"Sources: {', '.join(df['source'].unique())}")

    if "extraction_date" in df.columns:
        logger.info(f"Extraction date: {df['extraction_date'].iloc[0]}")

    # Estadísticas por fuente
    logger.info("\nRecords by source:")
    source_counts = df["source"].value_counts()
    for source, count in source_counts.items():
        logger.info(f"  - {source}: {count} records")

    logger.info("=" * 60 + "\n")


# --- Main Scraper Function ---
def main():
    """Función principal del scraper"""

    logger.info("=" * 60)
    logger.info("🚀 STARTING MATERIAL PRICE SCRAPER")
    logger.info("=" * 60)
    start_time = datetime.now()

    # 1. Initialize Sources
    sources = [
        StaticDataSource(),
        NumbeoGlobalScraper(),
        # Agregar más scrapers aquí en el futuro
        # Example: AmazonScraper(), HomeDepotScraper(), etc.
    ]

    logger.info(f"Initialized {len(sources)} data source(s)")

    all_data = []
    errors = []
    source_stats = {}

    # 2. Fetch Data from each source
    for source in sources:
        source_name = source.__class__.__name__

        try:
            logger.info(f"\n{'─'*60}")
            logger.info(f"📡 Fetching from: {source_name}")
            logger.info(f"{'─'*60}")

            # Fetch raw data
            raw_data = source.fetch_prices()
            logger.info(f"  ➜ Raw data fetched: {len(raw_data)} items")

            # Format data
            formatted_data = source.format_data(raw_data)
            logger.info(f"  ➜ Data formatted: {len(formatted_data)} items")

            # Validate data
            validated_data = validate_data(formatted_data)
            logger.info(f"  ➜ Data validated: {len(validated_data)} valid items")

            all_data.extend(validated_data)
            source_stats[source_name] = {
                "raw": len(raw_data),
                "formatted": len(formatted_data),
                "validated": len(validated_data),
            }

            logger.info(f"✅ {source_name} completed successfully")

        except Exception as e:
            error_msg = f"Failed to fetch from {source_name}: {str(e)}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            errors.append(error_msg)
            source_stats[source_name] = {"error": str(e)}

    # 3. Process and Save Data
    logger.info(f"\n{'='*60}")
    logger.info("💾 PROCESSING COLLECTED DATA")
    logger.info(f"{'='*60}")

    if all_data:
        # Create DataFrame
        df = pd.DataFrame(all_data)
        logger.info(f"Created DataFrame with {len(df)} records")

        # Add extraction timestamp if not present
        if "extraction_date" not in df.columns:
            df["extraction_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Deduplicate
        df = deduplicate_data(df)

        # Sort by material and country
        df = df.sort_values(["material", "country"])

        # Display statistics
        display_statistics(df)

        # Save with backup
        try:
            save_data_with_backup(df, OUTPUT_FILE)
            logger.info(f"✅ SUCCESS! Data saved to {OUTPUT_FILE}")
        except Exception as e:
            logger.error(f"❌ Failed to save data: {e}")
            errors.append(f"Failed to save data: {e}")
    else:
        logger.warning("⚠️  No data collected from any source!")

    # 4. Summary Report
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    logger.info(f"\n{'='*60}")
    logger.info("📋 SCRAPING SESSION SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Duration: {duration:.2f} seconds")
    logger.info(f"Total sources attempted: {len(sources)}")
    logger.info(f"Successful sources: {len(sources) - len(errors)}")
    logger.info(f"Failed sources: {len(errors)}")

    if all_data:
        logger.info(f"Total valid records collected: {len(all_data)}")
        logger.info(f"Final records after deduplication: {len(df)}")
    else:
        logger.info("Total valid records collected: 0")

    # Source-by-source breakdown
    logger.info("\nSource breakdown:")
    for source_name, stats in source_stats.items():
        if "error" in stats:
            logger.info(f"  ❌ {source_name}: ERROR - {stats['error']}")
        else:
            logger.info(f"  ✅ {source_name}:")
            logger.info(
                f"     Raw: {stats['raw']}, "
                f"Formatted: {stats['formatted']}, "
                f"Validated: {stats['validated']}"
            )

    if errors:
        logger.warning(f"\n⚠️  Completed with {len(errors)} error(s):")
        for error in errors:
            logger.warning(f"  - {error}")
    else:
        logger.info("\n✅ All sources processed successfully!")

    logger.info(f"{'='*60}")
    logger.info("🏁 SCRAPER FINISHED")
    logger.info(f"{'='*60}\n")

    return len(all_data) > 0


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Scraping interrupted by user")
        exit(130)
    except Exception as e:
        logger.error(f"\n❌ Critical error: {e}", exc_info=True)
        exit(1)
