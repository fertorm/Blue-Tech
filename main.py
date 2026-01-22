import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys


class MainLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Blue Tech - Suite Principal")
        self.root.geometry("400x300")

        self.setup_ui()

    def setup_ui(self):
        tk.Label(
            self.root, text="🚀 Blue Tech Launcher", font=("Arial", 20, "bold")
        ).pack(pady=20)

        tk.Button(
            self.root,
            text="🕵️ Abrir Scraper",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            width=20,
            command=self.open_scraper,
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="📊 Abrir Dashboard",
            font=("Arial", 12),
            bg="#FF9800",
            fg="white",
            width=20,
            command=self.open_dashboard,
        ).pack(pady=10)

        tk.Label(
            self.root, text="v1.0 - Sistema Integrado", font=("Arial", 8), fg="gray"
        ).pack(side=tk.BOTTOM, pady=10)

    def open_scraper(self):
        try:
            # Asume que scraper_runner.py está en el mismo directorio
            subprocess.Popen([sys.executable, "scraper_runner.py"])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el Scraper: {e}")

    def open_dashboard(self):
        try:
            # Streamlit corre como un script module o ejecutable
            # Intentamos ejecutarlo como modulo de python
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el Dashboard: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainLauncher(root)
    root.mainloop()
