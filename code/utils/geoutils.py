"""
Географические утилиты.
"""

from geopy.distance import geodesic
from typing import Tuple, Optional

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Расчет расстояния между двумя точками в километрах.
    
    Args:
        lat1: Широта первой точки
        lon1: Долгота первой точки
        lat2: Широта второй точки
        lon2: Долгота второй точки
    
    Returns:
        Расстояние в километрах
    """
    return geodesic((lat1, lon1), (lat2, lon2)).km

def get_coordinates_from_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Получение координат по адресу (заглушка, можно интегрировать с API геокодера).
    
    Args:
        address: Адрес для геокодирования
    
    Returns:
        Кортеж (широта, долгота) или None
    """
    # Здесь можно интегрировать с API Яндекс.Карт или других геокодеров
    # Пока возвращаем заглушку
    return None

def is_point_in_radius(lat1: float, lon1: float, lat2: float, lon2: float, radius_km: float) -> bool:
    """
    Проверка, находится ли точка в пределах заданного радиуса.
    
    Args:
        lat1: Широта центральной точки
        lon1: Долгота центральной точки
        lat2: Широта проверяемой точки
        lon2: Долгота проверяемой точки
        radius_km: Радиус в километрах
    
    Returns:
        True, если точка находится в радиусе, иначе False
    """
    distance = calculate_distance(lat1, lon1, lat2, lon2)
    return distance <= radius_km
