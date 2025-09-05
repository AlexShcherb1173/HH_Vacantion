# Общие функции вынесены в services.py.
# Дубли удаляются через remove_duplicates принимает три параметра: существующие элементы, новые элементы и
# ключ для сравнения(ключ по url).
# Работает для JSON, CSV, XLSX, TXT.
# Убирает дубликаты по ключу url (или любому другому).
# Если key=None, проверяет весь словарь.
# Фильтрация данных через filter_items по любым критериям и поддерживает сравнение с
# множеством значений (list, tuple, set)..
# Оба метода типизированы и документированы.


from typing import Any, Dict, List, Optional


def remove_duplicates(
    existing: List[Dict[str, Any]], new_items: List[Dict[str, Any]], key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Объединяет два списка словарей, убирая дубликаты по ключу `key`.
    Если key=None, сравнивает полностью словарь."""
    seen = set()
    result = []

    # Добавляем существующие элементы
    for item in existing:
        identifier = item.get(key) if key else tuple(sorted(item.items()))
        if identifier not in seen:
            seen.add(identifier)
            result.append(item)

    # Добавляем новые элементы
    for item in new_items:
        identifier = item.get(key) if key else tuple(sorted(item.items()))
        if identifier not in seen:
            seen.add(identifier)
            result.append(item)

    return result


def filter_items(items: List[Dict], criteria: Optional[Dict] = None) -> List[Dict]:
    """Фильтрует список словарей по заданным критериям.
    :param items: список словарей
    :param criteria: словарь критериев фильтрации
    :return: отфильтрованный список словарей"""
    if not criteria:
        return items
    filtered = []
    for item in items:
        match = True
        for key, value in criteria.items():
            if key not in item:
                match = False
                break
            if isinstance(value, (list, tuple, set)):
                if item[key] not in value:
                    match = False
                    break
            else:
                if item[key] != value:
                    match = False
                    break
        if match:
            filtered.append(item)
    return filtered
