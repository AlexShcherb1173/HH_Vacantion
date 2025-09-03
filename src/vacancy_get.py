# Что реализовано:
# __slots__ для экономии памяти.
# 6 атрибутов: title, location, published_at, url, salary, description.
# Приватные методы валидации: проверяют корректность данных при инициализации.
# Магические методы сравнения: __lt__, __le__, __eq__, __gt__, __ge__ — по зарплате.
# Если зарплата не указана — устанавливается 0.

from datetime import datetime
from typing import Optional, Union


class Vacancy:
    """Класс, представляющий вакансию с основными атрибутами и сравнением по зарплате."""

    __slots__ = (
        "__title",
        "__location",
        "__published_at",
        "__url",
        "__salary",
        "__description",
    )

    def __init__(
        self,
        title: str,
        location: str,
        salary: Union[int, None],
        description: str,
        published_at: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        """Инициализация вакансии.
        :param title: Название вакансии
        :param location: Локация вакансии
        :param published_at: Дата публикации в формате ISO
        :param url: Ссылка на вакансию
        :param salary: Зарплата (если не указана, 0)
        :param description: Краткое описание вакансии"""
        self.__title = self.__validate_title(title)
        self.__location = self.__validate_location(location)
        self.__published_at = self.__validate_date(published_at)
        self.__url = self.__validate_url(url)
        self.__salary = self.__validate_salary(salary)
        self.__description = self.__validate_description(description)

    # ================= Валидация =================

    def __validate_title(self, value: str) -> str:
        """Проверка и нормализация названия вакансии."""
        if not value or not isinstance(value, str):
            raise ValueError("Название вакансии должно быть строкой и не пустым")
        return value.strip()

    def __validate_location(self, value: str) -> str:
        """Проверка и нормализация локации вакансии."""
        if not value or not isinstance(value, str):
            return "Не указано"
        return value.strip()

    def __validate_date(self, value: Optional[str]) -> datetime:
        """Проверка и нормализация даты вакансии."""
        if value is None:
            raise ValueError("Дата вакансии отсутствует")
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            raise ValueError("Некорректная дата публикации вакансии")

    def __validate_url(self, value: Optional[str]) -> str:
        """Проверка и нормализация ссылки на вакансию."""
        if not isinstance(value, str) or not value.startswith("http"):
            raise ValueError("Некорректная ссылка на вакансию")
        return value

    def __validate_salary(self, value: Union[int, None]) -> int:
        """Проверка и нормализация значения зарплаты."""
        if value is None:
            return 0
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Зарплата должна быть положительным числом или None")
        return int(value)

    def __validate_description(self, value: str) -> str:
        """Проверка и нормализация описания вакансии."""
        if not value or not isinstance(value, str):
            return "Описание не указано"
        return value.strip()

    def to_dict(self) -> dict:
        """Возвращает словари всех атрибутов вакансии"""
        return {
            "title": self.title,
            "location": self.location,
            "published_at": self.published_at.isoformat(),
            "url": self.url,
            "salary": self.salary,
            "description": self.description,
        }

    # ================= Свойства =================

    @property
    def title(self) -> str:
        return self.__title

    @property
    def location(self) -> str:
        return self.__location

    @property
    def published_at(self) -> datetime:
        return self.__published_at

    @property
    def url(self) -> str:
        return self.__url

    @property
    def salary(self) -> int:
        return self.__salary

    @property
    def description(self) -> str:
        return self.__description

    # ================= Сравнение =================

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.salary == other.salary

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.salary < other.salary

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.salary <= other.salary

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.salary > other.salary

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.salary >= other.salary

    # ================= Представление =================

    def __repr__(self) -> str:
        return f"Vacancy(title={self.title!r}, salary={self.salary}, " f"location={self.location!r}, url={self.url!r})"
