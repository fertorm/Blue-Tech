import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
from bs4 import BeautifulSoup
import threading
import datetime
from datetime import datetime
import random
from database_manager import DatabaseManager


class ScraperLogic:
    def __init__(self, log_callback):
        self.log = log_callback
        self.db = DatabaseManager()

    def scrape_tailoy(self, url):
        self.log(f"Iniciando scrapeo de Tailoy: {url}")
        headers = {"User-Agent": "Mozilla/5.0"}
        data_batch = []
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")
            products = soup.select(".product-item")

            for product in products:
                try:
                    title = product.select_one(".product-item-link").get_text(
                        strip=True
                    )
                    price_elem = product.select_one(
                        '[data-price-type="finalPrice"] .price'
                    ) or product.select_one(".price")
                    price_txt = price_elem.get_text(strip=True) if price_elem else "0"

                    price_val = self.db.clean_price(price_txt, decimal_separator=".")

                    data_batch.append(
                        {
                            "Fuente": "Tailoy",
                            "Material": title,
                            "Precio_BS": price_val,
                            "Fecha_Consulta": datetime.now().strftime("%Y-%m-%d"),
                        }
                    )
                except Exception:
                    continue
            return data_batch
        except Exception as e:
            self.log(f"Error en Tailoy: {e}")
            return []

    def scrape_libreria_brasil(
        self, url="https://libreriabrasil.com/categoria-producto/escolar/"
    ):
        self.log(f"Iniciando scrapeo de Libreria Brasil: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        data_batch = []
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")
            products = soup.select("li.product")

            for product in products:
                try:
                    title_elem = product.select_one(".woocommerce-loop-product__title")
                    title = (
                        title_elem.get_text(strip=True) if title_elem else "Sin Nombre"
                    )

                    price_elem = product.select_one(".price")
                    price_txt = price_elem.get_text(strip=True) if price_elem else "0"

                    # Limpieza extra para 'Bs.' que a veces viene pegado
                    price_txt = price_txt.replace("Bs.", "").replace("Bs", "").strip()

                    price_val = self.db.clean_price(price_txt, decimal_separator=",")

                    data_batch.append(
                        {
                            "Fuente": "Libreria Brasil",
                            "Material": title,
                            "Precio_BS": price_val,
                            "Fecha_Consulta": datetime.now().strftime("%Y-%m-%d"),
                        }
                    )
                except Exception:
                    continue
            return data_batch
        except Exception as e:
            self.log(f"Error en Libreria Brasil: {e}")
            return []

    def scrape_materiales_bo(
        self, url="https://materiales.com.bo/collections/utiles-escolares"
    ):
        self.log(f"Iniciando scrapeo de Materiales BO: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        data_batch = []
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")
            products = soup.select(".main_box")

            for product in products:
                try:
                    title_elem = product.select_one(".desc h5 a")
                    title = (
                        title_elem.get_text(strip=True) if title_elem else "Sin Nombre"
                    )

                    # Intentar buscar .money primero, si no, usar .price completo
                    price_elem = product.select_one(".price .money")
                    if not price_elem:
                        price_elem = product.select_one(".price")

                    price_txt = price_elem.get_text(strip=True) if price_elem else "0"

                    # Limpieza preliminar (el resto lo hace database_manager)
                    price_txt = price_txt.replace("Desde", "").strip()

                    price_val = self.db.clean_price(price_txt, decimal_separator=",")

                    data_batch.append(
                        {
                            "Fuente": "Materiales BO",
                            "Material": title,
                            "Precio_BS": price_val,
                            "Fecha_Consulta": datetime.now().strftime("%Y-%m-%d"),
                        }
                    )
                except Exception:
                    continue
            return data_batch
        except Exception as e:
            self.log(f"Error en Materiales BO: {e}")
            return []


class ScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scraper App - Blue Tech")
        self.root.geometry("800x600")

        self.logic = ScraperLogic(self.log)
        self.is_running = False

        self.setup_ui()

    def setup_ui(self):
        lbl_title = tk.Label(
            self.root, text="🕵️ Scraper de Precios", font=("Arial", 16, "bold")
        )
        lbl_title.pack(pady=10)

        frame_controls = tk.Frame(self.root)
        frame_controls.pack(pady=10)

        self.var_tailoy = tk.BooleanVar(value=True)
        self.var_brasil = tk.BooleanVar(value=True)
        self.var_mat_bo = tk.BooleanVar(value=True)

        chk_tailoy = tk.Checkbutton(
            frame_controls, text="Tailoy", variable=self.var_tailoy
        )
        chk_brasil = tk.Checkbutton(
            frame_controls, text="Libreria Brasil", variable=self.var_brasil
        )
        chk_mat_bo = tk.Checkbutton(
            frame_controls, text="Materiales BO", variable=self.var_mat_bo
        )

        chk_tailoy.pack(side=tk.LEFT, padx=10)
        chk_brasil.pack(side=tk.LEFT, padx=10)
        chk_mat_bo.pack(side=tk.LEFT, padx=10)

        self.btn_start = tk.Button(
            self.root,
            text="▶ Iniciar Scraping",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12),
            command=self.start_thread,
        )
        self.btn_start.pack(pady=10)

        self.log_area = scrolledtext.ScrolledText(self.root, height=15)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def log(self, msg):
        self.root.after(0, lambda: self._safe_log(msg))

    def _safe_log(self, msg):
        self.log_area.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_area.see(tk.END)

    def start_thread(self):
        if self.is_running:
            return
        self.is_running = True
        self.btn_start.config(state=tk.DISABLED)
        threading.Thread(target=self.run_process, daemon=True).start()

    def run_process(self):
        all_data = []

        if self.var_tailoy.get():
            data = self.logic.scrape_tailoy("https://www.tailoy.com.bo/escolar.html")
            all_data.extend(data)
            self.log(f"Tailoy: {len(data)} items encontrados.")

        if self.var_brasil.get():
            data = self.logic.scrape_libreria_brasil()
            all_data.extend(data)
            self.log(f"Libreria Brasil: {len(data)} items encontrados.")

        if self.var_mat_bo.get():
            data = self.logic.scrape_materiales_bo()
            all_data.extend(data)
            self.log(f"Materiales BO: {len(data)} items encontrados.")

        if all_data:
            success, msg = self.logic.db.save_data(all_data)
            self.log(f"Guardado: {msg}")
        else:
            self.log("No se recolectaron datos.")

        self.is_running = False
        self.root.after(0, lambda: self.btn_start.config(state=tk.NORMAL))


if __name__ == "__main__":
    root = tk.Tk()
    app = ScraperApp(root)
    root.mainloop()
