"""
Модуль для настройки логирования.
"""

import logging
import os
from datetime import datetime
from typing import Optional

def setup_logger(name: str = __name__, 
                log_level: int = logging.INFO,
                log_file: Optional[str] = None) -> logging.Logger:
    """
    Настройка логгера.
    
    Args:
        name: Имя логгера
        log_level: Уровень логирования
        log_file: Путь к файлу для записи логов (опционально)
    
    Returns:
        Настроенный логгер
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Форматтер
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Обработчик для файла (если указан)
    if log_file:
        # Создаем директорию для логов, если не существует
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str = __name__) -> logging.Logger:
    """
    Получение логгера с указанным именем.
    
    Args:
        name: Имя логгера
    
    Returns:
        Логгер
    """
    return logging.getLogger(name)
