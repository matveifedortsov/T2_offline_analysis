#!/usr/bin/env python3
"""
Скрипт для инициализации структуры данных проекта.
Запуск: python scripts/init_data_structure.py
"""

import os
import sys

def create_data_structure():
    """Создание структуры каталогов для данных"""
    
    # Основные директории
    directories = [
        'data/raw/links/tele2',
        'data/raw/links/mts',
        'data/raw/links/beeline',
        'data/raw/links/megafon',
        'data/raw/parsed/tele2',
        'data/raw/parsed/mts',
        'data/raw/parsed/beeline',
        'data/raw/parsed/megafon',
        'data/processed/combined',
        'data/processed/combined/city_stats',
        'data/processed/cleaned',
        'data/processed/cleaned/features',
        'data/processed/cleaned/aggregated',
        'data/processed/cleaned/time_series',
        'data/external/population/cities',
        'data/external/population/districts',
        'data/external/economic/income',
        'data/external/economic/retail',
        'data/external/economic/business',
        'data/external/geographic/coordinates',
        'data/external/geographic/infrastructure',
        'data/external/geographic/geo_json/city_borders',
        'data/external/geographic/geo_json/district_borders',
        'data/external/market/telecom',
        'data/external/market/general'
    ]
    
    # Создание директорий
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Создана директория: {directory}")
    
    # Создание README файлов
    readme_files = {
        'data/README.md': '# Данные проекта анализа дистрибуции Т2\n\nОписание структуры данных...',
        'data/external/README.md': '# Внешние данные\n\nОписание необходимых внешних данных...'
    }
    
    for file_path, content in readme_files.items():
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Создан файл: {file_path}")
    
    # Создание .gitkeep файлов
    for directory in directories:
        gitkeep_path = os.path.join(directory, '.gitkeep')
        with open(gitkeep_path, 'w') as f:
            f.write('# Этот файл нужен для сохранения структуры каталогов в Git')
        print(f"Создан файл: {gitkeep_path}")
    
    print("\nСтруктура данных создана успешно!")
    print("Не забудьте добавить внешние данные в data/external/")

if __name__ == "__main__":
    create_data_structure()
