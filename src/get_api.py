# Что здесь есть:
# Абстрактный класс VacancyAPI с методами:
# _connect() — подключение к API (без реализации).
# get_vacancies() — получение вакансий (без реализации).
# Класс HHAPI, который:
# Наследует абстрактный класс.
# Приватный атрибут __base_url.
# Приватный метод _connect() проверяет доступность API.
# Метод get_vacancies() принимает ключевое слово, формирует параметры (text, per_page), делает запрос и
# возвращает список словарей из ключа "items".

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import requests


class VacancyAPI(ABC):
    """Абстрактный класс для работы с API сервисов вакансий."""

    @abstractmethod
    def _connect(self) -> requests.Response:
        """Подключение к API. Должно возвращать объект Response."""
        pass

    @abstractmethod
    def get_vacancies(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Получение списка вакансий по ключевому слову.
        :param keyword: Ключевое слово для поиска.
        :return: Список вакансий в виде списка словарей.
        """
        pass


class HHAPI(VacancyAPI):
    """Класс для работы с API hh.ru."""

    def __init__(self) -> None:
        self.__base_url = "https://api.hh.ru/vacancies"
        self.__last_response: requests.Response | None = None

    def _connect(self) -> requests.Response:
        """Приватный метод подключения к API."""
        try:
            response = requests.get(self.__base_url, timeout=10)
            if response.status_code != 200:
                raise ConnectionError(
                    f"Ошибка подключения: {response.status_code} {response.reason}"
                )
            self.__last_response = response
            return response
        except requests.RequestException as e:
            raise ConnectionError(f"Ошибка сети: {e}")

    def get_vacancies(self, keyword: str) -> List[Dict[str, Any]]:
        """Получение вакансий с hh.ru по ключевому слову."""
        # Проверяем соединение перед запросом
        self._connect()

        params = {
            "text": keyword,
            "per_page": 20,  # кол-во вакансий на страницу
            "page": 0,       # первая страница
        }

        try:
            response = requests.get(self.__base_url, params=params, timeout=10)
            if response.status_code != 200:
                raise ConnectionError(
                    f"Ошибка при получении вакансий: {response.status_code} {response.reason}"
                )
            data = response.json()
            return data.get("items", [])
        except requests.RequestException as e:
            raise ConnectionError(f"Ошибка запроса вакансий: {e}")