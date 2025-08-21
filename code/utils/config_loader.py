"""
Модуль для загрузки и сохранения конфигурации.
"""

import importlib.util
import json
import os
from typing import Any, Dict

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Загрузка конфигурации из Python-файла.
    
    Args:
        config_path: Путь к файлу конфигурации
    
    Returns:
        Словарь с конфигурацией
    """
    try:
        spec = importlib.util.spec_from_file_location("config", config_path)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        
        # Преобразуем модуль в словарь
        config_dict = {}
        for key in dir(config_module):
            if not key.startswith('_'):
                config_dict[key] = getattr(config_module, key)
        
        return config_dict
        
    except Exception as e:
        raise Exception(f"Ошибка при загрузке конфигурации: {str(e)}")

def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Сохранение конфигурации в JSON-файл.
    
    Args:
        config: Словарь с конфигурацией
        config_path: Путь для сохранения файла
    """
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        raise Exception(f"Ошибка при сохранении конфигурации: {str(e)}")
