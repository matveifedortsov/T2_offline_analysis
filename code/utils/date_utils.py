"""
Утилиты для работы с датами и временем.
"""

from datetime import datetime, timedelta
from typing import List  # Добавьте этот импорт

def format_date(date_obj: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Форматирование даты в строку.
    
    Args:
        date_obj: Объект даты/времени
        format_str: Строка формата
    
    Returns:
        Отформатированная строка даты
    """
    return date_obj.strftime(format_str)

def get_current_timestamp() -> str:
    """
    Получение текущей временной метки.
    
    Returns:
        Строка с текущей временной меткой
    """
    return format_date(datetime.now())

def parse_date(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Парсинг строки в объект даты/времени.
    
    Args:
        date_str: Строка с датой
        format_str: Строка формата
    
    Returns:
        Объект даты/времени
    """
    return datetime.strptime(date_str, format_str)

def get_date_range(start_date: datetime, end_date: datetime) -> List[datetime]:
    """
    Получение списка дат в диапазоне.
    
    Args:
        start_date: Начальная дата
        end_date: Конечная дата
    
    Returns:
        Список дат в диапазоне
    """
    dates = []
    current_date = start_date
    
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    
    return dates
