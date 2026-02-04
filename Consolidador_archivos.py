import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os


class ConsolidadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Consolidador de Archivos Excel/CSV")
        self.root.geometry("600x500")

        self.input_files = []
        self.output_path = tk.StringVar()
        self.start_row_var = tk.StringVar(value="0")
        self.end_row_var = tk.StringVar(value="")  # Empty implies all rows

        self.setup_ui()

    def setup_ui(self):
        # Main Container
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 1. File Selection Section ---
        file_frame = tk.LabelFrame(main_frame, text="1. Archivos de Entrada")
        file_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        btn_add = tk.Button(
            file_frame, text="Agregar Archivos", command=self.add_files, bg="#e1e1e1"
        )
        btn_add.pack(side=tk.LEFT, padx=5, pady=5)

        btn_preview = tk.Button(
            file_frame,
            text="Visualizar Archivo",
            command=self.preview_file,
            bg="#d1e7dd",
        )
        btn_preview.pack(side=tk.LEFT, padx=5, pady=5)

        self.file_listbox = tk.Listbox(file_frame, selectmode=tk.EXTENDED, height=8)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=(40, 5))
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        btn_clear = tk.Button(
            file_frame, text="Limpiar Lista", command=self.clear_files, bg="#ffdddd"
        )
        btn_clear.pack(anchor="e", padx=5, pady=5)

        # --- 2. Configuration Section ---
        config_frame = tk.LabelFrame(main_frame, text="2. Configuración")
        config_frame.pack(fill=tk.X, pady=(0, 10))

        # Row Range Grid
        range_frame = tk.Frame(config_frame)
        range_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(range_frame, text="Fila Inicial (0-based):").grid(
            row=0, column=0, sticky="w", padx=5
        )
        tk.Entry(range_frame, textvariable=self.start_row_var, width=10).grid(
            row=0, column=1, padx=5
        )

        tk.Label(range_frame, text="Fila Final (Opcional):").grid(
            row=0, column=2, sticky="w", padx=5
        )
        tk.Entry(range_frame, textvariable=self.end_row_var, width=10).grid(
            row=0, column=3, padx=5
        )

        tk.Label(range_frame, text="(Dejar vacío para leer hasta el final)").grid(
            row=0, column=4, sticky="w", padx=5, columnspan=2
        )

        # Output Path
        out_frame = tk.Frame(config_frame)
        out_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(out_frame, text="Archivo de Salida:").pack(side=tk.LEFT, padx=5)
        tk.Entry(out_frame, textvariable=self.output_path).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=5
        )
        tk.Button(out_frame, text="Examinar...", command=self.browse_output).pack(
            side=tk.LEFT, padx=5
        )

        # --- 3. Action Section ---
        action_frame = tk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)

        self.progress = ttk.Progressbar(
            action_frame, orient=tk.HORIZONTAL, length=100, mode="determinate"
        )
        self.progress.pack(fill=tk.X, pady=(0, 10))

        btn_consolidate = tk.Button(
            action_frame,
            text="CONSOLIDAR ARCHIVOS",
            command=self.consolidate,
            bg="#4caf50",
            fg="white",
            font=("Arial", 10, "bold"),
            height=2,
        )
        btn_consolidate.pack(fill=tk.X)

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos",
            filetypes=[
                ("Excel/CSV Files", "*.xlsx *.xls *.csv"),
                ("Todos los archivos", "*.*"),
            ],
        )
        for f in files:
            if f not in self.input_files:
                self.input_files.append(f)
                self.file_listbox.insert(tk.END, f)

    def clear_files(self):
        self.input_files = []
        self.file_listbox.delete(0, tk.END)

    def browse_output(self):
        f = filedialog.asksaveasfilename(
            title="Guardar archivo consolidado como...",
            defaultextension=".xlsx",
            initialdir="data",
            filetypes=[("Excel File", "*.xlsx"), ("CSV File", "*.csv")],
        )
        if f:
            self.output_path.set(f)

    def preview_file(self):
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning(
                "Aviso", "Seleccione un archivo de la lista para visualizar."
            )
            return

        file_path = self.input_files[selection[0]]

        try:
            # Read first 50 rows without header to show raw structure
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".csv":
                df_preview = pd.read_csv(file_path, header=None, nrows=50)
            elif ext in [".xlsx", ".xls"]:
                df_preview = pd.read_excel(file_path, header=None, nrows=50)
            else:
                messagebox.showerror(
                    "Error", "Formato no soportado para previsualización."
                )
                return

            # --- Preview Window ---
            top = tk.Toplevel(self.root)
            top.title(f"Vista Previa: {os.path.basename(file_path)}")
            top.geometry("800x600")

            # Instructions
            tk.Label(
                top,
                text="Use esta vista para identificar la 'Fila Inicial' (donde están los encabezados).",
                bg="#ffffcc",
                pady=5,
            ).pack(fill=tk.X)

            # Treeview
            tree_frame = tk.Frame(top)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            tree = ttk.Treeview(tree_frame)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            vsb.pack(side=tk.RIGHT, fill=tk.Y)
            tree.configure(yscrollcommand=vsb.set)

            # Columns (Phantom column #0 for Index, plus columns for data)
            # Create generic column names 0, 1, 2...
            columns = [str(i) for i in range(len(df_preview.columns))]
            tree["columns"] = columns
            tree["show"] = "headings tree"  # Show #0

            tree.heading("#0", text="Fila Index")
            tree.column("#0", width=80, anchor="center")

            for col in columns:
                tree.heading(col, text=f"Col {col}")
                tree.column(col, width=100)

            # Insert Data
            # Replace NaN with empty string
            df_preview = df_preview.fillna("")
            for idx, row in df_preview.iterrows():
                tree.insert("", "end", text=str(idx), values=list(row))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo visualizar el archivo:\n{e}")

    def preview_file_dummy(self):
        return  # dummy to allow replace logic if needed, but not needed here.

    def consolidate(self):
        if not self.input_files:
            messagebox.showwarning("Aviso", "No hay archivos para consolidar.")
            return

        out_file = self.output_path.get()
        if not out_file:
            messagebox.showwarning("Aviso", "Por favor seleccione una ruta de salida.")
            return

        # Parse Range
        try:
            start_row = int(self.start_row_var.get())
            end_row_str = self.end_row_var.get().strip()
            end_row = int(end_row_str) if end_row_str else None
        except ValueError:
            messagebox.showerror(
                "Error", "Los rangos de fila deben ser números enteros."
            )
            return

        dataframes = []
        self.progress["maximum"] = len(self.input_files)
        self.progress["value"] = 0

        try:
            for i, file_path in enumerate(self.input_files):
                ext = os.path.splitext(file_path)[1].lower()

                # Determine how many rows to read
                # pandas 'nrows' parameter reads 'n' rows. It is not an end index.
                # If end_row is specified, nrows = end_row - start_row
                nrows = None
                if end_row is not None:
                    if end_row <= start_row:
                        raise ValueError(
                            f"La fila final ({end_row}) debe ser mayor a la inicial ({start_row})."
                        )
                    nrows = end_row - start_row

                if ext == ".csv":
                    df = pd.read_csv(
                        file_path, header=start_row, nrows=nrows
                    )  # using header=start_row to act as skip
                    # Note: header argument in pandas defines which row is header.
                    # If we simply want to skip rows and assume next is header, we use 'header' parameter appropriately.
                    # Or 'skiprows'. Let's assume standard behavior:
                    # User says "Start Row 5". This usually means Row 5 is the header or data starts there.
                    # Let's interpret Start Row as the 0-indexed row number where the HEADER is located.
                    # Data follows immediately.
                    # Creating a generic reader:
                    df = pd.read_csv(file_path, header=start_row, nrows=nrows)

                elif ext in [".xlsx", ".xls"]:
                    df = pd.read_excel(file_path, header=start_row, nrows=nrows)

                else:
                    print(f"Formato no soportado saltado: {file_path}")
                    continue

                # Add a column identifying the source file (optional but useful)
                df["Fuente_Archivo"] = os.path.basename(file_path)

                dataframes.append(df)

                self.progress["value"] = i + 1
                self.root.update_idletasks()

            if not dataframes:
                messagebox.showerror(
                    "Error", "No se pudieron leer datos de los archivos seleccionados."
                )
                return

            # Concatenate
            full_df = pd.concat(dataframes, ignore_index=True)

            # Save
            if out_file.lower().endswith(".csv"):
                full_df.to_csv(out_file, index=False)
            else:
                full_df.to_excel(out_file, index=False)

            messagebox.showinfo(
                "Éxito",
                f"Consolidación completada.\nGuardado en: {out_file}\nTotal filas: {len(full_df)}",
            )
            self.progress["value"] = 0

        except Exception as e:
            messagebox.showerror(
                "Error Crítico", f"Ocurrió un error durante la consolidación:\n{str(e)}"
            )
            self.progress["value"] = 0


if __name__ == "__main__":
    root = tk.Tk()
    app = ConsolidadorApp(root)
    root.mainloop()
