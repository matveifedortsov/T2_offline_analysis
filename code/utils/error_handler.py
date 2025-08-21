"""
Обработка ошибок и повторные попытки.
"""

import time
import logging
from typing import Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)

def retry_on_error(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Декоратор для повторных попыток при ошибках.
    
    Args:
        max_retries: Максимальное количество попыток
        delay: Задержка между попытками в секундах
        backoff: Множитель для увеличения задержки
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            current_delay = delay
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Превышено максимальное количество попыток для {func.__name__}: {str(e)}")
                        raise
                    
                    logger.warning(f"Ошибка в {func.__name__} (попытка {retries}/{max_retries}): {str(e)}")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return None
        return wrapper
    return decorator

def log_exceptions(func: Callable) -> Callable:
    """
    Декоратор для логирования исключений.
    
    Args:
        func: Функция для обертывания
    
    Returns:
        Обернутая функция
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Исключение в {func.__name__}: {str(e)}")
            raise
    return wrapper
