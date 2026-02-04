# 🎙️ Podcast Analyzer con IA

Herramienta avanzada para analizar podcasts usando Whisper (transcripción) y Gemini (análisis con IA).

## ✨ Características

- 🎯 **Descarga automática** de audio desde múltiples plataformas
- 🗣️ **Transcripción precisa** con OpenAI Whisper
- 🧠 **Análisis inteligente** con Google Gemini
- ⚡ **Procesamiento paralelo** para máxima velocidad
- 📊 **Reportes profesionales** en Markdown + JSON
- 🔧 **Altamente configurable** vía variables de entorno

## 🚀 Instalación Rápida

### 1. Clonar o descargar el proyecto

```bash
git clone <tu-repo>
cd podcast-analyzer
```

### 2. Crear entorno virtual (recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar API Key

1. Obtén tu Google API Key en: https://aistudio.google.com/app/apikey
2. Copia el archivo de ejemplo:
   ```bash
   cp .env.example .env
   ```
3. Edita `.env` y añade tu API key:
   ```bash
   GOOGLE_API_KEY=tu_clave_aqui
   ```

## 📖 Uso

### Uso básico

```bash
python spotify_analyzer_optimized.py
```

El programa te pedirá la URL del podcast:
```
🎙️  ANALIZADOR DE PODCASTS CON IA
============================================================

📎 Ingresa la URL del podcast: https://youtube.com/watch?v=...
```

### URLs soportadas

Funciona con cualquier plataforma soportada por yt-dlp:
- YouTube
- Spotify (con plugins adicionales)
- SoundCloud
- Apple Podcasts
- Y muchas más...

## 📁 Estructura de Archivos

```
podcast-analyzer/
├── spotify_analyzer_optimized.py   # Código principal
├── requirements.txt                 # Dependencias
├── .env                             # Configuración (crear desde .env.example)
├── .env.example                     # Plantilla de configuración
├── downloads/                       # Audios descargados (temporal)
├── output/                          # Resultados finales
│   ├── resultado_final.md          # Reporte legible
│   └── resultado_final.json        # Datos estructurados
└── podcast_analyzer.log            # Log de ejecución
```

## ⚙️ Configuración Avanzada

Edita el archivo `.env` para personalizar:

```bash
# Modelo de Whisper (base, small, medium, large)
WHISPER_MODEL=base

# Procesamiento paralelo (1-5 hilos)
MAX_WORKERS=3

# Directorios personalizados
DOWNLOAD_PATH=./mis_descargas
OUTPUT_PATH=./mis_resultados
```

### Modelos de Whisper

| Modelo | Velocidad | Precisión | Uso RAM | Recomendado para |
|--------|-----------|-----------|---------|------------------|
| `tiny` | ⚡⚡⚡⚡⚡ | ⭐⭐ | 1 GB | Tests rápidos |
| `base` | ⚡⚡⚡⚡ | ⭐⭐⭐ | 1.5 GB | **Uso general** |
| `small` | ⚡⚡⚡ | ⭐⭐⭐⭐ | 2 GB | Mejor calidad |
| `medium` | ⚡⚡ | ⭐⭐⭐⭐⭐ | 5 GB | Producción |
| `large` | ⚡ | ⭐⭐⭐⭐⭐ | 10 GB | Máxima precisión |

## 📊 Ejemplo de Salida

### resultado_final.md

```markdown
# 🎙️ Análisis de Podcast

## 📋 Información

- **Archivo**: podcast-emprendimiento-abc123.mp3
- **Duración**: 1:15:30
- **Idioma**: es
- **Insights generados**: 75

## 📊 RESUMEN EJECUTIVO

### Tesis Principal
El podcast explora estrategias de growth hacking para startups...

### Tres Pilares Fundamentales
1. **Marketing de Contenidos**: ...
2. **Data-Driven Decisions**: ...
3. **Optimización Continua**: ...

### Conclusión
...

## 🔍 Insights por Minuto

**[0:00:00]** Introducción al concepto de product-market fit...
**[0:01:00]** Análisis de métricas clave: CAC y LTV...
**[0:02:00]** Estrategias de retención de usuarios...
```

## 🐛 Solución de Problemas

### Error: "GOOGLE_API_KEY no encontrada"

**Solución:** Verifica que el archivo `.env` existe y contiene tu API key.

```bash
# Verifica el contenido
cat .env

# Debe contener:
GOOGLE_API_KEY=AIzaSyC_tu_clave_real
```

### Error: "yt-dlp no encontrado"

**Solución:** Reinstala las dependencias:

```bash
pip install --upgrade yt-dlp
```

### Error: "Out of memory" durante transcripción

**Solución:** Usa un modelo más ligero:

```bash
# En .env
WHISPER_MODEL=tiny
```

### El proceso es muy lento

**Soluciones:**
1. Aumenta workers (si tu API lo permite):
   ```bash
   MAX_WORKERS=5
   ```
2. Usa un modelo Whisper más pequeño
3. Verifica tu conexión a internet

## 📈 Rendimiento Esperado

Tiempos aproximados en hardware moderno (CPU de 8 núcleos):

| Duración Podcast | Modelo Whisper | Workers | Tiempo Total |
|------------------|----------------|---------|--------------|
| 30 min | base | 3 | ~3-5 min |
| 60 min | base | 3 | ~5-8 min |
| 120 min | base | 3 | ~12-15 min |
| 60 min | small | 3 | ~8-12 min |

## 🔒 Seguridad

- ✅ API keys en `.env` (nunca en el código)
- ✅ `.env` en `.gitignore` por defecto
- ✅ No almacena datos sensibles
- ✅ Logs locales solamente

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -am 'Añade nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Pull Request

## 📝 Licencia

MIT License - ver archivo LICENSE

## 🙏 Agradecimientos

- OpenAI Whisper por el motor de transcripción
- Google Gemini por el análisis con IA
- yt-dlp por la descarga de audio

## 📧 Contacto

¿Preguntas? Abre un issue en GitHub o contacta al mantenedor.

---

**⭐ Si te resulta útil, deja una estrella en GitHub!**
