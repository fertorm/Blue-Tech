from abc import ABC, abstractmethod
from typing import List, Dict
import pandas as pd
from datetime import datetime


class ScraperSource(ABC):
    """
    Abstract base class for material price sources.
    """

    def __init__(self, country: str, currency: str):
        self.country = country
        self.currency = currency

    @abstractmethod
    def fetch_prices(self) -> List[Dict]:
        """
        Fetches prices and returns a list of dictionaries.
        Each dictionary should have:
        - material: str
        - price: float
        - unit: str (e.g., 'ton', 'm3', 'kg')
        - source_url: str
        - date: str (YYYY-MM-DD)
        """
        pass

    def format_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Helper to ensure all fields are present and add country/currency.
        """
        formatted = []
        for item in raw_data:
            # Only set default country/currency if not provided by the individual item
            if "country" not in item:
                item["country"] = self.country
            if "currency" not in item:
                item["currency"] = self.currency

            if "date" not in item:
                item["date"] = datetime.now().strftime("%Y-%m-%d")
            formatted.append(item)
        return formatted
