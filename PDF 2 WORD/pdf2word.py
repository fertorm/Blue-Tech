from pdf2docx import Converter
import os


def convertir_pdf_a_word(ruta_pdf, ruta_docx=None, start=0, end=None):
    # Si no se especifica ruta de salida, usar el mismo nombre
    if ruta_docx is None:
        ruta_docx = ruta_pdf.replace(".pdf", ".docx")

    # Verificar que el PDF existe
    if not os.path.exists(ruta_pdf):
        print(f"Error: El archivo {ruta_pdf} no existe")
        return False

    try:
        # Convertir
        cv = Converter(ruta_pdf)
        cv.convert(ruta_docx, start=start, end=end)
        cv.close()
        print(f"Conversión exitosa: {ruta_docx}")
        return True
    except Exception as e:
        print(f"Error durante la conversión: {e}")
        return False


# Usar la función
if __name__ == "__main__":
    import tkinter as tk
    from tkinter import filedialog, messagebox

    def ask_page_range(parent):
        """
        Muestra un diálogo personalizado para seleccionar rango de páginas.
        Retorna (start, end) o (None, None) si se cancela.
        """
        dialog = tk.Toplevel(parent)
        dialog.title("Rango de Páginas")
        dialog.geometry("300x150")

        # Variables para guardar resultados
        result = {"start": 0, "end": None, "confirmed": False}

        tk.Label(dialog, text="Página Inicio (0 para primera):").pack(pady=5)
        entry_start = tk.Entry(dialog)
        entry_start.insert(0, "0")
        entry_start.pack(pady=5)

        tk.Label(dialog, text="Página Fin (vacío o 0 para final):").pack(pady=5)
        entry_end = tk.Entry(dialog)
        entry_end.insert(0, "0")
        entry_end.pack(pady=5)

        def on_confirm():
            try:
                s = entry_start.get().strip()
                e = entry_end.get().strip()

                start_val = int(s) if s else 0
                end_val = int(e) if e else 0

                if end_val == 0:
                    end_val = None

                result["start"] = start_val
                result["end"] = end_val
                result["confirmed"] = True
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Por favor ingrese números válidos.")

        btn = tk.Button(dialog, text="Convertir", command=on_confirm)
        btn.pack(pady=10)

        # Hacer modal
        # No usamos transient porque el padre (root) está oculto y ocultaría también esta ventana
        # dialog.transient(parent)
        dialog.grab_set()
        dialog.focus_force()  # Asegurar que tenga el foco
        parent.wait_window(dialog)

        return result

    # Crear ventana raíz oculta
    root = tk.Tk()
    root.withdraw()

    print("Por favor seleccione el archivo PDF a convertir...")

    # Abrir diálogo de selección
    ruta_seleccionada = filedialog.askopenfilename(
        title="Seleccionar archivo PDF", filetypes=[("Archivos PDF", "*.pdf")]
    )

    if ruta_seleccionada:
        # Preguntar por rango de páginas con diálogo personalizado
        # Necesitamos mostrar root temporalmente o usarlo como padre
        rango = ask_page_range(root)

        if rango["confirmed"]:
            print(f"Iniciando conversión: Inicio={rango['start']}, Fin={rango['end']}")
            convertir_pdf_a_word(
                ruta_seleccionada, start=rango["start"], end=rango["end"]
            )
        else:
            print("Conversión cancelada por el usuario.")
    else:
        print("No se seleccionó ningún archivo.")
