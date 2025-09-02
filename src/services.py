# Общие функции вынесены в services.py.
# Дубли удаляются через remove_duplicates (ключ по url).
# Фильтрация данных через filter_items.

from typing import List, Dict, Any


def remove_duplicates(existing: List[Dict[str, Any]], new_items: List[Dict[str, Any]], key: str = "url") -> List[
    Dict[str, Any]]:
    """
    Убирает дубли из списка словарей по указанному ключу.

    :param existing: Существующие данные.
    :param new_items: Новые данные для добавления.
    :param key: Ключ для определения уникальности.
    :return: Список новых элементов без дубликатов.
    """
    existing_keys = {item[key] for item in existing}
    return [item for item in new_items if item[key] not in existing_keys]


def filter_items(items: List[Dict[str, Any]], criteria: dict) -> List[Dict[str, Any]]:
    """
    Фильтрует список словарей по заданным критериям.

    :param items: Список словарей.
    :param criteria: Словарь с ключом-значением для фильтрации.
    :return: Отфильтрованный список словарей.
    """
    filtered = items
    for k, v in criteria.items():
        filtered = [item for item in filtered if item.get(k) == v]
    return filtered