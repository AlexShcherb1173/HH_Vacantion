# Что реализовано:
# Получение вакансий через HHAPI по ключевому слову.
# Конвертация каждого элемента API в объект Vacancy.
# Сохранение вакансий во все форматы файлов (JSON, CSV, XLSX, TXT).
# Возможность фильтрации вакансий по локации в JSON-файле.
# Возможность удаления вакансии по URL из JSON-файла.
# Простой CLI-интерфейс для пользователя.

from src.get_api import HHAPI
from src.vacancy_get import Vacancy
from src.work_files import JSONHandler, CSVHandler, XLSXHandler, TXTHandler

def convert_api_to_vacancy(item: dict) -> Vacancy:
    """Конвертирует словарь API hh.ru в объект Vacancy"""
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


def main():
    keyword = input("Введите ключевое слово для поиска вакансий: ").strip()
    if not keyword:
        print("Ключевое слово не может быть пустым")
        return

    # ------------------ Получаем вакансии с hh.ru ------------------
    hh_api = HHAPI()
    api_items = hh_api.get_vacancies(keyword)

    if not api_items:
        print("Вакансии не найдены")
        return

    vacancies = [convert_api_to_vacancy(item) for item in api_items]

    print(f"Найдено {len(vacancies)} вакансий")

    # ------------------ Сохраняем вакансии ------------------
    handlers = [
        JSONHandler(),
        CSVHandler(),
        XLSXHandler(),
        TXTHandler()
    ]

    for handler in handlers:
        handler.add_items([vac.to_dict() for vac in vacancies])
        #handler.add_items([vac.__dict__ for vac in vacancies])
        print(f"Вакансии сохранены в {handler.__class__.__name__}")

    # ------------------ Работа с файлами ------------------
    # Пример фильтрации JSON
    json_handler = JSONHandler()
    location_filter = input("Фильтровать по локации (оставьте пустым для пропуска): ").strip()
    if location_filter:
        filtered = json_handler.get_items(criteria={"location": location_filter})
        print(f"Найдено {len(filtered)} вакансий для локации {location_filter}:")
        for vac in filtered:
            print(f"{vac['title']} | {vac['location']} | {vac['salary']} | {vac['url']}")

    # Пример удаления вакансий по URL
    delete_url = input("Введите URL вакансии для удаления (оставьте пустым для пропуска): ").strip()
    if delete_url:
        json_handler.delete_items(criteria={"url": delete_url})
        print(f"Вакансия {delete_url} удалена из JSON файла")


if __name__ == "__main__":
    main()