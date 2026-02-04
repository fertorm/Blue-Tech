"""
Analizador de Podcasts con IA
Extrae audio, transcribe y genera insights usando Whisper y Gemini.
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from datetime import timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

import whisper
import google.generativeai as genai
from dotenv import load_dotenv


# --- CONFIGURACIÓN DE LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("podcast_analyzer.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


# --- MODELOS DE DATOS ---
@dataclass
class SegmentInsight:
    """Representa un insight de un segmento temporal."""

    minute: int
    timestamp: str
    text: str
    insight: str


@dataclass
class PodcastAnalysis:
    """Resultado completo del análisis."""

    audio_file: Path
    insights: List[SegmentInsight]
    executive_summary: str
    metadata: Dict


# --- CONFIGURACIÓN ---
class Config:
    """Centraliza la configuración de la aplicación."""

    def __init__(self):
        load_dotenv()
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.whisper_model_size = os.getenv("WHISPER_MODEL", "base")
        self.download_path = Path(os.getenv("DOWNLOAD_PATH", "./downloads"))
        self.output_path = Path(os.getenv("OUTPUT_PATH", "./data"))
        self.max_workers = int(os.getenv("MAX_WORKERS", "3"))
        self.batch_size = int(os.getenv("BATCH_SIZE", "5"))

        self._validate()
        self._setup_directories()

    def _validate(self):
        """Valida que las configuraciones necesarias estén presentes."""
        if not self.google_api_key:
            logger.error("GOOGLE_API_KEY no encontrada en .env")
            raise ValueError(
                "GOOGLE_API_KEY es requerida. Configúrala en el archivo .env"
            )

    def _setup_directories(self):
        """Crea los directorios necesarios."""
        self.download_path.mkdir(exist_ok=True)
        self.output_path.mkdir(exist_ok=True)


# --- DESCARGADOR DE AUDIO ---
class AudioDownloader:
    """Maneja la descarga de audio desde URLs."""

    def __init__(self, download_path: Path):
        self.download_path = download_path

    def download(self, url: str) -> Path:
        """
        Descarga audio de una URL usando yt-dlp.

        Args:
            url: URL del podcast o video

        Returns:
            Path al archivo de audio descargado

        Raises:
            subprocess.CalledProcessError: Si la descarga falla
        """
        logger.info(f"Descargando audio desde: {url}")

        output_tmpl = str(self.download_path / "%(title)s-%(id)s.%(ext)s")
        cmd = [
            sys.executable,
            "-m",
            "yt_dlp",
            "--extract-audio",
            "--audio-format",
            "mp3",
            "--audio-quality",
            "0",  # Mejor calidad
            "--output",
            output_tmpl,
            "--no-playlist",  # Evitar descargar playlists completas
            url,
        ]

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.debug(f"Salida de yt-dlp: {result.stdout}")

            # Encuentra el archivo más reciente
            audio_files = list(self.download_path.glob("*.mp3"))
            if not audio_files:
                raise FileNotFoundError("No se encontró el archivo de audio descargado")

            audio_file = max(audio_files, key=os.path.getctime)
            logger.info(f"Audio descargado exitosamente: {audio_file.name}")
            return audio_file

        except subprocess.CalledProcessError as e:
            logger.error(f"Error al descargar audio: {e.stderr}")
            raise


# --- TRANSCRIPTOR ---
class AudioTranscriber:
    """Maneja la transcripción de audio usando Whisper."""

    def __init__(self, model_size: str = "base"):
        logger.info(f"Cargando modelo Whisper: {model_size}")
        self.model = whisper.load_model(model_size)
        logger.info("Modelo Whisper cargado exitosamente")

    def transcribe(self, audio_path: Path, language: str = "es") -> Dict:
        """
        Transcribe un archivo de audio.

        Args:
            audio_path: Ruta al archivo de audio
            language: Código de idioma (default: español)

        Returns:
            Diccionario con la transcripción y segmentos
        """
        logger.info(f"Transcribiendo: {audio_path.name}")
        logger.warning(
            "Este proceso puede tomar varios minutos según la duración del audio..."
        )

        try:
            result = self.model.transcribe(
                str(audio_path), language=language, verbose=False, task="transcribe"
            )

            logger.info(
                f"Transcripción completada. {len(result['segments'])} segmentos encontrados"
            )
            return result

        except Exception as e:
            logger.error(f"Error durante la transcripción: {str(e)}")
            raise


# --- ANALIZADOR DE IA ---
class AIAnalyzer:
    """Maneja el análisis con IA usando Gemini."""

    def __init__(self, api_key: str, max_workers: int = 3):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
        self.max_workers = max_workers
        logger.info(f"Analizador IA configurado (workers: {max_workers})")

    def _analyze_segment(self, minute: int, text: str) -> Optional[SegmentInsight]:
        """
        Analiza un segmento individual de texto.

        Args:
            minute: Número del minuto
            text: Texto a analizar

        Returns:
            SegmentInsight o None si falla
        """
        if not text.strip():
            return None

        timestamp = str(timedelta(minutes=minute))
        prompt = (
            f"Analiza este fragmento de un podcast (minuto {minute}) y extrae "
            f"el insight o concepto clave más importante en una frase concisa y técnica.\n\n"
            f"Texto: {text}\n\n"
            f"Responde SOLO con el insight, sin prefijos ni explicaciones."
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=150,
                ),
            )

            insight = response.text.strip()
            logger.debug(f"Minuto {minute} procesado")

            return SegmentInsight(
                minute=minute,
                timestamp=timestamp,
                text=text[:200],  # Guardar muestra del texto
                insight=insight,
            )

        except Exception as e:
            logger.warning(f"Error al procesar minuto {minute}: {str(e)}")
            return None

    def analyze_segments(self, segments_data: Dict[int, str]) -> List[SegmentInsight]:
        """
        Analiza múltiples segmentos en paralelo.

        Args:
            segments_data: Diccionario {minuto: texto}

        Returns:
            Lista de SegmentInsight
        """
        logger.info(f"Analizando {len(segments_data)} segmentos con IA...")
        insights = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Crear tareas
            future_to_minute = {
                executor.submit(self._analyze_segment, minute, text): minute
                for minute, text in segments_data.items()
            }

            # Procesar resultados conforme se completan
            for future in as_completed(future_to_minute):
                minute = future_to_minute[future]
                try:
                    result = future.result()
                    if result:
                        insights.append(result)
                        logger.info(f"✓ Minuto {minute} completado")
                except Exception as e:
                    logger.error(f"✗ Error en minuto {minute}: {str(e)}")

        # Ordenar por minuto
        insights.sort(key=lambda x: x.minute)
        logger.info(f"Análisis completado: {len(insights)} insights generados")
        return insights

    def generate_executive_summary(self, insights: List[SegmentInsight]) -> str:
        """
        Genera un resumen ejecutivo basado en los insights.

        Args:
            insights: Lista de insights generados

        Returns:
            Resumen ejecutivo
        """
        logger.info("Generando resumen ejecutivo...")

        insights_text = "\n".join(
            [f"[{ins.timestamp}] {ins.insight}" for ins in insights]
        )

        prompt = f"""Basándote en estos insights cronológicos de un podcast, genera un reporte ejecutivo profesional con la siguiente estructura:

## 📊 RESUMEN EJECUTIVO

### Tesis Principal
[Una declaración clara del tema central o argumento principal del podcast]

### Tres Pilares Fundamentales
1. **[Pilar 1]**: [Explicación concisa]
2. **[Pilar 2]**: [Explicación concisa]
3. **[Pilar 3]**: [Explicación concisa]

### Conclusión
[Síntesis del impacto o aplicabilidad práctica del contenido]

---

Insights del podcast:
{insights_text}

Genera un reporte profesional, bien estructurado y directo al grano."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,
                    max_output_tokens=1000,
                ),
            )

            summary = response.text.strip()
            logger.info("Resumen ejecutivo generado exitosamente")
            return summary

        except Exception as e:
            logger.error(f"Error al generar resumen: {str(e)}")
            return "Error: No se pudo generar el resumen ejecutivo."


# --- PROCESADOR PRINCIPAL ---
class PodcastAnalyzer:
    """Orquesta todo el proceso de análisis."""

    def __init__(self, config: Config):
        self.config = config
        self.downloader = AudioDownloader(config.download_path)
        self.transcriber = AudioTranscriber(config.whisper_model_size)
        self.analyzer = AIAnalyzer(config.google_api_key, config.max_workers)

    def _group_by_minute(self, segments: List[Dict]) -> Dict[int, str]:
        """
        Agrupa segmentos de transcripción por minuto.

        Args:
            segments: Lista de segmentos de Whisper

        Returns:
            Diccionario {minuto: texto_concatenado}
        """
        minutes_data = {}

        for seg in segments:
            minute = int(seg["start"] // 60)
            text = seg["text"].strip()

            if minute not in minutes_data:
                minutes_data[minute] = ""
            minutes_data[minute] += text + " "

        # Limpiar espacios extras
        minutes_data = {k: v.strip() for k, v in minutes_data.items()}

        logger.info(f"Agrupados {len(minutes_data)} minutos de contenido")
        return minutes_data

    def analyze(self, url: str) -> PodcastAnalysis:
        """
        Ejecuta el análisis completo del podcast.

        Args:
            url: URL del podcast

        Returns:
            PodcastAnalysis con todos los resultados
        """
        logger.info("=" * 60)
        logger.info("INICIANDO ANÁLISIS DE PODCAST")
        logger.info("=" * 60)

        # Paso 1: Descargar audio
        audio_file = self.downloader.download(url)

        # Paso 2: Transcribir
        transcription = self.transcriber.transcribe(audio_file)

        # Paso 3: Agrupar por minuto
        minutes_data = self._group_by_minute(transcription["segments"])

        # Paso 4: Analizar con IA
        insights = self.analyzer.analyze_segments(minutes_data)

        # Paso 5: Generar resumen ejecutivo
        executive_summary = self.analyzer.generate_executive_summary(insights)

        # Crear resultado
        analysis = PodcastAnalysis(
            audio_file=audio_file,
            insights=insights,
            executive_summary=executive_summary,
            metadata={
                "url": url,
                "duration": transcription.get("duration", 0),
                "language": transcription.get("language", "unknown"),
                "total_segments": len(transcription["segments"]),
                "total_insights": len(insights),
            },
        )

        logger.info("=" * 60)
        logger.info("ANÁLISIS COMPLETADO")
        logger.info("=" * 60)

        return analysis

    def save_results(
        self, analysis: PodcastAnalysis, filename: str = "resultado_final.md"
    ):
        """
        Guarda los resultados en archivos.

        Args:
            analysis: Resultado del análisis
            filename: Nombre del archivo de salida
        """
        output_file = self.config.output_path / filename
        json_file = self.config.output_path / filename.replace(".md", ".json")

        # Guardar Markdown
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# 🎙️ Análisis de Podcast\n\n")

            # Metadata
            f.write("## 📋 Información\n\n")
            f.write(f"- **Archivo**: {analysis.audio_file.name}\n")
            f.write(
                f"- **Duración**: {timedelta(seconds=int(analysis.metadata['duration']))}\n"
            )
            f.write(f"- **Idioma**: {analysis.metadata['language']}\n")
            f.write(
                f"- **Insights generados**: {analysis.metadata['total_insights']}\n\n"
            )

            # Resumen ejecutivo
            f.write(analysis.executive_summary)
            f.write("\n\n---\n\n")

            # Insights detallados
            f.write("## 🔍 Insights por Minuto\n\n")
            for insight in analysis.insights:
                f.write(f"**[{insight.timestamp}]** {insight.insight}\n\n")

        logger.info(f"Resultados guardados en: {output_file}")

        # Guardar JSON para procesamiento posterior
        json_data = {
            "audio_file": str(analysis.audio_file),
            "metadata": analysis.metadata,
            "executive_summary": analysis.executive_summary,
            "insights": [
                {
                    "minute": ins.minute,
                    "timestamp": ins.timestamp,
                    "insight": ins.insight,
                }
                for ins in analysis.insights
            ],
        }

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Datos JSON guardados en: {json_file}")


# --- EJECUCIÓN PRINCIPAL ---
def main():
    """Función principal de ejecución."""
    try:
        # Cargar configuración
        config = Config()

        # Crear analizador
        analyzer = PodcastAnalyzer(config)

        # Solicitar URL
        print("\n" + "=" * 60)
        print("🎙️  ANALIZADOR DE PODCASTS CON IA")
        print("=" * 60)
        url = input("\n📎 Ingresa la URL del podcast: ").strip()

        if not url:
            print("❌ URL no válida")
            return

        # Ejecutar análisis
        analysis = analyzer.analyze(url)

        # Guardar resultados
        analyzer.save_results(analysis)

        # Mostrar resumen en consola
        print("\n" + "=" * 60)
        print("✅ ¡ANÁLISIS COMPLETADO!")
        print("=" * 60)
        print(f"\n📄 Revisa los resultados en:")
        print(f"   - {config.output_path / 'resultado_final.md'}")
        print(f"   - {config.output_path / 'resultado_final.json'}")
        print()

    except KeyboardInterrupt:
        logger.warning("\n⚠️ Proceso interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error fatal: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
