# 🚀 Guía de Inicio Rápido - Blue Tech Materials Tracker

Esta guía te ayudará a tener el sistema funcionando en menos de 5 minutos.

## ⚡ Quick Start

### 1. Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/your-org/blue-tech-materials.git
cd blue-tech-materials

# Crear entorno virtual e instalar dependencias
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# Crear estructura de directorios
mkdir -p data/backups logs
```

### 2. Configuración Básica

```bash
# Copiar template de configuración
cp .env.example .env

# Las configuraciones por defecto funcionan, pero puedes personalizar si necesitas
```

### 3. Recolectar Datos

```bash
# Ejecutar el scraper
python material_scraper_improved.py
```

**Salida esperada:**
```
============================================================
🚀 STARTING MATERIAL PRICE SCRAPER
============================================================
Initialized 2 data source(s)

────────────────────────────────────────────────────────────
📡 Fetching from: StaticDataSource
────────────────────────────────────────────────────────────
  ➜ Raw data fetched: 15 items
  ➜ Data formatted: 15 items
  ➜ Data validated: 15 valid items
✅ StaticDataSource completed successfully

────────────────────────────────────────────────────────────
📡 Fetching from: NumbeoGlobalScraper
────────────────────────────────────────────────────────────
  ➜ Raw data fetched: 8 items
  ➜ Data formatted: 8 items
  ➜ Data validated: 8 valid items
✅ NumbeoGlobalScraper completed successfully

============================================================
💾 PROCESSING COLLECTED DATA
============================================================
Created DataFrame with 23 records
Validation complete: 23 valid records
✅ Data saved successfully to: data/material_prices.csv

============================================================
📋 SCRAPING SESSION SUMMARY
============================================================
Duration: 2.34 seconds
Total sources attempted: 2
Successful sources: 2
Failed sources: 0
Total valid records collected: 23
```

### 4. Lanzar Dashboard

```bash
# Iniciar dashboard
streamlit run material_dashboard_improved.py
```

El navegador se abrirá automáticamente en: `http://localhost:8501`

## 📊 Usando el Dashboard

### Navegación Básica

1. **Filtros en la Barra Lateral**
   - Selecciona un material (ej: "Cemento", "Acero")
   - Filtra por países específicos
   - Activa/desactiva visualización de moneda original

2. **Indicadores Clave (KPIs)**
   - Precio promedio global
   - Mercado más económico
   - Mercado más costoso

3. **Visualizaciones**
   - **Mapa Mundial**: Intensidad de precios por país
   - **Gráfico de Barras**: Comparación directa entre países
   - **Box Plot**: Distribución de precios

4. **Datos Detallados**
   - Tabla con todos los datos filtrados
   - Botón de descarga CSV

### Funcionalidades Avanzadas

- **Comparar Múltiples Países**: Usa el multiselect en la barra lateral
- **Análisis de Variación**: Ve desviación estándar y coeficiente de variación
- **Ver Datos Crudos**: Expande la sección al final para ver todos los datos
- **Descargar Reportes**: Usa los botones de descarga CSV

## 🔄 Actualización de Datos

### Manual

```bash
# Re-ejecutar scraper cuando quieras actualizar
python material_scraper_improved.py
```

### Automática (Linux/Mac con cron)

```bash
# Editar crontab
crontab -e

# Agregar línea para ejecutar diariamente a las 6 AM
0 6 * * * cd /path/to/project && /path/to/venv/bin/python material_scraper_improved.py
```

### Automática (Windows con Task Scheduler)

1. Abrir "Programador de tareas"
2. Crear tarea básica
3. Trigger: Diariamente a las 6:00 AM
4. Acción: Ejecutar `python.exe material_scraper_improved.py`

## 🎨 Personalización Rápida

### Cambiar Puerto del Dashboard

```bash
streamlit run material_dashboard_improved.py --server.port 8502
```

### Agregar Nuevos Países

Edita `config.py`:

```python
COUNTRY_MAPPING = {
    # ... existentes ...
    "TuPais": "ISO",
}
```

### Agregar Nuevas Monedas

Edita `config.py`:

```python
EXCHANGE_RATES = {
    # ... existentes ...
    "TUC": 0.XX,  # Tu moneda: tasa a USD
}
```

### Cambiar Nivel de Logs

Edita `.env`:

```env
LOG_LEVEL=DEBUG  # Opciones: DEBUG, INFO, WARNING, ERROR
```

## 📝 Comandos Útiles

```bash
# Ver logs en tiempo real
tail -f logs/scraper.log

# Limpiar cache del dashboard
streamlit cache clear

# Ejecutar tests
pytest test_dashboard.py -v

# Ver estructura de datos
head -n 5 data/material_prices.csv

# Contar registros
wc -l data/material_prices.csv

# Ver último backup
ls -lt data/backups/ | head -n 2
```

## ❓ Problemas Comunes

### "No module named 'streamlit'"

```bash
# Asegúrate de estar en el entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstalar dependencias
pip install -r requirements.txt
```

### "Data file not found"

```bash
# Ejecutar scraper primero
python material_scraper_improved.py
```

### Dashboard no carga

```bash
# Verificar que el puerto no esté en uso
netstat -ano | findstr :8501  # Windows
lsof -i :8501                 # Linux/Mac

# Usar puerto alternativo
streamlit run material_dashboard_improved.py --server.port 8502
```

### Permisos denegados (Linux/Mac)

```bash
# Dar permisos a directorios
chmod -R 755 data logs

# Dar permisos de ejecución a scripts
chmod +x material_scraper_improved.py
```

## 🎯 Próximos Pasos

1. **Explora el Dashboard**: Prueba todos los filtros y visualizaciones
2. **Agrega Datos**: Crea tu propia fuente de datos en `sources/`
3. **Automatiza**: Configura ejecuciones programadas
4. **Personaliza**: Ajusta colores, idioma y métricas según necesites
5. **Comparte**: Exporta reportes y compártelos con tu equipo

## 💡 Tips Pro

- **Usa atajos de teclado**: `Ctrl+C` para detener, `↑` para repetir comando
- **Monitorea logs**: Mantén `tail -f logs/scraper.log` abierto mientras scrapes
- **Cache del dashboard**: Presiona `C` en el dashboard para limpiar cache
- **Modo oscuro**: En el dashboard, ir a Settings > Theme > Dark
- **Performance**: Para datasets grandes, considera usar `@st.cache_data`

## 📚 Recursos Adicionales

- 📖 **README completo**: Ver `README.md` para documentación detallada
- 🧪 **Tests**: Ejecutar `pytest` para verificar el sistema
- ⚙️ **Configuración**: Ver `config.py` para todas las opciones
- 📝 **Logs**: Revisar `logs/` para debugging

## 🆘 Soporte

¿Necesitas ayuda?

- 📧 Email: support@bluetech.com
- 💬 Discord: https://discord.gg/bluetech
- 🐛 Issues: https://github.com/your-org/blue-tech-materials/issues

---

**¡Listo! Ya tienes el sistema funcionando. Happy tracking! 🎉**
