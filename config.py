"""
Configuration Module
====================

Configuración centralizada para el sistema de tracking de precios de materiales.

Uso:
    from config import Config
    
    # Acceder a configuraciones
    data_file = Config.DATA_FILE
    rates = Config.EXCHANGE_RATES
"""

import os
from pathlib import Path
from datetime import datetime

class Config:
    """Configuración centralizada del sistema"""
    
    # --- Directorios ---
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    BACKUP_DIR = DATA_DIR / "backups"
    LOG_DIR = BASE_DIR / "logs"
    
    # --- Archivos ---
    OUTPUT_FILE = DATA_DIR / "material_prices.csv"
    LOG_FILE = LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    
    # --- ISO-3 Country Mapping ---
    COUNTRY_MAPPING = {
        # América del Sur
        "Bolivia": "BOL",
        "Santa Cruz": "BOL",
        "Brasil": "BRA",
        "Brazil": "BRA",
        "Argentina": "ARG",
        "Chile": "CHL",
        "Peru": "PER",
        "Perú": "PER",
        "Paraguay": "PRY",
        "Uruguay": "URY",
        "Venezuela": "VEN",
        "Colombia": "COL",
        "Ecuador": "ECU",
        "Guyana": "GUY",
        "Suriname": "SUR",
        
        # América del Norte
        "USA": "USA",
        "United States": "USA",
        "Estados Unidos": "USA",
        "Canada": "CAN",
        "Canadá": "CAN",
        "Mexico": "MEX",
        "México": "MEX",
        
        # América Central
        "Guatemala": "GTM",
        "Honduras": "HND",
        "El Salvador": "SLV",
        "Nicaragua": "NIC",
        "Costa Rica": "CRI",
        "Panama": "PAN",
        "Panamá": "PAN",
        
        # Europa
        "Europe": "EUR",
        "Europa": "EUR",
        "Spain": "ESP",
        "España": "ESP",
        "France": "FRA",
        "Francia": "FRA",
        "Germany": "DEU",
        "Alemania": "DEU",
        "Italy": "ITA",
        "Italia": "ITA",
        "United Kingdom": "GBR",
        "Reino Unido": "GBR",
        "Portugal": "PRT",
        "Netherlands": "NLD",
        "Países Bajos": "NLD",
        
        # Asia
        "China": "CHN",
        "India": "IND",
        "Japan": "JPN",
        "Japón": "JPN",
        "South Korea": "KOR",
        "Corea del Sur": "KOR",
        "Thailand": "THA",
        "Tailandia": "THA",
        "Vietnam": "VNM",
        "Indonesia": "IDN",
        "Malaysia": "MYS",
        "Malasia": "MYS",
        "Philippines": "PHL",
        "Filipinas": "PHL",
        "Singapore": "SGP",
        "Singapur": "SGP",
        
        # Medio Oriente
        "United Arab Emirates": "ARE",
        "Emiratos Árabes": "ARE",
        "Saudi Arabia": "SAU",
        "Arabia Saudita": "SAU",
        "Israel": "ISR",
        "Turkey": "TUR",
        "Turquía": "TUR",
        
        # África
        "South Africa": "ZAF",
        "Sudáfrica": "ZAF",
        "Egypt": "EGY",
        "Egipto": "EGY",
        "Nigeria": "NGA",
        "Kenya": "KEN",
        "Kenia": "KEN",
        
        # Oceanía
        "Australia": "AUS",
        "New Zealand": "NZL",
        "Nueva Zelanda": "NZL",
        
        # Rusia
        "Russia": "RUS",
        "Rusia": "RUS",
        
        # Especiales
        "Global": "GLO",
    }
    
    # --- Exchange Rates to USD (Actualizado Enero 2026) ---
    EXCHANGE_RATES = {
        # Principales monedas
        "USD": 1.0,
        "EUR": 1.10,
        "GBP": 1.28,
        "JPY": 0.0068,
        "CHF": 1.15,
        
        # América del Sur
        "BOB": 0.145,      # Boliviano
        "BRL": 0.20,       # Real Brasileño
        "ARS": 0.001,      # Peso Argentino (muy volátil)
        "CLP": 0.0011,     # Peso Chileno
        "PEN": 0.27,       # Sol Peruano
        "PYG": 0.00013,    # Guaraní Paraguayo
        "UYU": 0.026,      # Peso Uruguayo
        "COP": 0.00025,    # Peso Colombiano
        "VES": 0.000027,   # Bolívar Venezolano
        
        # América del Norte
        "MXN": 0.058,      # Peso Mexicano
        "CAD": 0.72,       # Dólar Canadiense
        
        # Asia
        "CNY": 0.138,      # Yuan Chino
        "INR": 0.012,      # Rupia India
        "KRW": 0.00075,    # Won Surcoreano
        "THB": 0.029,      # Baht Tailandés
        "VND": 0.000040,   # Dong Vietnamita
        "IDR": 0.000063,   # Rupia Indonesia
        "MYR": 0.22,       # Ringgit Malayo
        "PHP": 0.018,      # Peso Filipino
        "SGD": 0.75,       # Dólar de Singapur
        
        # Medio Oriente
        "AED": 0.27,       # Dirham de EAU
        "SAR": 0.27,       # Riyal Saudí
        "ILS": 0.28,       # Shekel Israelí
        "TRY": 0.029,      # Lira Turca
        
        # Rusia
        "RUB": 0.010,      # Rublo Ruso
        
        # África
        "ZAR": 0.055,      # Rand Sudafricano
        "EGP": 0.020,      # Libra Egipcia
        "NGN": 0.00067,    # Naira Nigeriana
        
        # Oceanía
        "AUD": 0.66,       # Dólar Australiano
        "NZD": 0.61,       # Dólar Neozelandés
    }
    
    # --- Scraping Configuration ---
    SCRAPING_CONFIG = {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "timeout": 30,
        "max_retries": 3,
        "delay_between_requests": 1,  # segundos
    }
    
    # --- Data Validation ---
    REQUIRED_FIELDS = ['material', 'country', 'price', 'currency', 'unit']
    
    # --- Backup Configuration ---
    MAX_BACKUPS = 10  # Número máximo de backups a mantener
    
    # --- Dashboard Configuration ---
    DASHBOARD_CONFIG = {
        "page_title": "Global Construction Materials Dashboard",
        "page_icon": "🏗️",
        "layout": "wide",
        "cache_ttl": 3600,  # Cache TTL en segundos (1 hora)
    }
    
    # --- Logging Configuration ---
    LOGGING_CONFIG = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "date_format": "%Y-%m-%d %H:%M:%S",
    }
    
    @classmethod
    def ensure_directories(cls):
        """Asegura que todos los directorios necesarios existan"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.BACKUP_DIR.mkdir(exist_ok=True)
        cls.LOG_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def get_exchange_rate(cls, currency):
        """
        Obtiene la tasa de cambio para una moneda específica.
        
        Args:
            currency: Código de moneda (ej: "BOB", "USD")
            
        Returns:
            float: Tasa de cambio a USD
        """
        return cls.EXCHANGE_RATES.get(currency.upper(), 1.0)
    
    @classmethod
    def get_country_code(cls, country_name):
        """
        Obtiene el código ISO-3 para un país.
        
        Args:
            country_name: Nombre del país
            
        Returns:
            str: Código ISO-3 o "UNK" si no se encuentra
        """
        return cls.COUNTRY_MAPPING.get(country_name, "UNK")


# Asegurar directorios al importar
Config.ensure_directories()
