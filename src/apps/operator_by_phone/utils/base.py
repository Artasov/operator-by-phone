import re


def normalize_phone_number(phone_number: str) -> str:
    """
    Убираем лишние символы, приводим к формату:
    - Удаляем +, пробелы, скобки и т.д.
    - Меняем ведущую '8' на '7' (если это российский номер)
    - В итоге хотим 11-значный номер, начинающийся на '7'.
      Пример: +7 (917) 345-32-23 -> 79173453223
    """
    print(f"Исходный номер: {phone_number}")
    cleaned = re.sub(r'\D', '', phone_number)  # оставляем только цифры
    if len(cleaned) == 11 and cleaned.startswith('8'):
        cleaned = '7' + cleaned[1:]
    elif len(cleaned) == 10:
        cleaned = '7' + cleaned
    print(f"Нормализованный номер: {cleaned}")
    return cleaned
