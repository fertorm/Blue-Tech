import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import sys
import math

# 1. Cargar datos desde archivo seleccionado por el usuario
print("Iniciando selección de archivo...")
root = tk.Tk()
root.withdraw()  # Ocultar la ventana principal de Tkinter

columna_seleccionada_index = tk.IntVar(value=-1)


file_path = filedialog.askopenfilename(
    title="Seleccione el archivo de datos (CSV o Excel)",
    filetypes=[
        ("Archivos de Datos", "*.csv *.xlsx *.xls"),
        ("Todos los archivos", "*.*"),
    ],
)

if not file_path:
    print("No se seleccionó ningún archivo. Saliendo...")
    sys.exit()

print(f"Leyendo archivo: {file_path}")

try:
    if file_path.endswith(".csv"):
        # Leer CSV
        df = pd.read_csv(file_path)
    else:
        # Leer Excel
        df = pd.read_excel(file_path)

    # Mostrar información de columnas y solicitar selección
    columnas = df.columns.tolist()
    print(f"Archivo cargado. Columnas encontradas ({len(columnas)}):")
    for i, col in enumerate(columnas):
        print(f"{i}: {col}")

    from tkinter import ttk, messagebox

    final_start_row = 0
    final_end_row = len(df)

    # Ventana de selección de columna
    seleccion_window = tk.Toplevel(root)
    seleccion_window.title("Selección de Columna y Vista Previa")
    seleccion_window.geometry("1000x600")

    # Frame principal
    main_frame = tk.Frame(seleccion_window)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- Sección de Selección de Columna (Izquierda) ---
    left_frame = tk.Frame(main_frame, width=300)
    left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

    label = tk.Label(
        left_frame,
        text=f"Archivo cargado.\nColumnas encontradas: {len(columnas)}\n\nSeleccione columna:",
        justify=tk.LEFT,
    )
    label.pack(anchor="w")

    listbox = tk.Listbox(left_frame, selectmode=tk.SINGLE)
    for col in columnas:
        listbox.insert(tk.END, col)
    listbox.pack(fill=tk.BOTH, expand=True, pady=5)

    # --- Sección de Vista Previa de Datos (Derecha) ---
    right_frame = tk.Frame(main_frame)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    preview_label = tk.Label(right_frame, text="Vista Previa (Primeras 15 filas):")
    preview_label.pack(anchor="w")

    # Treeview para mostrar el dataframe
    tree_frame = tk.Frame(right_frame)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    tree_scroll_y = tk.Scrollbar(tree_frame)
    tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    tree_scroll_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
    tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    tree = ttk.Treeview(
        tree_frame, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set
    )
    tree.pack(fill=tk.BOTH, expand=True)

    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)

    # Configurar columnas del Treeview
    tree["columns"] = list(df.columns)
    tree["show"] = "headings tree"  # Mostrar encabezados y la columna #0 (tree)

    # Configurar la columna índice (#0)
    tree.heading("#0", text="Índice")
    tree.column("#0", width=50, anchor="center")

    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="w")

    # Insertar datos (primeras 15 filas)
    df_preview = df.head(15).fillna("")  # Reemplazar NaNs para visualización
    for index, row in df_preview.iterrows():
        tree.insert("", "end", text=str(index), values=list(row))

    # --- Selección de Rango de Filas ---
    range_frame = tk.Frame(left_frame)
    range_frame.pack(fill=tk.X, pady=10)

    tk.Label(range_frame, text="Fila Inicial:").grid(row=0, column=0, sticky="w")
    start_row_var = tk.StringVar(value="0")
    entry_start = tk.Entry(range_frame, textvariable=start_row_var, width=10)
    entry_start.grid(row=0, column=1, padx=5)

    tk.Label(range_frame, text="Fila Final:").grid(row=1, column=0, sticky="w")
    end_row_var = tk.StringVar(value=str(len(df)))
    entry_end = tk.Entry(range_frame, textvariable=end_row_var, width=10)
    entry_end.grid(row=1, column=1, padx=5)

    def on_select():
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning(
                "Atención",
                "Por favor seleccione una columna de la lista de la izquierda.",
            )
            return

        # Validar filas
        try:
            s_row = int(start_row_var.get())
            e_row = int(end_row_var.get())

            if s_row < 0:
                raise ValueError("La fila inicial no puede ser negativa.")
            if e_row > len(df):
                raise ValueError(
                    f"La fila final no puede ser mayor al total de filas ({len(df)})."
                )
            if s_row >= e_row:
                raise ValueError("La fila inicial debe ser menor que la fila final.")

            global final_start_row, final_end_row
            final_start_row = s_row
            final_end_row = e_row

            columna_seleccionada_index.set(selection[0])
            seleccion_window.destroy()
            root.quit()  # Salir del mainloop de Tkinter local

        except ValueError as ve:
            messagebox.showerror("Error en Rango de Filas", str(ve))

    btn = tk.Button(
        left_frame,
        text="Analizar Columna Seleccionada",
        command=on_select,
        bg="#dddddd",
        height=2,
    )
    btn.pack(pady=10, fill=tk.X)

    # Manejar cierre de ventana
    seleccion_window.protocol(
        "WM_DELETE_WINDOW",
        lambda: (
            columna_seleccionada_index.set(-2),
            seleccion_window.destroy(),
            root.quit(),
        ),
    )

    # Esperar selección
    print("Esperando selección de columna por el usuario...")
    root.mainloop()

    idx = columna_seleccionada_index.get()

    if idx == -1:
        # Selección inválida o cerrada sin confirmar (aunque root.quit debería manejarse)
        print(
            "No se seleccionó ninguna columna. Intentando usar la tercera por defecto..."
        )
        if len(columnas) >= 3:
            idx = 2
        else:
            print("No se puede proceder. Saliendo.")
            sys.exit()
    elif idx == -2:
        print("Operación cancelada por el usuario. Saliendo...")
        sys.exit()

    columna_nombre = columnas[idx]
    print(
        f"Analizando columna: '{columna_nombre}' (Filas {final_start_row} a {final_end_row})"
    )

    # Extraer datos con el rango seleccionado
    # Convertir a numérico forzando errores a NaN (por si hay texto como encabezados en las filas)
    datos = pd.to_numeric(
        df.iloc[final_start_row:final_end_row, idx], errors="coerce"
    ).to_numpy()

    # Filtrar valores no numéricos si los hubiera (limpieza básica)
    datos = datos[~np.isnan(datos)]

except Exception as e:
    print(f"Error al leer el archivo: {e}")
    sys.exit()

muestras = np.arange(1, len(datos) + 1)

# 2. Cálculos Estadísticos (Rigor Científico)
media = np.mean(datos)
desviacion = np.std(datos)
limite_inferior = 230  # Umbral de seguridad

# 3. Predicción Simple (Media Móvil de los últimos 3 días)
prediccion_dia_16 = np.mean(datos[-3:])

# 4. Generación del Reporte Visual
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))

# --- Gráfico 1: Serie de Tiempo ---
ax1.plot(
    muestras, datos, marker="o", linestyle="-", color="blue", label="Resistencia Real"
)

# Líneas de referencia
ax1.axhline(media, color="green", linestyle="--", label=f"Promedio: {media:.2f} kg/cm²")
ax1.axhline(
    limite_inferior, color="red", linestyle=":", label="Límite Crítico (230 kg/cm²)"
)

# Graficar la predicción
ax1.scatter(
    16,
    prediccion_dia_16,
    color="orange",
    s=100,
    label=f"Predicción Día 16: {prediccion_dia_16:.2f}",
    zorder=5,
)

# Estética y Etiquetas del Gráfico 1
ax1.set_title("Reporte de Calidad de Materiales - Proyecto Blue Tech", fontsize=14)
ax1.set_xlabel("Número de Muestra / Día", fontsize=12)
ax1.set_ylabel("Resistencia (kg/cm²)", fontsize=12)
ax1.grid(True, alpha=0.3)
ax1.legend()

# --- Gráfico 2: Histograma y Curva de Gauss ---
# Histograma
count, bins, ignored = ax2.hist(
    datos,
    bins="auto",
    density=True,
    alpha=0.6,
    color="skyblue",
    edgecolor="black",
    label="Frecuencia Observada",
)

# Cálculos adicionales para el gráfico
mediana = np.median(datos)
# Moda aproximada (punto medio del bin con mayor frecuencia)
hist_vals, bin_edges = np.histogram(datos, bins="auto")
max_idx = np.argmax(hist_vals)
moda = (bin_edges[max_idx] + bin_edges[max_idx + 1]) / 2

# Curva de Gauss
xmin, xmax = ax2.get_xlim()
x = np.linspace(xmin, xmax, 100)
p = (1 / (np.sqrt(2 * np.pi) * desviacion)) * np.exp(
    -0.5 * ((x - media) / desviacion) ** 2
)

ax2.plot(
    x,
    p,
    "r-",
    linewidth=2,
    label=r"Curva Gaussiana ($\mu$={:.2f}, $\sigma$={:.2f})".format(media, desviacion),
)

# Líneas de tendencia central
ax2.axvline(
    media, color="green", linestyle="--", linewidth=2, label=f"Media: {media:.2f}"
)
ax2.axvline(
    mediana,
    color="purple",
    linestyle="-.",
    linewidth=2,
    label=f"Mediana: {mediana:.2f}",
)
ax2.axvline(
    moda, color="gold", linestyle=":", linewidth=2, label=f"Moda (aprox): {moda:.2f}"
)

# Probabilidad de Falla (Área bajo la curva < Límite Inferior)
# Usando función de error para CDF de distribución normal


z_score = (limite_inferior - media) / desviacion
prob_falla = 0.5 * (1 + math.erf(z_score / math.sqrt(2)))
prob_falla_porcentaje = prob_falla * 100

# Sombrear área de falla
x_falla = np.linspace(xmin, limite_inferior, 100)
p_falla = (1 / (np.sqrt(2 * np.pi) * desviacion)) * np.exp(
    -0.5 * ((x_falla - media) / desviacion) ** 2
)
ax2.fill_between(
    x_falla,
    p_falla,
    color="red",
    alpha=0.3,
    label=f"Prob. Falla: {prob_falla_porcentaje:.2f}%",
)
ax2.axvline(limite_inferior, color="red", linestyle=":", linewidth=1)

# Estética y Etiquetas del Gráfico 2
ax2.set_title("Distribución de Resistencias y Curva Normal", fontsize=14)
ax2.set_xlabel("Resistencia (kg/cm²)", fontsize=12)
ax2.set_ylabel("Densidad de Probabilidad", fontsize=12)
ax2.grid(True, alpha=0.3)
ax2.legend(loc="upper right", fontsize=9)

plt.tight_layout()
plt.show()

print(f"--- Análisis Final ---")
print(f"Desviación Estándar (Sigma): {desviacion:.2f}")
print(f"Nivel de variabilidad: {'Bajo' if desviacion < 15 else 'Alto'}")
