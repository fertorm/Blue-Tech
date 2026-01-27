"""
Material Price Dashboard
========================

Este módulo proporciona un dashboard interactivo para visualizar
precios de materiales de construcción a nivel global.

Características:
- Visualización en mapa mundial
- Comparación entre países
- Conversión automática a USD
- Filtros dinámicos

Uso:
    streamlit run material_dashboard.py

Autor: Blue Tech
Fecha: Enero 2026
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import logging
from datetime import datetime

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Configuration ---
st.set_page_config(
    page_title="Global Construction Materials Dashboard",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Constants ---
DATA_FILE = "data/material_prices.csv"

# ISO-3 Code Mapping (Expandido y corregido)
COUNTRY_MAPPING = {
    "Bolivia": "BOL",
    "Santa Cruz": "BOL",
    "Brasil": "BRA",
    "Brazil": "BRA",
    "Argentina": "ARG",
    "Chile": "CHL",
    "Peru": "PER",
    "Perú": "PER",
    "China": "CHN",
    "USA": "USA",
    "United States": "USA",
    "Estados Unidos": "USA",
    "Paraguay": "PRY",
    "Russia": "RUS",
    "Rusia": "RUS",
    "India": "IND",
    "Europe": "EUR",
    "Europa": "EUR",
    "Global": "GLO",
    "Mexico": "MEX",
    "México": "MEX",
    "Colombia": "COL",
    "Ecuador": "ECU",
    "Uruguay": "URY",
    "Venezuela": "VEN",
}

# Approximate Exchange Rates to USD (Enero 2026 - Actualizadas)
EXCHANGE_RATES = {
    "USD": 1.0,
    "BOB": 0.145,      # 1 BOB = ~0.145 USD (aprox 6.90 BOB/USD)
    "CNY": 0.138,      # 1 CNY = ~0.138 USD
    "BRL": 0.20,       # 1 BRL = ~0.20 USD
    "ARS": 0.001,      # Alta volatilidad - verificar regularmente
    "RUB": 0.010,      # 1 RUB = ~0.010 USD
    "INR": 0.012,      # 1 INR = ~0.012 USD
    "EUR": 1.10,       # 1 EUR = ~1.10 USD
    "CLP": 0.0011,     # Peso Chileno
    "PEN": 0.27,       # Sol Peruano
    "PYG": 0.00013,    # Guaraní Paraguayo
    "MXN": 0.058,      # Peso Mexicano
    "COP": 0.00025,    # Peso Colombiano
}


# --- Helper Functions ---
@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_data():
    """
    Carga y procesa los datos de precios de materiales.
    
    Returns:
        pd.DataFrame: DataFrame con los datos procesados o vacío si hay error
    """
    try:
        if not os.path.exists(DATA_FILE):
            st.error(
                f"❌ Archivo de datos no encontrado en {DATA_FILE}. "
                f"Por favor ejecuta el script de scraping primero."
            )
            logger.error(f"Data file not found: {DATA_FILE}")
            return pd.DataFrame()

        df = pd.read_csv(DATA_FILE)
        logger.info(f"Data loaded successfully: {len(df)} records")

        # Validar que el DataFrame no esté vacío
        if df.empty:
            st.warning("⚠️ El archivo de datos está vacío.")
            return pd.DataFrame()

        # Asegurar que price sea numérico
        if "price" in df.columns:
            df["price"] = pd.to_numeric(df["price"], errors="coerce")
            df = df.dropna(subset=["price"])
            
            # Validar precios positivos
            df = df[df["price"] > 0]
            logger.info(f"Valid prices after cleaning: {len(df)} records")

        # Agregar Country ID (ISO-3)
        if "country" in df.columns:
            df["country_id"] = df["country"].map(COUNTRY_MAPPING)
            
            # Registrar países sin mapeo
            unmapped = df[df["country_id"].isna()]["country"].unique()
            if len(unmapped) > 0:
                logger.warning(f"Unmapped countries: {unmapped}")
                df["country_id"] = df["country_id"].fillna("UNK")

        # Validar campos requeridos
        required_fields = ["material", "country", "price", "currency", "unit"]
        missing_fields = [field for field in required_fields if field not in df.columns]
        if missing_fields:
            st.error(f"❌ Campos faltantes en los datos: {missing_fields}")
            logger.error(f"Missing required fields: {missing_fields}")
            return pd.DataFrame()

        return df

    except Exception as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
        logger.error(f"Error loading data: {str(e)}", exc_info=True)
        return pd.DataFrame()


def convert_to_usd(row):
    """
    Convierte el precio a USD usando las tasas de cambio definidas.
    
    Args:
        row: Fila del DataFrame con 'price' y 'currency'
        
    Returns:
        float: Precio convertido a USD o None si hay error
    """
    try:
        # Validar datos
        if pd.isna(row["price"]) or pd.isna(row["currency"]):
            logger.warning(f"Invalid price or currency in row: {row}")
            return None
        
        currency = row["currency"].strip().upper()
        
        # Obtener tasa de cambio
        rate = EXCHANGE_RATES.get(currency)
        
        if rate is None:
            if currency != "USD":
                logger.warning(f"Unknown currency: {currency}. Assuming USD.")
            rate = 1.0
        
        return row["price"] * rate
        
    except Exception as e:
        logger.error(f"Error converting to USD: {e}")
        return None


def format_currency(value, currency="USD"):
    """Formatea valores monetarios de manera consistente"""
    if pd.isna(value):
        return "N/A"
    return f"${value:,.2f} {currency}"


def get_statistics(df):
    """Calcula estadísticas descriptivas del DataFrame"""
    if df.empty:
        return {}
    
    return {
        "total_records": len(df),
        "unique_materials": df["material"].nunique(),
        "unique_countries": df["country"].nunique(),
        "avg_price_usd": df["price_usd"].mean(),
        "min_price_usd": df["price_usd"].min(),
        "max_price_usd": df["price_usd"].max(),
    }


# --- Main App ---
def main():
    """Función principal del dashboard"""
    
    # Header
    st.title("🏗️ Construction Material Prices Tracker")
    st.markdown("### Análisis Global de Precios de Materiales de Construcción")
    st.markdown("---")

    # 1. Load Data
    with st.spinner("Cargando datos..."):
        df = load_data()
    
    if df.empty:
        st.info("💡 **Consejo:** Ejecuta el script `material_scraper.py` para recolectar datos.")
        return

    # Add USD Normalized Price
    df["price_usd"] = df.apply(convert_to_usd, axis=1)
    df = df.dropna(subset=["price_usd"])  # Eliminar conversiones fallidas

    if df.empty:
        st.error("❌ No se pudieron convertir los precios a USD.")
        return

    # 2. Sidebar Filters
    st.sidebar.header("🔍 Filtros")
    
    # Estadísticas generales en sidebar
    with st.sidebar.expander("📊 Estadísticas Generales", expanded=False):
        stats = get_statistics(df)
        st.metric("Total de Registros", f"{stats['total_records']:,}")
        st.metric("Materiales Únicos", stats['unique_materials'])
        st.metric("Países Cubiertos", stats['unique_countries'])

    # Material Filter
    available_materials = sorted(df["material"].unique())
    selected_material = st.sidebar.selectbox(
        "Seleccionar Material",
        available_materials,
        index=0,
        help="Elige el material que deseas analizar"
    )

    # Filter Data by Material
    df_filtered = df[df["material"] == selected_material].copy()

    # Country Filter
    available_countries = sorted(df_filtered["country"].unique())
    selected_countries = st.sidebar.multiselect(
        "Seleccionar Países",
        available_countries,
        default=available_countries,
        help="Filtra por uno o más países específicos"
    )

    if selected_countries:
        df_filtered = df_filtered[df_filtered["country"].isin(selected_countries)]

    # Currency Filter (opcional)
    show_original_currency = st.sidebar.checkbox(
        "Mostrar precios originales",
        value=False,
        help="Muestra los precios en su moneda original además de USD"
    )

    # Validar datos filtrados
    if df_filtered.empty:
        st.warning("⚠️ No hay datos disponibles para los filtros seleccionados.")
        return

    # 3. KPIs
    st.subheader("📈 Indicadores Clave")
    
    avg_price = df_filtered["price_usd"].mean()
    min_price_row = df_filtered.loc[df_filtered["price_usd"].idxmin()]
    max_price_row = df_filtered.loc[df_filtered["price_usd"].idxmax()]
    
    # Obtener unidad (asumiendo consistencia por material)
    unit = df_filtered["unit"].mode()[0] if not df_filtered["unit"].empty else "unit"

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Precio Promedio Global",
            format_currency(avg_price),
            help=f"Precio promedio por {unit}"
        )
    
    with col2:
        st.metric(
            "Mercado Más Económico",
            f"{min_price_row['country']}",
            format_currency(min_price_row['price_usd']),
            delta=f"ISO: {min_price_row['country_id']}",
            help=f"Precio más bajo encontrado por {unit}"
        )
    
    with col3:
        st.metric(
            "Mercado Más Costoso",
            f"{max_price_row['country']}",
            format_currency(max_price_row['price_usd']),
            delta=f"ISO: {max_price_row['country_id']}",
            help=f"Precio más alto encontrado por {unit}"
        )

    st.markdown("---")

    # 4. Visualizations
    st.subheader(f"🗺️ Distribución Global de Precios: {selected_material}")

    # Mapa Choropleth
    fig_map = px.choropleth(
        df_filtered,
        locations="country_id",
        locationmode="ISO-3",
        color="price_usd",
        hover_name="country",
        hover_data={
            "country_id": True,
            "price": ":,.2f",
            "currency": True,
            "price_usd": ":,.2f",
            "unit": True,
        },
        labels={"price_usd": "Precio (USD)"},
        color_continuous_scale="Blues",
        title=f"Intensidad de Precio (USD) - {selected_material}",
        projection="natural earth",
    )
    
    fig_map.update_geos(
        showcountries=True,
        countrycolor="lightgray",
        showcoastlines=True,
        coastlinecolor="gray"
    )
    
    fig_map.update_layout(
        height=500,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    st.plotly_chart(fig_map, use_container_width=True)

    # 5. Comparación por País
    st.markdown("---")
    col_chart, col_table = st.columns([2, 1])

    with col_chart:
        st.subheader("📊 Comparación de Precios por País")
        
        # Ordenar por precio
        df_sorted = df_filtered.sort_values("price_usd", ascending=True)
        
        fig_bar = px.bar(
            df_sorted,
            x="price_usd",
            y="country",
            orientation='h',
            color="price_usd",
            text="country_id",
            title=f"Precio por {unit} en USD",
            labels={"price_usd": "Precio USD", "country": "País"},
            color_continuous_scale="Blues",
        )
        
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(
            showlegend=False,
            height=max(400, len(df_sorted) * 40)
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_table:
        st.subheader("📋 Datos Detallados")
        
        # Preparar datos para mostrar
        display_df = df_filtered[
            ["country", "country_id", "price", "currency", "price_usd", "unit", "source"]
        ].copy()
        
        display_df = display_df.sort_values("price_usd")
        display_df["price"] = display_df["price"].map("{:,.2f}".format)
        display_df["price_usd"] = display_df["price_usd"].map("${:,.2f}".format)
        
        # Renombrar columnas para mejor presentación
        display_df.columns = ["País", "ISO-3", "Precio", "Moneda", "Precio USD", "Unidad", "Fuente"]
        
        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True
        )
        
        # Botón de descarga
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f"{selected_material}_prices_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

    # 6. Análisis de Variación
    st.markdown("---")
    st.subheader("📉 Análisis de Variación de Precios")
    
    col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
    
    with col_stats1:
        st.metric("Desviación Estándar", f"${df_filtered['price_usd'].std():,.2f}")
    
    with col_stats2:
        st.metric("Rango", f"${df_filtered['price_usd'].max() - df_filtered['price_usd'].min():,.2f}")
    
    with col_stats3:
        coef_var = (df_filtered['price_usd'].std() / df_filtered['price_usd'].mean()) * 100
        st.metric("Coef. Variación", f"{coef_var:.1f}%")
    
    with col_stats4:
        st.metric("Mediana", f"${df_filtered['price_usd'].median():,.2f}")

    # Box plot para visualizar distribución
    fig_box = px.box(
        df_filtered,
        y="price_usd",
        x="country",
        title="Distribución de Precios por País",
        labels={"price_usd": "Precio USD", "country": "País"}
    )
    
    fig_box.update_layout(showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

    # 7. Información de Fuentes
    st.markdown("---")
    with st.expander("ℹ️ Información de Fuentes de Datos"):
        sources_df = df_filtered[["source", "country"]].drop_duplicates()
        st.write("**Fuentes utilizadas en esta consulta:**")
        st.dataframe(sources_df, hide_index=True)
        
        if "extraction_date" in df_filtered.columns:
            latest_date = df_filtered["extraction_date"].max()
            st.info(f"📅 Última actualización: {latest_date}")

    # 8. Raw Data Section
    with st.expander("🔍 Ver Todos los Datos Crudos"):
        st.dataframe(df, use_container_width=True)
        
        # Descarga de todos los datos
        csv_all = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Todos los Datos",
            data=csv_all,
            file_name=f"all_material_prices_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
            <p>🏗️ <strong>Blue Tech Construction Materials Dashboard</strong> | 
            Desarrollado con Streamlit y Plotly | 
            © 2026</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    import sys
    from streamlit.web import cli as stcli

    if st.runtime.exists():
        main()
    else:
        # Auto-relaunch con streamlit
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
