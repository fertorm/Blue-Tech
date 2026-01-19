import pandas as pd
import plotly.express as px
import os


def generar_mapa(df):
    fig = px.choropleth(
        df,
        locations="iso_alpha",  # Columna con códigos tipo ESP, MEX, ARG
        hover_name="pais",
        hover_data=["titular", "enlace"],  # Mostrar titular y enlace al pasar el mouse
        title="Monitor de Noticias Globales 2026",
        projection="natural earth",
        color_discrete_sequence=["#1f77b4"],  # Color uniforme o basado en volumen
    )

    fig.update_geos(
        showcountries=True,
        countrycolor="DarkGrey",
        showocean=True,
        oceancolor="LightBlue",
    )
    return fig


if __name__ == "__main__":
    csv_path = "noticias_mundo.csv"

    if os.path.exists(csv_path):
        print(f"Cargando datos de {csv_path}...")
        try:
            df = pd.read_csv(csv_path)
            if not df.empty:
                fig = generar_mapa(df)
                fig.show()
                print("Mapa generado y abierto en el navegador.")
            else:
                print("El archivo CSV está vacío.")
        except Exception as e:
            print(f"Error al cargar los datos: {e}")
    else:
        print(
            f"No se encontró el archivo {csv_path}. Ejecuta primero web_scrapper_v3.py"
        )
