import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import numpy as np


def quitar_fondo(ruta_imagen):
    """
    Toma una imagen, convierte el fondo blanco (o casi blanco) en transparente
    y guarda la nueva imagen en la misma carpeta con el sufijo '_sin_fondo'.
    """
    try:
        print(f"Procesando: {ruta_imagen}")

        # 1. Cargar imagen y convertir a RGBA
        img = Image.open(ruta_imagen).convert("RGBA")
        img_np = np.array(img)

        # 2. Definir qué es "blanco" (umbral ajustable)
        # Píxeles con R, G, y B mayores a 230 se consideran fondo
        r, g, b, a = img_np.T
        areas_blancas = (r > 230) & (g > 230) & (b > 230)

        # 3. Hacer transparentes esos píxeles (Alpha = 0)
        img_np[..., 3][areas_blancas.T] = 0

        # 4. Crear imagen final
        img_final = Image.fromarray(img_np)

        # 5. Generar nombre de archivo de salida
        carpeta = os.path.dirname(ruta_imagen)
        nombre_archivo = os.path.basename(ruta_imagen)
        nombre_base, _ = os.path.splitext(nombre_archivo)

        nombre_salida = f"{nombre_base}_sin_fondo.png"
        ruta_salida = os.path.join(carpeta, nombre_salida)

        # 6. Guardar
        img_final.save(ruta_salida, "PNG")
        print(f"✅ Imagen guardada en: {ruta_salida}")

    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")


if __name__ == "__main__":
    # Configuración de Tkinter para no mostrar ventana principal
    root = tk.Tk()
    root.withdraw()

    print("Por favor, selecciona una imagen...")
    ruta_input = filedialog.askopenfilename(
        title="Selecciona una imagen para quitar el fondo",
        filetypes=[
            ("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp;*.webp"),
            ("Todos los archivos", "*.*"),
        ],
    )

    if ruta_input:
        quitar_fondo(ruta_input)
        input("\nPresiona Enter para salir...")
    else:
        print("Operación cancelada.")
