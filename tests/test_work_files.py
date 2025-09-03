# Что проверяется:
# Добавление вакансий во все типы файлов (JSON, CSV, XLSX, TXT).
# Проверка, что дубликаты не добавляются.
# Фильтрация по критериям (например, location).
# Удаление вакансий по критериям.
# Полное удаление всех записей.
# Удаление вакансий проверяет, что все элементы с указанными критериями удалены.
# Подходит для всех четырёх хэндлеров: JSON, CSV, XLSX, TXT.

from pathlib import Path
from typing import Type

# import os
# import pytest
# from src.work_files import JSONHandler, CSVHandler, XLSXHandler, TXTHandler
#
# # Фейковые вакансии для тестирования
# fake_vacancies = [
#     {
#         "title": "Python Developer",
#         "location": "Москва",
#         "published_at": "2025-09-02T12:00:00Z",
#         "url": "https://hh.ru/vacancy/123",
#         "salary": 150000,
#         "description": "Разработка backend"
#     },
#     {
#         "title": "Junior Python Developer",
#         "location": "Санкт-Петербург",
#         "published_at": "2025-09-01T10:00:00Z",
#         "url": "https://hh.ru/vacancy/456",
#         "salary": 0,
#         "description": "Без опыта"
#     },
# ]
#
#
# @pytest.mark.parametrize("HandlerClass, filename", [
#     (JSONHandler, "test_vacancies.json"),
#     (CSVHandler, "test_vacancies.csv"),
#     (XLSXHandler, "test_vacancies.xlsx"),
#     (TXTHandler, "test_vacancies.txt"),
# ])
# def test_file_handler_add_get_delete(tmp_path, HandlerClass, filename):
#     file_path = tmp_path / filename
#     handler = HandlerClass(str(file_path))
#
#     # ------------------ Добавление ------------------
#     handler.add_items(fake_vacancies)
#     items = handler.get_items()
#     assert len(items) == 2
#     urls = [item["url"] for item in items]
#     assert "https://hh.ru/vacancy/123" in urls
#     assert "https://hh.ru/vacancy/456" in urls
#
#     # ------------------ Проверка добавления дубликатов ------------------
#     handler.add_items([fake_vacancies[0]])  # добавляем дубликат
#     items = handler.get_items()
#     assert len(items) == 2  # дубликат не добавился
#
#     # ------------------ Фильтрация ------------------
#     filtered = handler.get_items(criteria={"location": "Москва"})
#     assert len(filtered) == 1
#     assert filtered[0]["location"] == "Москва"
#
#     # ------------------ Удаление ------------------
#     handler.delete_items(criteria={"url": "https://hh.ru/vacancy/123"})
#     items_after_delete = handler.get_items()
#     urls_after_delete = [item["url"] for item in items_after_delete]
#     assert "https://hh.ru/vacancy/123" not in urls_after_delete
#     assert "https://hh.ru/vacancy/456" in urls_after_delete
#
#     # ------------------ Удаление всех ------------------
#     salary_criteria = "0" if HandlerClass in [CSVHandler, XLSXHandler] else 0
#     handler.delete_items(criteria={"salary": salary_criteria})
#     assert handler.get_items() == []
import pytest

from src.work_files import CSVHandler, FileHandler, JSONHandler, TXTHandler, XLSXHandler

fake_vacancies = [
    {
        "title": "Senior Python Developer",
        "location": "Москва",
        "published_at": "2025-09-01T12:00:00Z",
        "url": "https://hh.ru/vacancy/123",
        "salary": 150000,
        "description": "Опыт разработки backend",
    },
    {
        "title": "Junior Python Developer",
        "location": "Санкт-Петербург",
        "published_at": "2025-09-01T10:00:00Z",
        "url": "https://hh.ru/vacancy/456",
        "salary": 0,
        "description": "Без опыта",
    },
]


@pytest.mark.parametrize(
    "HandlerClass, filename",
    [
        (JSONHandler, "test_vacancies.json"),
        (CSVHandler, "test_vacancies.csv"),
        (XLSXHandler, "test_vacancies.xlsx"),
        (TXTHandler, "test_vacancies.txt"),
    ],
)
def test_file_handler_add_get_delete(tmp_path: Path, HandlerClass: Type[FileHandler], filename: str) -> None:
    file_path = tmp_path / filename
    handler = HandlerClass(str(file_path))

    # ------------------ Добавление ------------------
    handler.add_items(fake_vacancies)
    items = handler.get_items()
    assert len(items) == 2
    urls = [item["url"] for item in items]
    assert "https://hh.ru/vacancy/123" in urls
    assert "https://hh.ru/vacancy/456" in urls

    # ------------------ Проверка добавления дубликатов ------------------
    handler.add_items([fake_vacancies[0]])  # добавляем дубликат
    items = handler.get_items()
    assert len(items) == 2  # дубликат не добавился

    # ------------------ Фильтрация ------------------
    filtered = handler.get_items(criteria={"location": "Москва"})
    assert len(filtered) == 1
    assert filtered[0]["location"] == "Москва"

    filtered_multi = handler.get_items(criteria={"location": ["Москва", "Санкт-Петербург"]})
    assert len(filtered_multi) == 2

    # ------------------ Удаление ------------------
    handler.delete_items(criteria={"url": "https://hh.ru/vacancy/123"})
    items_after_delete = handler.get_items()
    urls_after_delete = [item["url"] for item in items_after_delete]
    assert "https://hh.ru/vacancy/123" not in urls_after_delete
    assert "https://hh.ru/vacancy/456" in urls_after_delete

    # ------------------ Удаление всех ------------------
    handler.delete_items(criteria={"salary": 0})
    assert handler.get_items() == []
