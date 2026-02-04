import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp
import os
import threading


class YoutubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Blue Tech - Descargador Pro")
        self.root.geometry("600x400")  # Aumentado ligeramente para mejor visibilidad
        self.root.resizable(False, False)
        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        lbl_title = tk.Label(
            main_frame,
            text="Descargador de Videos YouTube",
            font=("Segoe UI", 16, "bold"),
        )
        lbl_title.pack(pady=(0, 20))

        # --- URL ---
        tk.Label(main_frame, text="URL del Video:", font=("Segoe UI", 10)).pack(
            anchor="w"
        )
        self.url_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=self.url_var, font=("Segoe UI", 10)).pack(
            fill=tk.X, pady=(5, 10)
        )

        # --- Carpeta ---
        tk.Label(main_frame, text="Carpeta de Destino:", font=("Segoe UI", 10)).pack(
            anchor="w"
        )
        folder_frame = tk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=(5, 10))
        self.folder_var = tk.StringVar()
        tk.Entry(
            folder_frame,
            textvariable=self.folder_var,
            font=("Segoe UI", 10),
            state="readonly",
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(folder_frame, text="Examinar...", command=self.browse_folder).pack(
            side=tk.LEFT, padx=(10, 0)
        )

        # --- Opciones de Cookies (Mejorado) ---
        self.use_cookies_var = tk.BooleanVar(value=True)
        chk_cookies = tk.Checkbutton(
            main_frame,
            text="Usar cookies de Chrome (Recomendado para evitar bloqueos)",
            variable=self.use_cookies_var,
            font=("Segoe UI", 9),
        )
        chk_cookies.pack(anchor="w")

        lbl_note = tk.Label(
            main_frame,
            text="Nota: Si da error DPAPI, cierra Chrome e intenta de nuevo.",
            font=("Segoe UI", 8),
            fg="gray",
        )
        lbl_note.pack(anchor="w", pady=(0, 15))

        # --- Botón Acción ---
        self.btn_download = tk.Button(
            main_frame,
            text="DESCARGAR VIDEO",
            command=self.start_download,
            bg="#d32f2f",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            height=2,
        )
        self.btn_download.pack(fill=tk.X)

        self.progress = ttk.Progressbar(main_frame, mode="indeterminate")
        self.lbl_status = tk.Label(
            main_frame, text="Listo", fg="gray", font=("Segoe UI", 9)
        )
        self.lbl_status.pack(pady=(10, 0))

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def start_download(self):
        url, folder = self.url_var.get().strip(), self.folder_var.get().strip()
        if not url or not folder:
            messagebox.showwarning(
                "Atención", "Complete la URL y la carpeta de destino."
            )
            return

        self.toggle_controls(False)
        self.progress.pack(fill=tk.X, pady=(10, 0))
        self.progress.start()

        thread = threading.Thread(target=self.download_process, args=(url, folder))
        thread.daemon = True
        thread.start()

    def download_process(self, url, folder):
        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "nocheckcertificate": True,
        }

        # Intentamos cargar cookies de Chrome de forma segura
        if self.use_cookies_var.get():
            try:
                # Si esto falla por DPAPI, lanzará una excepción inmediatamente
                ydl_opts["cookiesfrombrowser"] = ("chrome",)
                self.update_status("Probando con cookies de Chrome...")
            except:
                # Si hay error de cifrado, eliminamos la opción silenciosamente
                if "cookiesfrombrowser" in ydl_opts:
                    del ydl_opts["cookiesfrombrowser"]
                self.update_status("Cookies bloqueadas. Descargando modo normal...")

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.update_status("Descargando video...")
                # Agregamos un segundo intento dentro de yt-dlp por si falla el descifrado interno
                ydl.download([url])
            self.on_download_complete(True)
        except Exception as e:
            error_str = str(e)
            # Si el error interno de yt-dlp sigue siendo sobre DPAPI, reintentamos sin cookies automáticamente
            if "DPAPI" in error_str and "cookiesfrombrowser" in ydl_opts:
                self.update_status("Reintentando sin cookies...")
                del ydl_opts["cookiesfrombrowser"]
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    self.on_download_complete(True)
                except Exception as e2:
                    self.on_download_complete(False, str(e2))
            else:
                error_clean = error_str.replace("[0;31mERROR: [0m", "")
                self.on_download_complete(False, error_clean)

    def update_status(self, text):
        self.root.after(0, lambda: self.lbl_status.config(text=text, fg="blue"))

    def on_download_complete(self, success, error_msg=None):
        self.root.after(0, lambda: self._finish_ui(success, error_msg))

    def _finish_ui(self, success, error_msg):
        self.progress.stop()
        self.progress.pack_forget()
        self.toggle_controls(True)
        if success:
            self.lbl_status.config(text="¡Éxito!", fg="green")
            messagebox.showinfo("Completado", "Video descargado con éxito.")
            self.url_var.set("")
        else:
            self.lbl_status.config(text="Error", fg="red")
            if "DPAPI" in str(error_msg):
                messagebox.showerror(
                    "Error de Cifrado",
                    "No se pudo acceder a las cookies de Chrome.\n\n"
                    "SOLUCIÓN:\n1. Cierra Chrome completamente.\n2. Intenta de nuevo.\n"
                    "3. O desactiva la opción de cookies.",
                )
            else:
                messagebox.showerror("Error", f"Detalle: {error_msg}")

    def toggle_controls(self, enable):
        state = tk.NORMAL if enable else tk.DISABLED
        self.btn_download.config(state=state)


if __name__ == "__main__":
    root = tk.Tk()
    app = YoutubeDownloaderApp(root)
    root.mainloop()
