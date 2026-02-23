import os
import cv2
import numpy as np
from PIL import Image
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox


class GridConfigDialog(tk.Toplevel):
    def __init__(
        self, parent, total_width, total_height, default_rows=5, default_cols=5
    ):
        super().__init__(parent)
        self.title("Configuración de Cuadrícula")
        self.total_width = total_width
        self.total_height = total_height

        self.rows_var = tk.IntVar(value=default_rows)
        self.cols_var = tk.IntVar(value=default_cols)

        self.row_heights = []
        self.col_widths = []
        self.result = None

        self.create_widgets()

    def create_widgets(self):
        # Frame superior: Número de filas y columnas
        config_frame = tk.Frame(self)
        config_frame.pack(padx=10, pady=10)

        tk.Label(config_frame, text="Filas:").grid(row=0, column=0)
        tk.Entry(config_frame, textvariable=self.rows_var, width=5).grid(
            row=0, column=1
        )

        tk.Label(config_frame, text="Columnas:").grid(row=0, column=2)
        tk.Entry(config_frame, textvariable=self.cols_var, width=5).grid(
            row=0, column=3
        )

        tk.Button(
            config_frame, text="Generar Configuración", command=self.generate_inputs
        ).grid(row=0, column=4, padx=10)

        # Frame para las dimensiones (scrollable si es necesario, pero simple por ahora)
        self.inputs_frame = tk.Frame(self)
        self.inputs_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Botón procesar
        tk.Button(
            self,
            text="Procesar Imagen",
            command=self.on_process,
            bg="green",
            fg="white",
        ).pack(pady=10)

        # Generar inputs iniciales
        self.generate_inputs()

    def generate_inputs(self):
        # Limpiar frame anterior
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()

        rows = self.rows_var.get()
        cols = self.cols_var.get()

        # Calcular defaults
        default_h = self.total_height // rows
        default_w = self.total_width // cols

        # Inputs de filas
        row_frame = tk.LabelFrame(
            self.inputs_frame, text=f"Alturas de Filas (Total: {self.total_height}px)"
        )
        row_frame.pack(side="left", fill="both", expand=True, padx=5)

        self.row_entries = []
        for i in range(rows):
            f = tk.Frame(row_frame)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=f"Fila {i+1}:").pack(side="left")
            e = tk.Entry(f, width=8)
            e.insert(0, str(default_h))
            e.pack(side="right")
            self.row_entries.append(e)

        # Inputs de columnas
        col_frame = tk.LabelFrame(
            self.inputs_frame, text=f"Anchos de Columnas (Total: {self.total_width}px)"
        )
        col_frame.pack(side="right", fill="both", expand=True, padx=5)

        self.col_entries = []
        for i in range(cols):
            f = tk.Frame(col_frame)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=f"Col {i+1}:").pack(side="left")
            e = tk.Entry(f, width=8)
            e.insert(0, str(default_w))
            e.pack(side="right")
            self.col_entries.append(e)

    def on_process(self):
        try:
            r_heights = [int(e.get()) for e in self.row_entries]
            c_widths = [int(e.get()) for e in self.col_entries]

            # Validar totales (advertencia si no coinciden)
            if sum(r_heights) != self.total_height:
                if not messagebox.askyesno(
                    "Advertencia",
                    f"La suma de alturas ({sum(r_heights)}) no coincide con el total ({self.total_height}). ¿Continuar?",
                ):
                    return

            if sum(c_widths) != self.total_width:
                if not messagebox.askyesno(
                    "Advertencia",
                    f"La suma de anchos ({sum(c_widths)}) no coincide con el total ({self.total_width}). ¿Continuar?",
                ):
                    return

            self.result = (r_heights, c_widths)
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa números válidos.")


def procesar_stickers_custom(
    ruta_imagen_original, carpeta_salida, row_heights, col_widths
):
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    print(f"Procesando: {ruta_imagen_original}")

    img_pil = Image.open(ruta_imagen_original).convert("RGBA")
    img_np = np.array(img_pil)

    # Eliminar fondo blanco
    r, g, b, a = img_np.T
    white_areas = (r > 230) & (g > 230) & (b > 230)
    img_np[..., 3][white_areas.T] = 0

    img_final = Image.fromarray(img_np)

    nombres_stickers = [
        "verde-hoja",
        "naranja-atardecer",
        "morado-uva",
        "celeste-cielo",
        "rosado-pastel",
        "gris-humo",
        "azul-noche",
        "marron-tierra",
        "turquesa-bosque",
        "verde-oliva",
        "azul-marino",
        "celeste-glaciar",
        "turquesa-tropical",
        "violeta-medusa",
        "rosa-coral",
        "naranja-nemo",
        "verde-alga",
        "gris-perla",
        "oro-pirata",
        "azul-abisal",
    ]

    count = 0
    current_y = 0

    for f, h_cell in enumerate(row_heights):
        current_x = 0
        for c, w_cell in enumerate(col_widths):

            left = current_x
            top = current_y
            right = current_x + w_cell
            bottom = current_y + h_cell

            # Asegurar que no nos salimos de la imagen
            right = min(right, img_pil.width)
            bottom = min(bottom, img_pil.height)

            cell_img = img_final.crop((left, top, right, bottom))
            bbox = cell_img.getbbox()

            if bbox:
                # Filtro de ruido mínimo
                if bbox[2] - bbox[0] > 10 and bbox[3] - bbox[1] > 10:
                    sticker_crop = cell_img.crop(bbox)

                    if count < len(nombres_stickers):
                        nombre_base = nombres_stickers[count]
                    else:
                        nombre_base = f"sticker_extra_{count+1}"

                    nombre_archivo = f"lvl{count+1}-{nombre_base}.png"
                    ruta_salida = os.path.join(carpeta_salida, nombre_archivo)
                    sticker_crop.save(ruta_salida, "PNG")
                    print(
                        f"✅ Guardado: {nombre_archivo} (Grid: {f},{c} | Size: {sticker_crop.width}x{sticker_crop.height})"
                    )
                else:
                    print(f"⚠️ Celda con ruido ignorada en ({f},{c}).")
            else:
                print(f"⚠️ Celda vacía en ({f},{c}).")

            count += 1
            current_x += w_cell

        current_y += h_cell

    print(f"Procesados {count} stickers.")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    print("Selecciona la imagen de la hoja de stickers...")
    ruta_archivo = filedialog.askopenfilename(
        title="Selecciona la hoja de stickers",
        filetypes=[
            ("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp"),
            ("Todos los archivos", "*.*"),
        ],
    )

    if ruta_archivo:
        # Obtener dimensiones
        img_temp = Image.open(ruta_archivo)
        total_w, total_h = img_temp.size

        # Lanzar dialogo de configuración
        dialog = GridConfigDialog(
            root, total_w, total_h, default_rows=5, default_cols=5
        )
        root.wait_window(dialog)

        if dialog.result:
            r_heights, c_widths = dialog.result
            procesar_stickers_custom(
                ruta_archivo, "assets/stickers", r_heights, c_widths
            )
            print("\n✅ Proceso completado.")
        else:
            print("❌ Configuración cancelada.")
    else:
        print("❌ No se seleccionó ningún archivo.")

    root.quit()
