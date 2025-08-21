"""
Модуль для работы с файлами.
"""

import json
import csv
import pandas as pd
from typing import Any, Dict, List

def read_json(file_path: str) -> Any:
    """Чтение JSON-файла."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(data: Any, file_path: str, indent: int = 4) -> None:
    """Запись данных в JSON-файл."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)

def read_csv(file_path: str) -> List[Dict[str, Any]]:
    """Чтение CSV-файла."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write_csv(data: List[Dict[str, Any]], file_path: str) -> None:
    """Запись данных в CSV-файл."""
    if not data:
        return
        
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def read_dataframe(file_path: str, **kwargs) -> pd.DataFrame:
    """Чтение данных в DataFrame."""
    return pd.read_csv(file_path, **kwargs)

def write_dataframe(df: pd.DataFrame, file_path: str, **kwargs) -> None:
    """Запись DataFrame в файл."""
    df.to_csv(file_path, **kwargs)
