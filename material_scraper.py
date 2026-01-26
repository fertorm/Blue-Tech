import os
import pandas as pd
from datetime import datetime
from sources.static_data import StaticDataSource
from sources.numbeo_global import NumbeoGlobalScraper

# Define the output directory and file
DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "material_prices.csv")


def main():
    print("--- Starting Material Price Scraper ---")

    # 1. Initialize Sources
    sources = [
        StaticDataSource(),
        # Future: Add dynamic scrapers here
        NumbeoGlobalScraper(),
    ]

    all_data = []

    # 2. Fetch Data
    for source in sources:
        try:
            print(f"Fetching from {source.__class__.__name__}...")
            raw_data = source.fetch_prices()
            formatted_data = source.format_data(raw_data)
            all_data.extend(formatted_data)
            print(f"  -> {len(formatted_data)} records found.")
        except Exception as e:
            print(f"  [ERROR] Failed to fetch from {source.__class__.__name__}: {e}")

    # 3. Save to CSV
    if all_data:
        # Create data directory if it doesn't exist
        os.makedirs(DATA_DIR, exist_ok=True)

        df = pd.DataFrame(all_data)

        # Add timestamp of extraction if not present (redundant check but safe)
        if "extraction_date" not in df.columns:
            df["extraction_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        df.to_csv(OUTPUT_FILE, index=False)
        print(f"--- Success! Data saved to {OUTPUT_FILE} ({len(df)} records) ---")
    else:
        print("--- No data collected. ---")


if __name__ == "__main__":
    main()
