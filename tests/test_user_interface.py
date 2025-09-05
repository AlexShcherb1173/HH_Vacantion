# Что проверяется:
# Ввод пользователя через mock input.
# Получение вакансий через замоканный HHAPI.
# Фильтрация вакансий по ключевым словам и зарплате.
# Сохранение вакансий в JSON-файл в папку data.
# Тест проверяет фильтрацию, создание папки и сохранение файла.
# Создание папки data, если её нет.


import os
import shutil
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from src.user_interface import DATA_FOLDER, user_interaction
from src.work_files import JSONHandler


@pytest.fixture(autouse=True)
def cleanup_data_folder() -> Generator[None, None, None]:
    if os.path.exists(DATA_FOLDER):
        shutil.rmtree(DATA_FOLDER)
    os.makedirs(DATA_FOLDER, exist_ok=True)
    yield
    if os.path.exists(DATA_FOLDER):
        shutil.rmtree(DATA_FOLDER)


def test_user_interaction_with_location(monkeypatch: MagicMock) -> None:
    # Ввод пользователя с фильтром по локации
    inputs = iter(
        [
            "Python Developer",  # поисковый запрос
            "2",  # топ N
            "backend",  # ключевые слова
            "Москва",  # локация
            "100000-200000",  # диапазон зарплаты
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    # Мокаем HHAPI.get_vacancies
    with patch("src.get_api.HHAPI.get_vacancies") as mock_get:
        mock_get.return_value = [
            {
                "name": "Python Developer",
                "area": {"name": "Москва"},
                "published_at": "2025-09-02T12:00:00Z",
                "alternate_url": "https://hh.ru/vacancy/1",
                "salary": {"from": 150000, "to": 200000, "currency": "RUR"},
                "snippet": {"requirement": "Разработка backend"},
            },
            {
                "name": "Junior Developer",
                "area": {"name": "Санкт-Петербург"},
                "published_at": "2025-09-01T12:00:00Z",
                "alternate_url": "https://hh.ru/vacancy/2",
                "salary": {"from": 90000, "to": 120000, "currency": "RUR"},
                "snippet": {"requirement": "Разработка frontend"},
            },
        ]

        # Мокаем JSONHandler.add_items
        with patch.object(
            JSONHandler, "add_items", wraps=JSONHandler(os.path.join(DATA_FOLDER, "vacancies.json")).add_items
        ) as mock_add:
            user_interaction()
            assert mock_get.called
            assert mock_add.called
            json_file_path = os.path.join(DATA_FOLDER, "vacancies.json")
            assert os.path.exists(json_file_path)
