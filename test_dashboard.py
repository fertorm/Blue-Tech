"""
Unit Tests for Material Dashboard
==================================

Tests para validar las funciones del dashboard de materiales.

Uso:
    pytest tests/test_dashboard.py
    pytest tests/test_dashboard.py -v  # verbose
    pytest tests/test_dashboard.py --cov  # con coverage
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config


class TestConversion:
    """Tests para conversión de monedas"""
    
    def test_usd_conversion(self):
        """Test conversión de USD a USD"""
        assert Config.get_exchange_rate("USD") == 1.0
    
    def test_bob_conversion(self):
        """Test conversión de BOB a USD"""
        rate = Config.get_exchange_rate("BOB")
        assert rate > 0
        assert rate < 1  # BOB es menos que USD
    
    def test_eur_conversion(self):
        """Test conversión de EUR a USD"""
        rate = Config.get_exchange_rate("EUR")
        assert rate > 1  # EUR es más que USD
    
    def test_unknown_currency(self):
        """Test manejo de moneda desconocida"""
        rate = Config.get_exchange_rate("XYZ")
        assert rate == 1.0  # Fallback a USD


class TestCountryMapping:
    """Tests para mapeo de países"""
    
    def test_bolivia_mapping(self):
        """Test mapeo de Bolivia"""
        assert Config.get_country_code("Bolivia") == "BOL"
        assert Config.get_country_code("Santa Cruz") == "BOL"
    
    def test_brazil_variations(self):
        """Test variaciones de Brasil"""
        assert Config.get_country_code("Brazil") == "BRA"
        assert Config.get_country_code("Brasil") == "BRA"
    
    def test_usa_variations(self):
        """Test variaciones de USA"""
        assert Config.get_country_code("USA") == "USA"
        assert Config.get_country_code("United States") == "USA"
        assert Config.get_country_code("Estados Unidos") == "USA"
    
    def test_unknown_country(self):
        """Test país desconocido"""
        assert Config.get_country_code("UnknownCountry") == "UNK"


class TestDataValidation:
    """Tests para validación de datos"""
    
    def test_valid_price_data(self):
        """Test datos válidos"""
        data = {
            'material': 'Cement',
            'country': 'Bolivia',
            'price': 100.0,
            'currency': 'BOB',
            'unit': 'bag'
        }
        # Todos los campos requeridos presentes
        assert all(field in data for field in Config.REQUIRED_FIELDS)
    
    def test_missing_field(self):
        """Test datos con campos faltantes"""
        data = {
            'material': 'Cement',
            'country': 'Bolivia',
            # Falta price, currency, unit
        }
        assert not all(field in data for field in Config.REQUIRED_FIELDS)
    
    def test_invalid_price(self):
        """Test precio inválido"""
        assert not (0 > 0)  # Precio negativo
        assert not (-100 > 0)


class TestDataFrame:
    """Tests para operaciones con DataFrames"""
    
    def test_empty_dataframe(self):
        """Test DataFrame vacío"""
        df = pd.DataFrame()
        assert df.empty
        assert len(df) == 0
    
    def test_dataframe_with_data(self):
        """Test DataFrame con datos"""
        df = pd.DataFrame({
            'material': ['Cement', 'Steel'],
            'price': [100, 500],
            'country': ['Bolivia', 'Brazil']
        })
        assert not df.empty
        assert len(df) == 2
        assert 'material' in df.columns
    
    def test_filter_dataframe(self):
        """Test filtrado de DataFrame"""
        df = pd.DataFrame({
            'material': ['Cement', 'Steel', 'Cement'],
            'price': [100, 500, 120],
            'country': ['Bolivia', 'Brazil', 'Argentina']
        })
        
        cement_df = df[df['material'] == 'Cement']
        assert len(cement_df) == 2
        assert all(cement_df['material'] == 'Cement')
    
    def test_numeric_conversion(self):
        """Test conversión a numérico"""
        df = pd.DataFrame({
            'price': ['100', '200', 'invalid', '300']
        })
        
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df = df.dropna(subset=['price'])
        
        assert len(df) == 3  # Solo valores válidos
        assert all(isinstance(x, float) for x in df['price'])


class TestStatistics:
    """Tests para cálculos estadísticos"""
    
    def test_mean_calculation(self):
        """Test cálculo de promedio"""
        df = pd.DataFrame({'price': [100, 200, 300]})
        assert df['price'].mean() == 200
    
    def test_min_max(self):
        """Test valores mínimo y máximo"""
        df = pd.DataFrame({'price': [100, 200, 300, 50, 500]})
        assert df['price'].min() == 50
        assert df['price'].max() == 500
    
    def test_standard_deviation(self):
        """Test desviación estándar"""
        df = pd.DataFrame({'price': [100, 200, 300]})
        std = df['price'].std()
        assert std > 0
    
    def test_unique_count(self):
        """Test conteo de valores únicos"""
        df = pd.DataFrame({
            'material': ['Cement', 'Steel', 'Cement', 'Wood']
        })
        assert df['material'].nunique() == 3


class TestConfiguration:
    """Tests para configuración"""
    
    def test_directories_exist(self):
        """Test que directorios existen"""
        assert Config.DATA_DIR.exists()
        assert Config.BACKUP_DIR.exists()
    
    def test_required_fields(self):
        """Test campos requeridos definidos"""
        assert len(Config.REQUIRED_FIELDS) > 0
        assert 'material' in Config.REQUIRED_FIELDS
        assert 'price' in Config.REQUIRED_FIELDS
    
    def test_exchange_rates_exist(self):
        """Test tasas de cambio definidas"""
        assert len(Config.EXCHANGE_RATES) > 0
        assert 'USD' in Config.EXCHANGE_RATES
        assert Config.EXCHANGE_RATES['USD'] == 1.0


# Fixtures para tests
@pytest.fixture
def sample_dataframe():
    """DataFrame de ejemplo para tests"""
    return pd.DataFrame({
        'material': ['Cement', 'Steel', 'Wood', 'Cement'],
        'country': ['Bolivia', 'Brazil', 'Chile', 'Argentina'],
        'price': [100, 500, 200, 120],
        'currency': ['BOB', 'BRL', 'CLP', 'ARS'],
        'unit': ['bag', 'ton', 'm3', 'bag'],
        'source': ['Static', 'Numbeo', 'Static', 'Numbeo']
    })


def test_sample_fixture(sample_dataframe):
    """Test usando el fixture"""
    assert len(sample_dataframe) == 4
    assert 'material' in sample_dataframe.columns


# Tests de integración
class TestIntegration:
    """Tests de integración de componentes"""
    
    def test_complete_workflow(self, sample_dataframe):
        """Test flujo completo de datos"""
        df = sample_dataframe
        
        # 1. Filtrar por material
        cement = df[df['material'] == 'Cement']
        assert len(cement) == 2
        
        # 2. Convertir precios a USD (simulado)
        cement['price_usd'] = cement['price'] * 0.145  # BOB rate
        
        # 3. Calcular estadísticas
        avg_price = cement['price_usd'].mean()
        assert avg_price > 0
        
        # 4. Encontrar min/max
        min_idx = cement['price_usd'].idxmin()
        max_idx = cement['price_usd'].idxmax()
        
        assert min_idx in cement.index
        assert max_idx in cement.index


# Ejecutar tests si se corre directamente
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov"])
