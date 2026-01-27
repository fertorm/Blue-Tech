import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os


def procesar_datos_mapa(df_subset):
    if df_subset.empty:
        return pd.DataFrame()

    def agg_func(x):
        # Determinar status dominante (Info vs Error)
        # Si hay al menos un 'ok', mostramos Info (Azul). Si todo es error, Error (Rojo).
        statuses = x["status"].unique()
        if "ok" in statuses:
            final_status = "Info"
        else:
            final_status = "Error"

        # Construir resumen HTML de titulares
        titulares_html = []
        # Usamos zip para iterar, asegurándonos de manejar casos donde falten columnas si el csv está corrupto, pero asumimos estructura correcta
        for title, link, stat in zip(
            x["titular"].head(5), x["enlace"].head(5), x["status"]
        ):
            if stat == "error":
                # Resaltar link de error en rojo o con icono
                titulares_html.append(f"⚠️ <span style='color:red'>{title}</span>")
            else:
                titulares_html.append(f"• <a href='{link}'>{title}</a>")

        return pd.Series(
            {
                "titulares_resumen": "<br><br>".join(titulares_html),
                "cantidad_noticias": len(x),
                "status_color": final_status,
            }
        )

    # Agrupar y aplicar lógica
    return (
        df_subset.groupby(["iso_alpha", "pais"])
        .apply(agg_func, include_groups=False)
        .reset_index()
    )


def generar_mapa(df):
    # Asegurar que existan las columnas necesarias (retrocompatibilidad)
    if "category" not in df.columns:
        df["category"] = "General"
    if "status" not in df.columns:
        df["status"] = "ok"

    # Filtrar por categorías
    df_general = df[df["category"] == "General"]
    df_deportes = df[df["category"] == "Deportes"]

    # Procesar subconjuntos
    df_gen_agg = procesar_datos_mapa(df_general)
    df_dep_agg = procesar_datos_mapa(df_deportes)

    # Crear figura base
    fig = go.Figure()

    # Definir mapa de colores
    color_map = {"Info": "#636EFA", "Error": "#EF553B"}  # Azul Plotly, Rojo Plotly

    # --- TRAZAS GENERAL (Visibles por defecto) ---
    traces_general = []
    if not df_gen_agg.empty:
        # Usamos px para generar las trazas fácilmente y luego las añadimos a nuestra fig go
        temp_fig = px.choropleth(
            df_gen_agg,
            locations="iso_alpha",
            color="status_color",
            color_discrete_map=color_map,
            hover_name="pais",
            hover_data={
                "iso_alpha": False,
                "status_color": False,
                "cantidad_noticias": True,
            },
        )
        # Ajustar hovertemplate de las trazas generadas
        temp_fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br><br>Noticias: %{customdata[2]}<br><br>%{customdata[0]}<extra></extra>"
        )
        # Necesitamos pasar los customdata correctos. PX los organiza.
        # Al extraer trazas de PX, 'customdata' ya está seteado.
        # Pero el orden de columnas en customdata depende de hover_data.
        # Verificamos: hover_name=0, iso_alpha(drop), status_color(drop), cantidad_noticias=1, titulares_resumen(manual?)
        # Truco: añadimos titulares_resumen a hover_data para que esté en customdata

        temp_fig = px.choropleth(
            df_gen_agg,
            locations="iso_alpha",
            color="status_color",
            color_discrete_map=color_map,
            hover_name="pais",
            hover_data={
                "iso_alpha": False,
                "status_color": False,
                "titulares_resumen": True,  # customdata[0]
                "cantidad_noticias": True,  # customdata[1]
            },
        )
        temp_fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br><br>Noticias: %{customdata[2]}<br><br>%{customdata[3]}<extra></extra>"
        )

        traces_general = list(temp_fig.data)
        for trace in traces_general:
            trace.visible = True  # Visible por defecto base
            fig.add_trace(trace)

    # --- TRAZAS DEPORTES (Ocultas por defecto) ---
    traces_deportes = []
    if not df_dep_agg.empty:
        temp_fig = px.choropleth(
            df_dep_agg,
            locations="iso_alpha",
            color="status_color",
            color_discrete_map=color_map,
            hover_name="pais",
            hover_data={
                "iso_alpha": False,
                "status_color": False,
                "titulares_resumen": True,
                "cantidad_noticias": True,
            },
        )
        temp_fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br><br>Noticias: %{customdata[2]}<br><br>%{customdata[3]}<extra></extra>"
        )

        traces_deportes = list(temp_fig.data)
        for trace in traces_deportes:
            trace.visible = False  # Oculto por defecto
            fig.add_trace(trace)

    # --- CONFIGURAR LAYOUT Y BOTONES ---
    n_gen = len(traces_general)
    n_dep = len(traces_deportes)

    # Mascaras de visibilidad
    # Si seleccionamos General: [True]*n_gen + [False]*n_dep
    vis_general = [True] * n_gen + [False] * n_dep
    # Si seleccionamos Deportes: [False]*n_gen + [True]*n_dep
    vis_deportes = [False] * n_gen + [True] * n_dep

    fig.update_layout(
        title_text="Monitor de Noticias Globales 2026",
        geo=dict(
            showcountries=True,
            countrycolor="DarkGrey",
            showocean=True,
            oceancolor="LightBlue",
            projection_type="natural earth",
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.5,
                y=1.15,
                xanchor="center",
                yanchor="top",
                buttons=[
                    dict(
                        label="📰 General",
                        method="update",
                        args=[
                            {"visible": vis_general},
                            {"title": "Monitor Global - Noticias Generales"},
                        ],
                    ),
                    dict(
                        label="⚽ Deportes",
                        method="update",
                        args=[
                            {"visible": vis_deportes},
                            {"title": "Monitor Global - Noticias Deportivas"},
                        ],
                    ),
                ],
            )
        ],
    )

    return fig


if __name__ == "__main__":
    csv_path = "data/noticias_mundo.csv"

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
