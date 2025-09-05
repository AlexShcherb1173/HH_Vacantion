# Что тут тестируется:
# VacancyAPI — нельзя создать напрямую (абстрактный класс).
# _connect() — успешное подключение и ошибка при плохом статусе.
# Есть фикстура fake_vacancies с тестовыми данными.
# get_vacancies() — возврат списка вакансий при корректном ответе.
# Ошибка в get_vacancies() при статусе 404.
# В тесте test_get_vacancies_success используется фикстура вместо хардкода.


from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.get_api import HHAPI, VacancyAPI


@pytest.fixture
def fake_vacancies() -> list[dict[str, Any]]:
    """Фикстура с тестовыми вакансиями."""
    return [
        {
            "name": "Python Developer",
            "employer": {"name": "TestCompany"},
            "area": {"name": "Москва"},
            "alternate_url": "https://hh.ru/vacancy/123",
        },
        {
            "name": "Data Scientist",
            "employer": {"name": "AI Inc"},
            "area": {"name": "Санкт-Петербург"},
            "alternate_url": "https://hh.ru/vacancy/456",
        },
    ]


def test_vacancyapi_is_abstract() -> None:
    """Проверяем, что VacancyAPI нельзя создать напрямую."""
    with pytest.raises(TypeError):
        _ = VacancyAPI()


@patch("src.get_api.requests.get")
def test_connect_success(mock_get: MagicMock) -> None:
    """Проверка успешного подключения к API."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.reason = "OK"
    mock_get.return_value = mock_response

    hh = HHAPI()
    response = hh._connect()
    assert response.status_code == 200
    mock_get.assert_called_once_with(hh._base_url, timeout=10)


@patch("src.get_api.requests.get")
def test_connect_failure_status_code(mock_get: MagicMock) -> None:
    """Проверяем, что при плохом статусе выбрасывается ошибка."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.reason = "Internal Server Error"
    mock_get.return_value = mock_response

    hh = HHAPI()
    with pytest.raises(ConnectionError):
        hh._connect()


@patch("src.get_api.requests.get")
def test_get_vacancies_success(mock_get: MagicMock, fake_vacancies: list[dict[str, Any]]) -> None:
    """Проверка получения вакансий по ключевому слову."""
    # Первый вызов — _connect()
    mock_response_connect = MagicMock()
    mock_response_connect.status_code = 200
    mock_response_connect.json.return_value = {}

    # Второй вызов — get_vacancies()
    mock_response_vacancies = MagicMock()
    mock_response_vacancies.status_code = 200
    mock_response_vacancies.json.return_value = {"items": fake_vacancies}

    mock_get.side_effect = [mock_response_connect, mock_response_vacancies]

    hh = HHAPI()
    vacancies = hh.get_vacancies("Python")

    assert isinstance(vacancies, list)
    assert len(vacancies) == 2
    assert vacancies[0]["name"] == "Python Developer"
    assert vacancies[1]["employer"]["name"] == "AI Inc"


@patch("src.get_api.requests.get")
def test_get_vacancies_bad_status_code(mock_get: MagicMock) -> None:
    """Проверка ошибки при плохом статусе ответа в get_vacancies."""
    mock_response_connect = MagicMock()
    mock_response_connect.status_code = 200
    mock_response_connect.json.return_value = {}

    mock_response_vacancies = MagicMock()
    mock_response_vacancies.status_code = 404
    mock_response_vacancies.reason = "Not Found"

    mock_get.side_effect = [mock_response_connect, mock_response_vacancies]

    hh = HHAPI()
    with pytest.raises(ConnectionError):
        hh.get_vacancies("Python")
