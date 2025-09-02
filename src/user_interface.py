# Особенности интерфейса:
# Пользователь вводит поисковый запрос.
# Можно указать количество вакансий для ТОПа.
# Возможна фильтрация по ключевым словам в описании.
# Можно указать диапазон зарплаты.
# Пользователь может фильтровать вакансии по локации.
# Вакансии выводятся в человекочитаемом виде, без списков и словарей.
# Вакансии сохраняются в JSON файл в папку data. (расширяемо для CSV/XLSX/TXT).

import os
from typing import List
from src.get_api import HHAPI
from src.vacancy_get import Vacancy
from src.work_files import JSONHandler
from datetime import datetime

# Папка для хранения JSON файлов
DATA_FOLDER = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_FOLDER, exist_ok=True)


def convert_api_to_vacancy(item: dict) -> Vacancy:
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


def display_vacancy(vac: Vacancy):
    print(f"Название: {vac.title}")
    print(f"Локация: {vac.location}")
    print(f"Дата публикации: {vac.published_at.strftime('%Y-%m-%d %H:%M')}")
    print(f"Ссылка: {vac.url}")
    print(f"Зарплата: {vac.salary}")
    print(f"Описание: {vac.description}")
    print("-" * 40)


def user_interaction():
    print("=== Платформа: HeadHunter ===")
    search_query = input("Введите поисковый запрос: ").strip()
    if not search_query:
        print("Ключевое слово не может быть пустым")
        return

    top_n = input("Введите количество вакансий для вывода в топ N (оставьте пустым для всех): ").strip()
    top_n = int(top_n) if top_n.isdigit() else None

    filter_words = input("Введите ключевые слова для фильтрации вакансий (через пробел): ").split()
    location_filter = input("Введите локацию для фильтрации вакансий (оставьте пустым для пропуска): ").strip()

    salary_range_input = input("Введите диапазон зарплат (пример: 100000-150000, оставьте пустым для пропуска): ").strip()
    if salary_range_input:
        try:
            min_salary, max_salary = map(int, salary_range_input.split("-"))
        except ValueError:
            print("Некорректный формат диапазона зарплат")
            min_salary, max_salary = None, None
    else:
        min_salary, max_salary = None, None

    # Получаем вакансии
    hh_api = HHAPI()
    api_items = hh_api.get_vacancies(search_query)
    if not api_items:
        print("Вакансии не найдены")
        return

    vacancies: List[Vacancy] = [convert_api_to_vacancy(item) for item in api_items]

    # Фильтр по ключевым словам
    if filter_words:
        vacancies = [vac for vac in vacancies if any(word.lower() in vac.description.lower() for word in filter_words)]
        print(f"Найдено {len(vacancies)} вакансий по ключевым словам")

    # Фильтр по локации
    if location_filter:
        vacancies = [vac for vac in vacancies if location_filter.lower() in vac.location.lower()]
        print(f"Найдено {len(vacancies)} вакансий для локации: {location_filter}")

    # Фильтр по диапазону зарплаты
    if min_salary is not None and max_salary is not None:
        vacancies = [vac for vac in vacancies if min_salary <= vac.salary <= max_salary]
        print(f"Найдено {len(vacancies)} вакансий в диапазоне зарплат {min_salary}-{max_salary}")

    if not vacancies:
        print("Вакансии не найдены после фильтрации")
        return

    # Сортировка по зарплате
    vacancies.sort(reverse=True, key=lambda v: v.salary)
    if top_n:
        vacancies = vacancies[:top_n]

    print(f"=== ТОП {len(vacancies)} вакансий ===")
    for vac in vacancies:
        display_vacancy(vac)

    # Сохраняем в JSON в папку data
    json_file_path = os.path.join(DATA_FOLDER, "vacancies.json")
    json_handler = JSONHandler(json_file_path)
    json_handler.add_items([vac.to_dict() for vac in vacancies])
    print(f"Вакансии сохранены в JSON файл ({json_file_path})")