from typing import List, Dict
from .base_scraper import ScraperSource


class StaticDataSource(ScraperSource):
    def __init__(self):
        # We don't set a single country/currency because this source covers multiple
        super().__init__("Global", "Mixed")

    def fetch_prices(self) -> List[Dict]:
        data = []

        # --- BOLIVIA (Source: Research/Cadecocruz/Local Markets 2024-2025) ---
        # Currency: BOB
        # Cement ~ 50 BOB / 50kg bag -> ~1000 BOB / ton
        # Steel ~ 2000 USD / ton -> ~13920 BOB / ton (official)
        # Sand ~ 180-250 BOB / m3
        data.extend(
            [
                {
                    "country": "Bolivia",
                    "material": "Acero",
                    "price": 13920.0,
                    "currency": "BOB",
                    "unit": "ton",
                    "source": "Estimado (Mercado Local)",
                },
                {
                    "country": "Bolivia",
                    "material": "Cemento",
                    "price": 50.0,
                    "currency": "BOB",
                    "unit": "bolsa (50kg)",
                    "source": "Cadecocruz/Mercado",
                },
                {
                    "country": "Bolivia",
                    "material": "Arena",
                    "price": 250.0,
                    "currency": "BOB",
                    "unit": "m3",
                    "source": "Reportes Locales",
                },
                {
                    "country": "Bolivia",
                    "material": "Ladrillo",
                    "price": 1.5,
                    "currency": "BOB",
                    "unit": "unidad",
                    "source": "Promedio Local",
                },
            ]
        )

        # --- USA (Source: PPI/Market Indices 2025) ---
        # Currency: USD
        # Steel (HRC) ~ 983 USD / ton
        # Concrete ~ 150 USD / m3
        data.extend(
            [
                {
                    "country": "USA",
                    "material": "Acero",
                    "price": 983.0,
                    "currency": "USD",
                    "unit": "ton",
                    "source": "SteelBenchmarker",
                },
                {
                    "country": "USA",
                    "material": "Concreto",
                    "price": 150.0,
                    "currency": "USD",
                    "unit": "m3",
                    "source": "Market Estimate",
                },
                {
                    "country": "USA",
                    "material": "Madera",
                    "price": 600.0,
                    "currency": "USD",
                    "unit": "1000 bd ft",
                    "source": "TradingEconomics Approx",
                },
            ]
        )

        # --- CHINA (Source: Market Reports 2025) ---
        # Currency: CNY
        # Steel ~ 3130 CNY / ton
        data.extend(
            [
                {
                    "country": "China",
                    "material": "Acero",
                    "price": 3130.0,
                    "currency": "CNY",
                    "unit": "ton",
                    "source": "Shanghai Futures",
                },
                {
                    "country": "China",
                    "material": "Concreto",
                    "price": 400.0,
                    "currency": "CNY",
                    "unit": "m3",
                    "source": "Estimate",
                },
            ]
        )

        # --- BRASIL (Source: SINAPI/Market 2024) ---
        # Currency: BRL
        # Steel ~ 4000 BRL / ton
        data.extend(
            [
                {
                    "country": "Brasil",
                    "material": "Acero",
                    "price": 4000.0,
                    "currency": "BRL",
                    "unit": "ton",
                    "source": "Estimativa Mercado",
                },
                {
                    "country": "Brasil",
                    "material": "Cimento",
                    "price": 35.0,
                    "currency": "BRL",
                    "unit": "saco (50kg)",
                    "source": "Varejo",
                },
            ]
        )

        # --- ARGENTINA (Source: AyC/Sodimac) ---
        # Currency: ARS (Highly volatile, using approx current)
        data.extend(
            [
                {
                    "country": "Argentina",
                    "material": "Cemento",
                    "price": 9000.0,
                    "currency": "ARS",
                    "unit": "bolsa (50kg)",
                    "source": "Estimado Local",
                },
                {
                    "country": "Argentina",
                    "material": "Acero",
                    "price": 1200000.0,
                    "currency": "ARS",
                    "unit": "ton",
                    "source": "Estimado Local",
                },
            ]
        )

        # --- RUSSIA ---
        # Currency: RUB
        data.extend(
            [
                {
                    "country": "Rusia",
                    "material": "Acero",
                    "price": 45000.0,
                    "currency": "RUB",
                    "unit": "ton",
                    "source": "Estimate",
                },
            ]
        )

        # --- INDIA ---
        # Currency: INR
        data.extend(
            [
                {
                    "country": "India",
                    "material": "Acero",
                    "price": 45000.0,
                    "currency": "INR",
                    "unit": "ton",
                    "source": "Market Estimate",
                },
                {
                    "country": "India",
                    "material": "Cemento",
                    "price": 350.0,
                    "currency": "INR",
                    "unit": "bag (50kg)",
                    "source": "Market Estimate",
                },
            ]
        )

        # Add common fields
        formatted = []
        for item in data:
            item["date"] = "2024-2025 (Ref)"
            item["source_url"] = "Static Seed Data"
            formatted.append(item)

        return formatted
