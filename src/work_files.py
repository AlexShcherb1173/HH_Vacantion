# Что реализовано:
# Абстрактный класс FileHandler с методами add_items, get_items, delete_items.
# Наследники для JSON, CSV, XLSX, TXT.
# Не перезаписываются данные, добавляются новые вакансии.
# Приватный атрибут файла с именем, есть значение по умолчанию.


from abc import ABC, abstractmethod
from typing import List, Dict, Any
import json
import csv
import os
from openpyxl import Workbook, load_workbook
from src.services import remove_duplicates, filter_items


class FileHandler(ABC):
    """Абстрактный класс для работы с файлами."""

    @abstractmethod
    def add_items(self, items: List[Dict[str, Any]]) -> None:
        """Добавление данных в файл."""
        pass

    @abstractmethod
    def get_items(self, criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Получение данных из файла по критериям."""
        pass

    @abstractmethod
    def delete_items(self, criteria: Dict[str, Any]) -> None:
        """Удаление данных из файла по критериям."""
        pass


# -------------------- JSON --------------------
class JSONHandler(FileHandler):
    def __init__(self, filename: str = "vacancies.json") -> None:
        self.__filename = filename

    def add_items(self, items: List[Dict[str, Any]]) -> None:
        data = self.get_items() or []
        items_to_add = remove_duplicates(data, items, key="url")
        data.extend(items_to_add)
        with open(self.__filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_items(self, criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if not os.path.exists(self.__filename):
            return []
        with open(self.__filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        if criteria:
            data = filter_items(data, criteria)
        return data

    def delete_items(self, criteria: Dict[str, Any]) -> None:
        data = self.get_items()
        data = [item for item in data if not all(item.get(k) == v for k, v in criteria.items())]
        with open(self.__filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


# -------------------- CSV --------------------
class CSVHandler(FileHandler):
    def __init__(self, filename: str = "vacancies.csv") -> None:
        self.__filename = filename

    def add_items(self, items: List[Dict[str, Any]]) -> None:
        existing = self.get_items() or []
        items_to_add = remove_duplicates(existing, items, key="url")
        if not items_to_add:
            return
        file_exists = os.path.exists(self.__filename)
        with open(self.__filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=items_to_add[0].keys())
            if not file_exists:
                writer.writeheader()
            for item in items_to_add:
                writer.writerow(item)

    def get_items(self, criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if not os.path.exists(self.__filename):
            return []
        with open(self.__filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = [row for row in reader]
        if criteria:
            data = filter_items(data, criteria)
        return data

    def delete_items(self, criteria: Dict[str, Any]) -> None:
        data = self.get_items()
        data = [item for item in data if not all(item.get(k) == v for k, v in criteria.items())]
        if not data:
            open(self.__filename, "w").close()
            return
        with open(self.__filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)


# -------------------- XLSX --------------------
class XLSXHandler(FileHandler):
    def __init__(self, filename: str = "vacancies.xlsx") -> None:
        self.__filename = filename

    def add_items(self, items: List[Dict[str, Any]]) -> None:
        if os.path.exists(self.__filename):
            wb = load_workbook(self.__filename)
            ws = wb.active
            existing = [dict(zip([c.value for c in ws[1]], [cell.value for cell in row])) for row in ws.iter_rows(min_row=2)]
        else:
            wb = Workbook()
            ws = wb.active
            ws.append(list(items[0].keys()))
            existing = []

        items_to_add = remove_duplicates(existing, items, key="url")
        for item in items_to_add:
            ws.append(list(item.values()))
        wb.save(self.__filename)

    def get_items(self, criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if not os.path.exists(self.__filename):
            return []
        wb = load_workbook(self.__filename)
        ws = wb.active
        keys = [cell.value for cell in ws[1]]
        data = [dict(zip(keys, [cell.value for cell in row])) for row in ws.iter_rows(min_row=2)]
        if criteria:
            data = filter_items(data, criteria)
        return data

    def delete_items(self, criteria: Dict[str, Any]) -> None:
        data = self.get_items()
        data = [item for item in data if not all(item.get(k) == v for k, v in criteria.items())]
        if not data:
            open(self.__filename, "w").close()
            return
        wb = Workbook()
        ws = wb.active
        ws.append(list(data[0].keys()))
        for item in data:
            ws.append(list(item.values()))
        wb.save(self.__filename)


# -------------------- TXT --------------------
class TXTHandler(FileHandler):
    def __init__(self, filename: str = "vacancies.txt") -> None:
        self.__filename = filename

    def add_items(self, items: List[Dict[str, Any]]) -> None:
        existing = self.get_items() or []
        items_to_add = remove_duplicates(existing, items, key="url")
        if not items_to_add:
            return
        with open(self.__filename, "a", encoding="utf-8") as f:
            for item in items_to_add:
                f.write(str(item) + "\n")

    def get_items(self, criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if not os.path.exists(self.__filename):
            return []
        data = []
        with open(self.__filename, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data.append(eval(line.strip()))
                except Exception:
                    continue
        if criteria:
            data = filter_items(data, criteria)
        return data

    def delete_items(self, criteria: Dict[str, Any]) -> None:
        data = self.get_items()
        data = [item for item in data if not all(item.get(k) == v for k, v in criteria.items())]
        with open(self.__filename, "w", encoding="utf-8") as f:
            for item in data:
                f.write(str(item) + "\n")