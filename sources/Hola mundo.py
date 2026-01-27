import csv


def obtener_datos():
    texto_base = "  Hola Mundo desde Python  "
    texto_limpio = texto_base.strip()

    # Lista de diccionarios con la información de cada ejemplo
    datos = [
        # --- 1. Transformación ---
        {
            "Categoria": "Transformación",
            "Metodo": "upper()",
            "Codigo": "texto_base.upper()",
            "Descripcion": "Todo mayúsculas",
            "Resultado": texto_base.upper(),
        },
        {
            "Categoria": "Transformación",
            "Metodo": "lower()",
            "Codigo": "texto_base.lower()",
            "Descripcion": "Todo minúsculas",
            "Resultado": texto_base.lower(),
        },
        {
            "Categoria": "Transformación",
            "Metodo": "capitalize()",
            "Codigo": "texto_base.strip().capitalize()",
            "Descripcion": "Primera letra mayúscula",
            "Resultado": texto_base.strip().capitalize(),
        },
        {
            "Categoria": "Transformación",
            "Metodo": "title()",
            "Codigo": "texto_base.title()",
            "Descripcion": "Primera letra de cada palabra mayúscula",
            "Resultado": texto_base.title(),
        },
        {
            "Categoria": "Transformación",
            "Metodo": "swapcase()",
            "Codigo": "texto_base.swapcase()",
            "Descripcion": "Invierte mayúsculas/minúsculas",
            "Resultado": texto_base.swapcase(),
        },
        # --- 2. Limpieza ---
        {
            "Categoria": "Limpieza",
            "Metodo": "strip()",
            "Codigo": "texto_base.strip()",
            "Descripcion": "Quita espacios inicio y fin",
            "Resultado": texto_base.strip(),
        },
        {
            "Categoria": "Limpieza",
            "Metodo": "lstrip()",
            "Codigo": "texto_base.lstrip()",
            "Descripcion": "Quita espacios izquierda",
            "Resultado": texto_base.lstrip(),
        },
        {
            "Categoria": "Limpieza",
            "Metodo": "rstrip()",
            "Codigo": "texto_base.rstrip()",
            "Descripcion": "Quita espacios derecha",
            "Resultado": texto_base.rstrip(),
        },
        # --- 3. Búsqueda y Reemplazo ---
        {
            "Categoria": "Búsqueda/Reemplazo",
            "Metodo": "find()",
            "Codigo": "texto_limpio.find('Mundo')",
            "Descripcion": "Índice donde empieza (-1 si no existe)",
            "Resultado": texto_limpio.find("Mundo"),
        },
        {
            "Categoria": "Búsqueda/Reemplazo",
            "Metodo": "index()",
            "Codigo": "texto_limpio.index('Mundo')",
            "Descripcion": "Similar a find (error si no existe)",
            "Resultado": texto_limpio.index("Mundo"),
        },
        {
            "Categoria": "Búsqueda/Reemplazo",
            "Metodo": "replace()",
            "Codigo": "texto_limpio.replace('Python', 'Blue Tech')",
            "Descripcion": "Reemplaza texto",
            "Resultado": texto_limpio.replace("Python", "Blue Tech"),
        },
        {
            "Categoria": "Búsqueda/Reemplazo",
            "Metodo": "count()",
            "Codigo": "texto_limpio.count('o')",
            "Descripcion": "Cuenta ocurrencias de 'o'",
            "Resultado": texto_limpio.count("o"),
        },
        {
            "Categoria": "Búsqueda/Reemplazo",
            "Metodo": "startswith()",
            "Codigo": "texto_limpio.startswith('Hola')",
            "Descripcion": "Empieza con...",
            "Resultado": texto_limpio.startswith("Hola"),
        },
        {
            "Categoria": "Búsqueda/Reemplazo",
            "Metodo": "endswith()",
            "Codigo": "texto_limpio.endswith('Python')",
            "Descripcion": "Termina con...",
            "Resultado": texto_limpio.endswith("Python"),
        },
        # --- 4. División y Unión ---
        {
            "Categoria": "División/Unión",
            "Metodo": "split()",
            "Codigo": "texto_limpio.split()",
            "Descripcion": "Divide string por espacios",
            "Resultado": str(texto_limpio.split()),
        },
        {
            "Categoria": "División/Unión",
            "Metodo": "split('o')",
            "Codigo": "texto_limpio.split('o')",
            "Descripcion": "Divide usando 'o' como separador",
            "Resultado": str(texto_limpio.split("o")),
        },
        {
            "Categoria": "División/Unión",
            "Metodo": "join()",
            "Codigo": "'-'.join(lista)",
            "Descripcion": "Une lista con conector",
            "Resultado": "-".join(texto_limpio.split()),
        },
        # --- 5. Verificación ---
        {
            "Categoria": "Verificación",
            "Metodo": "isdigit()",
            "Codigo": "'123'.isdigit()",
            "Descripcion": "Es número?",
            "Resultado": "123".isdigit(),
        },
        {
            "Categoria": "Verificación",
            "Metodo": "isalpha()",
            "Codigo": "'Hola'.isalpha()",
            "Descripcion": "Solo letras?",
            "Resultado": "Hola".isalpha(),
        },
        {
            "Categoria": "Verificación",
            "Metodo": "isalnum()",
            "Codigo": "'Hola123'.isalnum()",
            "Descripcion": "Letras o números?",
            "Resultado": "Hola123".isalnum(),
        },
        {
            "Categoria": "Verificación",
            "Metodo": "islower()",
            "Codigo": "'hola'.islower()",
            "Descripcion": "Todo minúsculas?",
            "Resultado": "hola".islower(),
        },
        {
            "Categoria": "Verificación",
            "Metodo": "isupper()",
            "Codigo": "'HOLA'.isupper()",
            "Descripcion": "Todo mayúsculas?",
            "Resultado": "HOLA".isupper(),
        },
        # --- Extra ---
        {
            "Categoria": "Extra",
            "Metodo": "len()",
            "Codigo": "len(texto_limpio)",
            "Descripcion": "Longitud del string",
            "Resultado": len(texto_limpio),
        },
    ]
    return datos


def mostrar_ejemplos():
    datos = obtener_datos()
    print(
        f"Texto original usado en la mayoría de ejemplos: '  Hola Mundo desde Python  '\n"
    )

    categoria_actual = ""
    for item in datos:
        if item["Categoria"] != categoria_actual:
            print(f"\n--- {item['Categoria']} ---")
            categoria_actual = item["Categoria"]

        print(f"{item['Metodo']}: {item['Resultado']} ({item['Descripcion']})")


def generar_csv_ejemplos():
    datos = obtener_datos()
    nombre_archivo = "ejemplos_strings.csv"

    with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as archivo_csv:
        columnas = ["Categoria", "Metodo", "Codigo", "Descripcion", "Resultado"]
        writer = csv.DictWriter(archivo_csv, fieldnames=columnas)

        writer.writeheader()
        writer.writerows(datos)

    print(f"\n[Éxito] Archivo '{nombre_archivo}' generado correctamente.")


if __name__ == "__main__":
    mostrar_ejemplos()
    generar_csv_ejemplos()
