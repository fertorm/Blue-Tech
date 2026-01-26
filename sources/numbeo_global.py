import requests
from bs4 import BeautifulSoup
from .base_scraper import ScraperSource
import time
import random


class NumbeoGlobalScraper(ScraperSource):
    def __init__(self):
        super().__init__("Global (Numbeo)", "Apartments")
        self.url = "https://www.numbeo.com/cost-of-living/prices_by_country.jsp?displayCurrency=USD&itemId=100"

    def fetch_prices(self):
        """
        Fetches 'Price per Square Meter to Buy Apartment in City Centre' from Numbeo.
        Returns a list of raw data dictionaries.
        """
        print(f"  [Numbeo] Connecting to {self.url}...")

        # Add headers to mimic a browser to avoid 403 Forbidden
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

        try:
            response = requests.get(self.url, headers=headers, timeout=15)
            response.raise_for_status()

            # Rate limiting safety
            time.sleep(random.uniform(1, 2))

            return response.text
        except requests.exceptions.RequestException as e:
            print(f"  [Numbeo] Error fetching data: {e}")
            return None

    def format_data(self, raw_html):
        """
        Parses the HTML and extracts country and price data.
        """
        if not raw_html:
            return []

        formatted_data = []
        soup = BeautifulSoup(raw_html, "html.parser")

        # Find the table containing the prices
        # Numbeo usually uses a table with id "t2" for these rankings
        table = soup.find("table", {"id": "t2"})

        if not table:
            # Fallback: try finding ANY table if ID changed
            print("  [Numbeo] specific table id='t2' not found, searching text...")
            tables = soup.find_all("table")
            for t in tables:
                if "Country" in t.text and "Price" in t.text:
                    table = t
                    break

        if not table:
            print("  [Numbeo] No valid price table found.")
            return []

        # Parse rows
        # The table usually has a <thead> and <tbody>
        tbody = table.find("tbody")
        full_rows = tbody.find_all("tr") if tbody else table.find_all("tr")

        for row in full_rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                # Format: Country Name | Price
                # Sometimes rank is first column, so we need to check

                # Check column contents
                # Usually: [Rank] [Country] [Price] [Bar] OR [Country] [Price]

                country_name = ""
                price_text = ""

                # Try to identify columns by content
                # Country column usually has a link or is text
                # Price column is numeric

                # Heuristic: Find first cell with text, second with number
                possible_values = [c.get_text(strip=True) for c in cols]

                for val in possible_values:
                    # Skip rank numbers (1, 2, 3...)
                    if val.isdigit() and len(val) < 4:
                        continue

                    # If it's a number (price)
                    if any(char.isdigit() for char in val) and "." in val:
                        price_text = val
                        pass
                    # If it's likely a country (alpha only, or with special chars)
                    elif not any(char.isdigit() for char in val) and len(val) > 2:
                        if not country_name:  # First alpha str is likely country
                            country_name = val

                # Refined extraction:
                # On Numbeo table 't2':
                # td[0] = Rank (optional)
                # td[1] = Country Name (within a link usually not always)
                # td[2] = Price

                if len(cols) >= 3:
                    # Standard table layout: Rank, Country, Price, Bar
                    country_col = cols[1]
                    price_col = cols[2]

                    country_name = country_col.get_text(strip=True)
                    price_text = price_col.get_text(strip=True)
                elif len(cols) == 2:
                    # Compact: Country, Price
                    country_name = cols[0].get_text(strip=True)
                    price_text = cols[1].get_text(strip=True)

                if country_name and price_text:
                    try:
                        # Clean price: remove currency symbol if present, extract float
                        # Numbeo format might be "1,234.56" or "1 234.56"
                        clean_price_str = price_text.replace(",", "")
                        price = float(clean_price_str)

                        formatted_data.append(
                            {
                                "country": country_name,
                                "material": "Apartamento (m2 Centro)",  # Proxy for construction cost
                                "price": price,
                                "currency": "USD",  # We requested displayCurrency=USD
                                "unit": "m2",
                                "source": "Numbeo (Global)",
                                "date": "2025-Now",
                                "source_url": self.url,
                            }
                        )
                    except ValueError:
                        continue  # Skip if price parse fails

        return formatted_data
