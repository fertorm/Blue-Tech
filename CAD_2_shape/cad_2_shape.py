import ezdxf
import geopandas as gpd
from shapely.geometry import Polygon
import tkinter as tk
from tkinter import filedialog
import os


def dxf_a_geojson(archivo_entrada, archivo_salida):
    # 1. Cargar el DXF
    doc = ezdxf.readfile(archivo_entrada)
    msp = doc.modelspace()

    poligonos = []
    nombres = []

    # 2. Filtrar solo polilíneas cerradas
    for entity in msp.query("LWPOLYLINE"):
        if entity.closed:
            # Extraer puntos (x, y)
            puntos = [(p[0], p[1]) for p in entity.get_points()]
            poligonos.append(Polygon(puntos))
            # Usar la capa como ID para vincular con Power BI
            nombres.append(entity.dxf.layer)

    # 3. Crear el GeoDataFrame
    gdf = gpd.GeoDataFrame({"ID_Obra": nombres, "geometry": poligonos})

    # 4. Guardar como GeoJSON (que luego puedes pasar a TopoJSON)
    gdf.to_file(archivo_salida, driver="GeoJSON")
    print(f"Éxito: {archivo_salida} generado con {len(poligonos)} elementos.")


def seleccionar_archivo_y_procesar():
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal

    print("Por favor, seleccione el archivo DXF de entrada.")
    archivo_entrada = filedialog.askopenfilename(
        title="Seleccionar archivo DXF",
        filetypes=[("Archivos DXF", "*.dxf"), ("Todos los archivos", "*.*")],
    )

    if not archivo_entrada:
        print("No se seleccionó ningún archivo. Operación cancelada.")
        return

    # Sugerir nombre de salida basado en el de entrada
    nombre_base = os.path.splitext(archivo_entrada)[0]
    archivo_salida_sugerido = f"{nombre_base}.geojson"

    print("Por favor, seleccione dónde guardar el archivo GeoJSON.")
    archivo_salida = filedialog.asksaveasfilename(
        title="Guardar archivo GeoJSON",
        initialfile=os.path.basename(archivo_salida_sugerido),
        defaultextension=".geojson",
        filetypes=[("Archivos GeoJSON", "*.geojson"), ("Todos los archivos", "*.*")],
    )

    if not archivo_salida:
        print("No se seleccionó destino. Operación cancelada.")
        return

    dxf_a_geojson(archivo_entrada, archivo_salida)


if __name__ == "__main__":
    seleccionar_archivo_y_procesar()
