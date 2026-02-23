import os
from PIL import Image


def partir_hoja_stickers(ruta_hoja, carpeta_salida, filas=4, columnas=5):
    """
    Divide la hoja de stickers en archivos individuales y ajusta el tamaño
    automáticamente al contenido (autocrop).
    """
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    # Abrir la imagen manteniendo la transparencia (RGBA)
    img = Image.open(ruta_hoja).convert("RGBA")
    ancho, alto = img.size

    # Calcular tamaño teórico de cada celda
    ancho_celda = ancho // columnas
    alto_celda = alto // filas

    # Nombres exactos según tus constantes del código
    nombres = [
        "1-verde-hoja",
        "2-naranja-atardecer",
        "3-morado-uva",
        "4-celeste-cielo",
        "5-rosado-pastel",
        "6-gris-humo",
        "7-azul-noche",
        "8-marron-tierra",
        "9-turquesa-bosque",
        "10-verde-oliva",
        "11-azul-marino",
        "12-celeste-glaciar",
        "13-turquesa-tropical",
        "14-violeta-medusa",
        "15-rosa-coral",
        "16-naranja-nemo",
        "17-verde-alga",
        "18-gris-perla",
        "19-oro-pirata",
        "20-azul-abisal",
    ]

    index = 0
    for f in range(filas):
        for c in range(columnas):
            if index >= len(nombres):
                break

            # Definir el área de recorte de la celda
            izquierda = c * ancho_celda
            superior = f * alto_celda
            derecha = izquierda + ancho_celda
            inferior = superior + alto_celda

            # Recortar la celda
            sticker = img.crop((izquierda, superior, derecha, inferior))

            # AUTOCROP: Elimina el espacio transparente sobrante alrededor del objeto
            bbox = sticker.getbbox()
            if bbox:
                sticker = sticker.crop(bbox)

            # Guardar con el nombre correspondiente
            nombre_archivo = f"sticker-lvl{nombres[index]}.png"
            ruta_final = os.path.join(carpeta_salida, nombre_archivo)

            # Redimensionar a un tamaño estándar para la app (ej: 256x256) manteniendo aspecto
            sticker.thumbnail((256, 256), Image.Resampling.LANCZOS)

            sticker.save(ruta_final, "PNG")
            print(f"✅ Procesado: {nombre_archivo}")
            index += 1


# --- EJECUCIÓN ---
# Asegúrate de que el nombre del archivo coincida con el tuyo
partir_hoja_stickers("hoja_stickers.png", "assets/stickers")
