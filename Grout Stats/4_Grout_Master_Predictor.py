import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from sklearn.linear_model import LinearRegression
import os


class GroutApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Blue Tech - Predictor SikaGrout 9400")
        self.root.geometry("400x450")
        self.model = None
        self.b_growth = 0

        # --- Interfaz ---
        tk.Label(
            root, text="Panel de Control Estadístico", font=("Arial", 14, "bold")
        ).pack(pady=10)

        self.btn_load = tk.Button(
            root,
            text="1. Cargar 'master_data_grout.csv'",
            command=self.load_and_train,
            bg="#4CAF50",
            fg="white",
        )
        self.btn_load.pack(pady=10)

        self.status_label = tk.Label(root, text="Estado: Esperando datos...", fg="red")
        self.status_label.pack()

        self.frame_pred = tk.LabelFrame(
            root, text=" Estimación a 28 Días ", padx=10, pady=10
        )
        self.frame_pred.pack(pady=20, padx=20, fill="both")

        tk.Label(self.frame_pred, text="Resistencia Medida (MPa):").grid(
            row=0, column=0, sticky="w"
        )
        self.entry_mpa = tk.Entry(self.frame_pred, state="disabled")
        self.entry_mpa.grid(row=0, column=1, pady=5)

        tk.Label(self.frame_pred, text="Edad de la rotura (Días):").grid(
            row=1, column=0, sticky="w"
        )
        self.entry_age = tk.Entry(self.frame_pred, state="disabled")
        self.entry_age.grid(row=1, column=1, pady=5)

        self.btn_predict = tk.Button(
            self.frame_pred,
            text="Calcular Predicción",
            command=self.predict,
            state="disabled",
            bg="#2196F3",
            fg="white",
        )
        self.btn_predict.grid(row=2, columnspan=2, pady=10)

        self.result_label = tk.Label(
            root, text="", font=("Arial", 11, "bold"), fg="blue"
        )
        self.result_label.pack()

    def load_and_train(self):
        # Buscamos directamente el archivo maestro que ya tiene los nombres limpios
        file_path = filedialog.askopenfilename(
            title="Seleccione master_data_grout.csv", filetypes=[("CSV files", "*.csv")]
        )
        if not file_path:
            return

        try:
            # LEER CON LOS NOMBRES DE COLUMNA CORRECTOS
            master_df = pd.read_csv(file_path)

            # Corregimos los nombres de las columnas según tu master_data_grout.csv
            # 'Edad_Dias' y 'Resistencia_MPa'
            X = np.log(master_df[["Edad_Dias"]]).values
            y = master_df["Resistencia_MPa"].values

            self.model = LinearRegression()
            self.model.fit(X, y)
            self.b_growth = self.model.coef_[0]

            self.status_label.config(
                text=f"Estado: Modelo Entrenado (n={len(master_df)})", fg="green"
            )
            self.entry_mpa.config(state="normal")
            self.entry_age.config(state="normal")
            self.btn_predict.config(state="normal")
            messagebox.showinfo("Éxito", "Modelo entrenado correctamente.")

        except KeyError as e:
            messagebox.showerror(
                "Error de Columnas",
                f"No se encontró la columna: {e}\nAsegúrese de usar 'master_data_grout.csv'",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")

    def predict(self):
        try:
            m_now = float(self.entry_mpa.get())
            t_now = float(self.entry_age.get())
            # Proyección logarítmica
            pred_28d = m_now + self.b_growth * (np.log(28) - np.log(t_now))
            status = "✅ CUMPLE" if pred_28d >= 110 else "⚠️ RIESGO"
            self.result_label.config(
                text=f"Proyección a 28d: {pred_28d:.2f} MPa\n[{status}]"
            )
        except:
            messagebox.showwarning("Atención", "Ingrese números válidos.")


if __name__ == "__main__":
    root = tk.Tk()
    app = GroutApp(root)
    root.mainloop()
