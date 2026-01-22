# Refactorización del Proyecto Blue Tech

Hemos reorganizado el código para cumplir con los requisitos de modularidad, simplicidad y orden.

## Estructura Nueva

1.  **`main.py`** (App Principal)
    *   Esta es la entrada principal. Ejecuta este archivo para ver el lanzador.
    *   Permite abrir el Scraper y el Dashboard independientemente.

2.  **`scraper_runner.py`** (App de Scraping)
    *   Aplicación dedicada exclusivamente a la recolección de datos.
    *   Interfaz limpia con opciones para activar/desactivar sitios (Tailoy, Libreria Brasil, Materiales BO).
    *   Guarda los datos automáticamente en `Base_Datos_BlueTech.xlsx`.

3.  **`dashboard.py`** (App de Dashboard)
    *   Visualización de datos con Streamlit.
    *   Lee los datos generados por el scraper.

4.  **`database_manager.py`** (Gestor de Datos)
    *   Módulo auxiliar que maneja la lógica de guardado y limpieza de precios en Excel. Evita duplicación de código.

## Instrucciones

1.  Ejecuta `main.py`:
    ```bash
    python main.py
    ```
2.  Desde el menú, abre el **Scraper**.
3.  Selecciona las tiendas que deseas procesar y dale a "Iniciar".
4.  Cierra el scraper o vuelve al menú y abre el **Dashboard** para ver los resultados.

## Notas sobre los Scrapers

-   **Tailoy**: Implementado con lógica real basada en el código anterior.
-   **Libreria Brasil & Materiales BO**: Actualmente usan datos simulados/placeholders. Para activarlos con datos reales, edita las funciones `scrape_libreria_brasil` y `scrape_materiales_bo` en `scraper_runner.py` con los selectores CSS correctos.
