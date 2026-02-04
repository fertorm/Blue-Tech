import os
import sys
import ctypes

# --- PATCH FOR PYTHON 3.14 COMPATIBILITY ---
if sys.version_info >= (3, 13):  # Applying for 3.13+ just in case, or definitely 3.14
    _original_CDLL = ctypes.CDLL

    class SafeCDLL(_original_CDLL):
        def __init__(
            self,
            name,
            mode=0,
            handle=None,
            use_errno=False,
            use_last_error=False,
            winmode=None,
        ):
            # Intercept CDLL(None) which fails on Py3.14
            if name is None and handle is None:
                if sys.platform == "win32":
                    try:
                        # Get handle to current process
                        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
                        handle = k32.GetModuleHandleW(None)
                        name = "kernel32"  # Dummy name to satisfy validation
                    except:
                        pass

            # If we fixed the handle, ensure we pass a string name
            if name is None and handle is not None:
                name = "kernel32"

            super().__init__(name, mode, handle, use_errno, use_last_error, winmode)

    ctypes.CDLL = SafeCDLL
# -------------------------------------------
import whisper
import json
import subprocess
from pathlib import Path
from datetime import timedelta
import google.generativeai as genai
import time
from google.api_core import exceptions
from dotenv import load_dotenv

# --- SETUP ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("❌ ERROR: GOOGLE_API_KEY no encontrada en .env")
    print("Por favor, configura tu API key en el archivo .env")
    sys.exit(1)

genai.configure(api_key=GOOGLE_API_KEY)


class PodcastApp:
    def __init__(self, model_size=None):
        # Load config from .env
        self.download_path = Path(os.getenv("DOWNLOAD_PATH", "./downloads"))
        model_size = model_size or os.getenv("WHISPER_MODEL", "base")

        print(f"--- Inicializando Motores (IA: Gemini | ASR: Whisper {model_size}) ---")
        self.transcription_model = whisper.load_model(model_size)
        self.ai_model = genai.GenerativeModel("gemini-2.0-flash")

        self.download_path.mkdir(exist_ok=True)

    def download_audio(self, url):
        if "spotify.com" in url:
            print(f"Step 1: Extrayendo audio de Spotify usando SpotDL...")
            # SpotDL automatically handles Spotify URLs/DRM by finding YouTube matches
            cmd = [
                sys.executable,
                "-m",
                "spotdl",
                url,
                "--output",
                str(self.download_path),
            ]
        else:
            print(f"Step 1: Extrayendo audio (Generic)...")
            output_tmpl = str(self.download_path / "%(id)s.%(ext)s")
            cmd = [
                sys.executable,
                "-m",
                "yt_dlp",
                "--extract-audio",
                "--audio-format",
                "mp3",
                "--output",
                output_tmpl,
                url,
            ]

        try:
            # We don't verify return code for spotdl as strict as yt-dlp sometimes,
            # but check=True is good. Captured output helps debugging.
            subprocess.run(
                cmd, check=True, capture_output=False, text=True
            )  # Let it print to stdout/stderr naturally for progress bars
        except subprocess.CalledProcessError as e:
            print(f"❌ Error downloading audio:")
            # If we didn't capture output, we can't print e.stdout/stderr easily unless we caught it.
            # SpotDL has own progress bar, so capture_output=False is better for user experience.
            print(f"Exit Code: {e.returncode}")
            raise e
        # Retorna el archivo más reciente en la carpeta de descargas
        return max(self.download_path.glob("*.mp3"), key=os.path.getctime)

    def get_insights(self, audio_path):
        print(
            f"Step 2: Transcribiendo y segmentando (esto toma tiempo según el hardware)..."
        )
        result = self.transcription_model.transcribe(str(audio_path), language="es")
        segments = result["segments"]

        # Agrupar por minuto
        minutes_data = {}
        for seg in segments:
            min_key = int(seg["start"] // 60)
            minutes_data[min_key] = minutes_data.get(min_key, "") + seg["text"] + " "

        detailed_insights = []
        print(f"Step 3: Procesando {len(minutes_data)} minutos con Gemini...")

        for minute, text in minutes_data.items():
            ts = str(timedelta(minutes=minute))
            prompt = f"Analiza este minuto {minute} de podcast y extrae el insight principal en una frase técnica: {text}"

            retry_count = 0
            max_retries = 5

            while retry_count < max_retries:
                try:
                    res = self.ai_model.generate_content(prompt)
                    detailed_insights.append(f"[{ts}] {res.text.strip()}")
                    print(f" Procesado minuto {minute}")
                    # Pequeña pausa para no saturar
                    time.sleep(2)
                    break
                except exceptions.ResourceExhausted:
                    wait_time = 30 * (retry_count + 1)  # Exponential-ish backoff
                    print(f" ⚠️ Rate Limit hit. Esperando {wait_time} segundos...")
                    time.sleep(wait_time)
                    retry_count += 1
                except Exception as e:
                    print(f" ❌ Error inesperado en minuto {minute}: {e}")
                    break

        return detailed_insights

    def summarize_all(self, insights):
        print(f"Step 4: Generando reporte ejecutivo final...")
        full_text = "\n".join(insights)
        prompt = f"Basado en estos insights por minuto, genera un reporte ejecutivo (Tesis, 3 Pilares y Conclusión): \n{full_text}"
        return self.ai_model.generate_content(prompt).text


# --- EJECUCIÓN ---
if __name__ == "__main__":
    app = PodcastApp(model_size="base")  # Cambia a 'small' o 'medium' para más rigor

    spotify_url = input("URL del Podcast: ")
    audio_file = app.download_audio(spotify_url)

    minute_by_minute = app.get_insights(audio_file)
    final_report = app.summarize_all(minute_by_minute)

    # Persistencia
    with open("resultado_final.md", "w", encoding="utf-8") as f:
        f.write("# Reporte de Podcast\n\n## Resumen Ejecutivo\n")
        f.write(final_report)
        f.write("\n\n## Insights por Minuto\n")
        f.write("\n".join(minute_by_minute))

    print("\n✅ ¡Listo! Revisa 'resultado_final.md'")
