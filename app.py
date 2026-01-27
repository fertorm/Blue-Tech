from flask import Flask, jsonify, send_from_directory
import os
import threading
from web_scrapper_v3 import scrapear_noticias
from scraper_runner import ScraperLogic
from database_manager import DatabaseManager

app = Flask(__name__, static_folder="landing_page")


# --- Helper Functions ---
def run_news_scraper():
    try:
        print("Iniciando scraping de noticias...")
        df = scrapear_noticias()
        # Ensure directory exists
        df.to_csv("data/noticias_mundo.csv", index=False)
        return {
            "status": "success",
            "message": f"Se obtuvieron {len(df)} noticias.",
            "count": len(df),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def run_prices_scraper():
    try:
        print("Iniciando scraping de precios...")
        # Mocking the log callback
        logs = []

        def log_capture(msg):
            logs.append(msg)
            print(f"[Scraper] {msg}")

        logic = ScraperLogic(log_capture)
        # Using the logic methods directly
        all_data = []

        # Run for all configured sources
        data_tailoy = logic.scrape_tailoy("https://www.tailoy.com.bo/escolar.html")
        all_data.extend(data_tailoy)

        data_brasil = logic.scrape_libreria_brasil()
        all_data.extend(data_brasil)

        data_mat_bo = logic.scrape_materiales_bo()
        all_data.extend(data_mat_bo)

        if all_data:
            success, msg = logic.db.save_data(all_data)
            return {
                "status": "success",
                "message": f"Se obtuvieron {len(all_data)} productos. {msg}",
                "count": len(all_data),
                "logs": logs,
            }
        else:
            return {
                "status": "warning",
                "message": "No se encontraron productos.",
                "logs": logs,
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- Routes ---


@app.route("/")
def index():
    return send_from_directory("landing_page", "index.html")


@app.route("/css/<path:path>")
def send_css(path):
    return send_from_directory("landing_page/css", path)


@app.route("/js/<path:path>")
def send_js(path):
    return send_from_directory("landing_page/js", path)


@app.route("/api/run-news", methods=["POST"])
def api_run_news():
    # Run synchronously for now (simple demo)
    result = run_news_scraper()
    return jsonify(result)


@app.route("/api/run-prices", methods=["POST"])
def api_run_prices():
    result = run_prices_scraper()
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
