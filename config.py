from pathlib import Path

# Папка для всех файлов
DATA_FOLDER = Path(__file__).resolve().parent / "data"
DATA_FOLDER.mkdir(exist_ok=True)  # создаём папку, если её нет