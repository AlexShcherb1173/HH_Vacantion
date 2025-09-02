# Что реализовано:
# Абстрактный класс FileHandler с методами add_items, get_items, delete_items.
# Наследники для JSON, CSV, XLSX, TXT.
# Не перезаписываются данные, добавляются новые вакансии.
# Приватный атрибут файла с именем, есть значение по умолчанию.
# Везде используется remove_duplicates(current, items, key="url").
# Файлы создаются при необходимости (_ensure_file или проверка os.path.exists).
# Данные корректно сохраняются и читаются для всех форматов: JSON, CSV, XLSX, TXT.
# Методы delete_items удаляют элементы по критериям и перезаписывают файл.


import json
import csv
from pathlib import Path
from abc import ABC, abstractmethod
from openpyxl import Workbook, load_workbook
from typing import List, Dict, Optional, Any
from src.services import remove_duplicates

# ------------------ Абстрактный класс ------------------
class FileHandler(ABC):
    """Абстрактный класс для работы с файлами вакансий."""
    def __init__(self, filename: Optional[str] = None) -> None:
        """:param filename: Имя файла"""
        self.__filename = filename or "data/vacancies_data"
        Path(self.__filename).parent.mkdir(exist_ok=True, parents=True)

    @abstractmethod
    def add_items(self, items: List[Dict[str, Any]]) -> None: ...
    """Добавляет вакансии в файл."""
    @abstractmethod
    def get_items(self, criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]: ...
    """Возвращает вакансии из файла с возможной фильтрацией."""
    @abstractmethod
    def delete_items(self, criteria: Optional[Dict[str, Any]] = None) -> None: ...
    """Удаляет вакансии из файла по критериям."""
# ------------------ JSON ------------------
class JSONHandler(FileHandler):
    """Работа с JSON-файлом вакансий."""
    def _ensure_file(self) -> None:
        if not Path(self._FileHandler__filename).exists():
            with open(self._FileHandler__filename, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)

    def add_items(self, items: List[Dict[str, Any]]) -> None:
        self._ensure_file()
        current = self.get_items()
        combined = remove_duplicates(current, items, key="url")
        with open(self._FileHandler__filename, "w", encoding="utf-8") as f:
            json.dump(combined, f, ensure_ascii=False, indent=4)

    def get_items(self, criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        self._ensure_file()
        with open(self._FileHandler__filename, "r", encoding="utf-8") as f:
            items = json.load(f)
        return _filter_items(items, criteria)

    def delete_items(self, criteria: Optional[Dict[str, Any]] = None) -> None:
        items = self.get_items()
        remaining = _remove_items(items, criteria)
        with open(self._FileHandler__filename, "w", encoding="utf-8") as f:
            json.dump(remaining, f, ensure_ascii=False, indent=4)

# ------------------ CSV ------------------
class CSVHandler(FileHandler):
    def _ensure_file(self):
        if not Path(self._FileHandler__filename).exists():
            with open(self._FileHandler__filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["title","location","published_at","url","salary","description"])
                writer.writeheader()

    def add_items(self, items: List[Dict[str, Any]]):
        self._ensure_file()
        current = self.get_items()
        combined = remove_duplicates(current, items, key="url")
        with open(self._FileHandler__filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title","location","published_at","url","salary","description"])
            writer.writeheader()
            writer.writerows(combined)

    def get_items(self, criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        self._ensure_file()
        with open(self._FileHandler__filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            items = list(reader)
        return _filter_items(items, criteria)

    def delete_items(self, criteria: Optional[Dict[str, Any]] = None):
        items = self.get_items()
        remaining = _remove_items(items, criteria)
        with open(self._FileHandler__filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title","location","published_at","url","salary","description"])
            writer.writeheader()
            writer.writerows(remaining)

# ------------------ XLSX ------------------
class XLSXHandler(FileHandler):
    def _ensure_file(self):
        if not Path(self._FileHandler__filename).exists():
            wb = Workbook()
            ws = wb.active
            ws.append(["title","location","published_at","url","salary","description"])
            wb.save(self._FileHandler__filename)

    def add_items(self, items: List[Dict[str, Any]]):
        self._ensure_file()
        current = self.get_items()
        combined = remove_duplicates(current, items, key="url")
        wb = Workbook()
        ws = wb.active
        ws.append(["title","location","published_at","url","salary","description"])
        for item in combined:
            ws.append([item.get(f, "") for f in ["title","location","published_at","url","salary","description"]])
        wb.save(self._FileHandler__filename)

    def get_items(self, criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        self._ensure_file()
        wb = load_workbook(self._FileHandler__filename)
        ws = wb.active
        rows = list(ws.values)
        keys = rows[0]
        items = [dict(zip(keys, row)) for row in rows[1:]]
        return _filter_items(items, criteria)

    def delete_items(self, criteria: Optional[Dict[str, Any]] = None):
        items = self.get_items()
        remaining = _remove_items(items, criteria)
        wb = Workbook()
        ws = wb.active
        ws.append(["title","location","published_at","url","salary","description"])
        for item in remaining:
            ws.append([item.get(f, "") for f in ["title","location","published_at","url","salary","description"]])
        wb.save(self._FileHandler__filename)

# ------------------ TXT ------------------
class TXTHandler(FileHandler):
    def _ensure_file(self):
        Path(self._FileHandler__filename).touch(exist_ok=True)

    def add_items(self, items: List[Dict[str, Any]]):
        self._ensure_file()
        current = self.get_items()
        combined = remove_duplicates(current, items, key="url")
        with open(self._FileHandler__filename, "w", encoding="utf-8") as f:
            for item in combined:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    def get_items(self, criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        self._ensure_file()
        items = []
        with open(self._FileHandler__filename, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    items.append(json.loads(line.strip()))
        return _filter_items(items, criteria)

    def delete_items(self, criteria: Optional[Dict[str, Any]] = None):
        items = self.get_items()
        remaining = _remove_items(items, criteria)
        with open(self._FileHandler__filename, "w", encoding="utf-8") as f:
            for item in remaining:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

# ------------------ Вспомогательные функции ------------------
def _filter_items(items: List[Dict[str, Any]], criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    if not criteria:
        return items
    result = []
    for item in items:
        match = True
        for k, v in criteria.items():
            val = item.get(k)
            if isinstance(v, (list, tuple, set)):
                if str(val) not in map(str, v):
                    match = False
                    break
            else:
                if str(val) != str(v):
                    match = False
                    break
        if match:
            result.append(item)
    return result

def _remove_items(items: List[Dict[str, Any]], criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    if not criteria:
        return []
    remaining = []
    for item in items:
        remove = True
        for k, v in criteria.items():
            val = item.get(k)
            if isinstance(v, (list, tuple, set)):
                if str(val) in map(str, v):
                    continue
                else:
                    remove = False
                    break
            else:
                if str(val) == str(v):
                    continue
                else:
                    remove = False
                    break
        if not remove:
            remaining.append(item)
    return remaining