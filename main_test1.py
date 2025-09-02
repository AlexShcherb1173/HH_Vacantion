# Что будет происходить:
# Создаётся объект HHAPI.
# Вызывается метод get_vacancies("Python").
# Полученные вакансии выводятся в консоль (название, компания, город, ссылка).
# Если API недоступно или ошибка сети — ловим исключение.

from src.get_api import HHAPI


def main() -> None:
    hh_api = HHAPI()
    keyword = "Python"

    try:
        vacancies = hh_api.get_vacancies(keyword)
        print(f"Найдено {len(vacancies)} вакансий по запросу '{keyword}':\n")

        # Выведем первые 5 вакансий
        for vac in vacancies[:5]:
            print(f"Название: {vac.get('name')}")
            print(f"Компания: {vac.get('employer', {}).get('name')}")
            print(f"Город: {vac.get('area', {}).get('name')}")
            print(f"Ссылка: {vac.get('alternate_url')}\n")

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
