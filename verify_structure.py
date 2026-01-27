import os
import sys
from pathlib import Path


def verify():
    base = Path.cwd()
    data = base / "data"
    docs = base / "docs"
    logs = base / "logs"

    # Check Directories
    if not data.exists():
        print("❌ Data dir missing")
        return
    if not docs.exists():
        print("❌ Docs dir missing")
        return
    if not logs.exists():
        print("❌ Logs dir missing")
        return

    # Check Files
    files_to_check = [
        data / "Base_Datos_BlueTech.xlsx",
        data / "noticias_mundo.csv",
        data / "precios_escolares.csv",
        logs / "scraper.log",
        docs / "QUICKSTART.md",
    ]

    for f in files_to_check:
        if f.exists():
            print(f"✅ Found {f.name}")
        else:
            print(f"❌ Missing {f.name}")


if __name__ == "__main__":
    verify()
