import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from datetime import datetime


def consolidate_files():
    # Initialize basic tkinter root (hidden)
    root = tk.Tk()
    root.withdraw()

    # 1. Ask for directory
    folder_selected = filedialog.askdirectory(
        title="Selecciona la carpeta con archivos Excel"
    )

    if not folder_selected:
        messagebox.showinfo("Cancelado", "No se seleccionó ninguna carpeta.")
        return

    # 2. Find Excel files
    excel_files = [
        f for f in os.listdir(folder_selected) if f.endswith((".xlsx", ".xls"))
    ]

    if not excel_files:
        messagebox.showwarning(
            "Sin archivos",
            "No se encontraron archivos Excel (.xlsx, .xls) en la carpeta seleccionada.",
        )
        return

    all_data = []
    print(f"Procesando {len(excel_files)} archivos...")

    # 3. Consolidate logic
    for file in excel_files:
        file_path = os.path.join(folder_selected, file)
        try:
            # Read the file
            df = pd.read_excel(file_path)
            # Optional: Add a column for source filename
            df["Archivo_Origen"] = file
            all_data.append(df)
            print(f"Leído: {file}")
        except Exception as e:
            print(f"Error leyendo {file}: {e}")

    if not all_data:
        messagebox.showerror("Error", "No se pudieron extraer datos de los archivos.")
        return

    # Concatenate all dataframes
    consolidated_df = pd.concat(all_data, ignore_index=True)

    # 4. Save logic (Subfolder of script directory)
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create 'consolidated_files' subfolder if it doesn't exist
    output_folder = os.path.join(script_dir, "consolidated_files")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"consolidado_{timestamp}.xlsx"
    output_path = os.path.join(output_folder, output_filename)

    try:
        consolidated_df.to_excel(output_path, index=False)
        messagebox.showinfo(
            "Éxito",
            f"Archivos consolidados correctamente.\n\nGuardado en:\n{output_path}",
        )
        # Open the folder for the user (Windows specific)
        os.startfile(output_folder)
    except Exception as e:
        messagebox.showerror("Error al guardar", f"No se pudo guardar el archivo:\n{e}")


if __name__ == "__main__":
    consolidate_files()
