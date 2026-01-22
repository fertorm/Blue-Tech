import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
# Configuración de la página
st.set_page_config(page_title="Blue Tech Dashboard", layout="wide")

st.title("🏗️ Blue Tech: Monitor de Precios en Bolivia")
st.markdown("Análisis de costos de materiales de construcción y escolares.")

# Cargar datos
try:
    df = pd.read_excel("Base_Datos_BlueTech.xlsx")

    # Pre-procesamiento básico
    if "Fecha_Consulta" in df.columns:
        df["Fecha_Consulta"] = pd.to_datetime(df["Fecha_Consulta"]).dt.date

    # Tabs para organizar la vista
    tab1, tab2 = st.tabs(["📊 Análisis General", "⚖️ Comparador de Precios"])

    # --- TAB 1: ANÁLISIS GENERAL (Lógica Original Mejorada) ---
    with tab1:
        st.header("Explorador de Datos")

        # --- FILTROS LATERALES (Solo afectan a esta tab si se desea,
        # pero streamlit sidebar es global. Lo mantenemos global para Tab 1 principalmente)
        st.sidebar.header("Filtros Globales")

        # Asegurarnos de que las columnas existen
        if "Fuente" in df.columns and "Material" in df.columns:
            fuente = st.sidebar.multiselect(
                "Seleccionar Fuente:",
                options=df["Fuente"].unique(),
                default=df["Fuente"].unique(),
            )

            # Filtrar df por fuente
            df_source_filtered = df[df["Fuente"].isin(fuente)]

            # Selector de material (dependiente de la fuente)
            materialES = df_source_filtered["Material"].unique().tolist()
            if materialES:
                material = st.selectbox(
                    "Seleccionar Material para Detalle:", options=materialES, index=0
                )

                df_filtrado = df[
                    (df["Fuente"].isin(fuente)) & (df["Material"] == material)
                ]

                # --- MÉTRICAS CLAVE ---
                col1, col2, col3 = st.columns(3)

                if "Precio_BS" in df_filtrado.columns and not df_filtrado.empty:
                    precio_promedio = df_filtrado["Precio_BS"].mean()
                    precio_max = df_filtrado["Precio_BS"].max()
                    precio_min = df_filtrado["Precio_BS"].min()

                    col1.metric("Precio Promedio", f"Bs. {precio_promedio:.2f}")
                    col2.metric("Precio Mínimo", f"Bs. {precio_min:.2f}")
                    col3.metric("Precio Máximo", f"Bs. {precio_max:.2f}")

                    # --- GRÁFICOS ---
                    st.subheader(f"Evolución: {material}")
                    if "Fecha_Consulta" in df_filtrado.columns:
                        fig = px.line(
                            df_filtrado.sort_values("Fecha_Consulta"),
                            x="Fecha_Consulta",
                            y="Precio_BS",
                            color="Fuente",
                            markers=True,
                            title="Histórico de Precios",
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No hay datos para la selección actual.")
            else:
                st.warning(
                    "No hay materiales disponibles para las fuentes seleccionadas."
                )
        else:
            st.warning("El archivo Excel no tiene la estructura esperada.")

    # --- TAB 2: COMPARADOR DE PRECIOS ---
    with tab2:
        st.header("🔎 Comparador por Búsqueda")
        st.markdown(
            "Busca un producto (ej. 'Cuaderno') para comparar precios entre todas las tiendas."
        )

        search_term = st.text_input("Buscar producto:", "")

        if search_term:
            # Filtrar por texto (case insensitive)
            mask = df["Material"].str.contains(search_term, case=False, na=False)
            df_search = df[mask]

            if not df_search.empty:
                st.success(
                    f"Se encontraron {len(df_search)} resultados para '{search_term}'."
                )

                # Top 5 más baratos
                st.subheader("🏆 Top 5 Opciones Más Económicas")
                df_cheapest = df_search.nsmallest(5, "Precio_BS")[
                    ["Fuente", "Material", "Precio_BS", "Fecha_Consulta"]
                ]
                st.table(df_cheapest)

                # Gráfico Comparativo (Boxplot para ver rangos de precios por tienda)
                st.subheader("📊 Distribución de Precios por Tienda")
                fig_box = px.box(
                    df_search,
                    x="Fuente",
                    y="Precio_BS",
                    color="Fuente",
                    points="all",
                    title=f"Rango de Precios para '{search_term}'",
                    hover_data=["Material"],
                )
                st.plotly_chart(fig_box, use_container_width=True)

                # Tabla completa
                with st.expander("Ver todos los resultados"):
                    st.dataframe(
                        df_search[["Fuente", "Material", "Precio_BS", "Fecha_Consulta"]]
                    )
            else:
                st.warning("No se encontraron productos que coincidan con la búsqueda.")

except FileNotFoundError:
    st.error("No se encontró 'Base_Datos_BlueTech.xlsx'. Ejecuta primero el Scraper.")
except Exception as e:
    st.error(f"Error cargando datos: {e}")
