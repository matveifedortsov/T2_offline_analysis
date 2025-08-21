"""
Модуль для валидации и очистки данных.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List

def validate_data(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Валидация данных.
    
    Args:
        data: Данные для валидации
        required_fields: Обязательные поля
    
    Returns:
        True, если данные валидны, иначе False
    """
    for field in required_fields:
        if field not in data or not data[field]:
            return False
    return True

def clean_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Очистка данных.
    
    Args:
        data: Данные для очистки
    
    Returns:
        Очищенные данные
    """
    cleaned_data = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            # Удаляем лишние пробелы и переносы строк
            cleaned_value = ' '.join(value.split()).strip()
            cleaned_data[key] = cleaned_value
        elif isinstance(value, (list, dict)) and not value:
            # Пропускаем пустые списки и словари
            continue
        else:
            cleaned_data[key] = value
    
    return cleaned_data

def normalize_phone(phone: str) -> str:
    """
    Нормализация телефонного номера.
    
    Args:
        phone: Телефонный номер
    
    Returns:
        Нормализованный телефонный номер
    """
    # Удаляем все нецифровые символы
    digits = ''.join(filter(str.isdigit, phone))
    
    # Приводим к формату +7XXXXXXXXXX
    if digits.startswith('8') and len(digits) == 11:
        return '+7' + digits[1:]
    elif digits.startswith('7') and len(digits) == 11:
        return '+' + digits
    elif len(digits) == 10:
        return '+7' + digits
    
    return phone
