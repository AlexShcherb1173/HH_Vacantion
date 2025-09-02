# Что проверяется:
# Создание вакансии с валидными данными.
# Зарплата None превращается в 0.
# Проверка, что None в зарплате конвертируется в 0.
# Ошибки при пустом названии и неправильной ссылке.
# Сравнение вакансий по зарплате (<, >, ==).
# Значения по умолчанию для описания и локации.
# Mock API возвращает тестовые данные hh.ru.
# Создание объектов Vacancy через конвертер convert_api_to_vacancy.
#

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from src.get_api import HHAPI
from src.vacancy_get import Vacancy

@pytest.fixture
def fake_api_response():
    """Фейковые данные, которые возвращает hh.ru API"""
    return [
        {
            "name": "Python Developer",
            "employer": {"name": "TestCompany"},
            "area": {"name": "Москва"},
            "published_at": "2025-09-02T12:00:00Z",
            "alternate_url": "https://hh.ru/vacancy/123",
            "salary": {"from": 120000, "to": 150000, "currency": "RUR"},
            "snippet": {"requirement": "Опыт работы 2+ года"},
        },
        {
            "name": "Junior Python Developer",
            "employer": {"name": "AI Inc"},
            "area": {"name": "Санкт-Петербург"},
            "published_at": "2025-09-01T10:00:00Z",
            "alternate_url": "https://hh.ru/vacancy/456",
            "salary": None,
            "snippet": {"requirement": "Без опыта"},
        },
    ]


def test_vacancy_creation_valid():
    vac = Vacancy(
        title="Python Developer",
        location="Москва",
        published_at="2025-09-02T12:00:00Z",
        url="https://hh.ru/vacancy/123",
        salary=150000,
        description="Разработка backend"
    )
    assert vac.title == "Python Developer"
    assert vac.location == "Москва"
    assert isinstance(vac.published_at, datetime)
    assert vac.url == "https://hh.ru/vacancy/123"
    assert vac.salary == 150000
    assert vac.description == "Разработка backend"


def test_vacancy_salary_none():
    vac = Vacancy(
        title="Junior Developer",
        location="Санкт-Петербург",
        published_at="2025-09-02T12:00:00Z",
        url="https://hh.ru/vacancy/456",
        salary=None,
        description="Тестовое описание"
    )
    # Зарплата по умолчанию 0
    assert vac.salary == 0


def test_vacancy_invalid_title():
    with pytest.raises(ValueError):
        Vacancy(
            title="",
            location="Москва",
            published_at="2025-09-02T12:00:00Z",
            url="https://hh.ru/vacancy/123",
            salary=100000,
            description="Описание"
        )


def test_vacancy_invalid_url():
    with pytest.raises(ValueError):
        Vacancy(
            title="Python Developer",
            location="Москва",
            published_at="2025-09-02T12:00:00Z",
            url="ftp://bad-url",
            salary=100000,
            description="Описание"
        )


def test_vacancy_comparison():
    vac1 = Vacancy(
        title="Vac1",
        location="Москва",
        published_at="2025-09-02T12:00:00Z",
        url="https://hh.ru/vacancy/1",
        salary=100000,
        description="Desc1"
    )
    vac2 = Vacancy(
        title="Vac2",
        location="Санкт-Петербург",
        published_at="2025-09-02T12:00:00Z",
        url="https://hh.ru/vacancy/2",
        salary=150000,
        description="Desc2"
    )

    assert vac1 < vac2
    assert vac2 > vac1
    assert vac1 != vac2

    vac3 = Vacancy(
        title="Vac3",
        location="Казань",
        published_at="2025-09-02T12:00:00Z",
        url="https://hh.ru/vacancy/3",
        salary=100000,
        description="Desc3"
    )

    assert vac1 == vac3
    assert vac1 <= vac3
    assert vac1 >= vac3


def test_vacancy_default_description_location():
    vac = Vacancy(
        title="Vacancy",
        location="",
        published_at="2025-09-02T12:00:00Z",
        url="https://hh.ru/vacancy/1",
        salary=None,
        description=""
    )
    assert vac.description == "Описание не указано"
    assert vac.location == "Не указано"
    assert vac.salary == 0

def convert_api_to_vacancy(item: dict) -> Vacancy:
    """Помощник для создания объекта Vacancy из данных API"""
    salary_data = item.get("salary")
    salary = salary_data.get("from") if salary_data else None

    return Vacancy(
        title=item.get("name"),
        location=item.get("area", {}).get("name", "Не указано"),
        published_at=item.get("published_at"),
        url=item.get("alternate_url"),
        salary=salary,
        description=item.get("snippet", {}).get("requirement", "Описание не указано")
    )


@patch("src.get_api.requests.get")
def test_hhapi_to_vacancy(mock_get, fake_api_response):
    """Интеграционный тест: получение вакансий из hh API и создание объектов Vacancy"""
    # Поддельные ответы API
    mock_response_connect = MagicMock()
    mock_response_connect.status_code = 200
    mock_response_connect.json.return_value = {}

    mock_response_vacancies = MagicMock()
    mock_response_vacancies.status_code = 200
    mock_response_vacancies.json.return_value = {"items": fake_api_response}

    mock_get.side_effect = [mock_response_connect, mock_response_vacancies]

    hh = HHAPI()
    api_items = hh.get_vacancies("Python")

    vacancies = [convert_api_to_vacancy(item) for item in api_items]

    assert len(vacancies) == 2

    # Проверяем первый объект
    vac1 = vacancies[0]
    assert vac1.title == "Python Developer"
    assert vac1.location == "Москва"
    assert vac1.salary == 120000
    assert vac1.description == "Опыт работы 2+ года"
    assert isinstance(vac1.published_at, datetime)

    # Проверяем второй объект
    vac2 = vacancies[1]
    assert vac2.title == "Junior Python Developer"
    assert vac2.location == "Санкт-Петербург"
    assert vac2.salary == 0  # None -> 0
    assert vac2.description == "Без опыта"