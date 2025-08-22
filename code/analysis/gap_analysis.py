"""
Анализ пробелов в дистрибуционной сети.
"""

import pandas as pd
import numpy as np
from geopy.distance import geodesic
from typing import Dict, List, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class GapAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.population_data = self._load_population_data()
        
    def analyze_gaps(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Анализ пробелов в дистрибуционной сети.
        
        Args:
            df: DataFrame с данными о салонах связи
            
        Returns:
            Словарь с результатами анализа пробелов
        """
        logger.info("Запуск анализа пробелов в дистрибуционной сети")
        
        # Фильтрация салонов Т2
        tele2_df = df[df['name'].str.contains('Tele2|Т2', case=False, na=False)]
        
        # Анализ пробелов на основе населения
        population_gaps = self._analyze_population_gaps(tele2_df)
        
        # Анализ пробелов на основе инфраструктуры
        infrastructure_gaps = self._analyze_infrastructure_gaps(df, tele2_df)
        
        # Анализ конкурентных пробелов
        competitive_gaps = self._analyze_competitive_gaps(df, tele2_df)
        
        return {
            'population_gaps': population_gaps,
            'infrastructure_gaps': infrastructure_gaps,
            'competitive_gaps': competitive_gaps,
            'recommendations': self._generate_gap_recommendations(population_gaps, infrastructure_gaps, competitive_gaps)
        }
    
    def _load_population_data(self) -> Dict[str, int]:
        """Загрузка данных о населении городов."""
        # Здесь можно загрузить реальные данные о населении
        # Пока используем заглушку
        return {
            'Москва': 12600000,
            'Санкт-Петербург': 5400000,
            'Новосибирск': 1620000,
            'Екатеринбург': 1490000,
            'Казань': 1250000,
            # Добавьте данные для других городов
        }
    
    def _analyze_population_gaps(self, tele2_df: pd.DataFrame) -> Dict[str, Any]:
        """Анализ пробелов на основе данных о населении."""
        population_gaps = {}
        
        for city, population in self.population_data.items():
            city_df = tele2_df[tele2_df['city'] == city]
            location_count = len(city_df)
            
            # Расчет количества салонов на душу населения
            if population > 0:
                per_capita = location_count / population * 100000  # на 100k населения
                population_gaps[city] = {
                    'population': population,
                    'locations': location_count,
                    'per_100k': per_capita,
                    'sufficiency': 'Достаточно' if per_capita >= 2 else 'Недостаточно'
                }
        
        return population_gaps
    
    def _analyze_infrastructure_gaps(self, all_df: pd.DataFrame, tele2_df: pd.DataFrame) -> Dict[str, Any]:
        """Анализ пробелов на основе инфраструктуры."""
        infrastructure_gaps = {}
        
        # Поиск районов с развитой инфраструктурой, но без салонов Т2
        developed_areas = all_df[
            (all_df['nearby_shopping_centers_count'] > 2) &
            (all_df['nearby_metro_count'] > 0) &
            (all_df['anchor_tenants_count'] > 1)
        ]
        
        # Исключаем районы, где уже есть салоны Т2
        tele2_coords = tele2_df[['latitude', 'longitude']].dropna().values
        gap_areas = []
        
        for _, area in developed_areas.iterrows():
            if pd.isna(area['latitude']) or pd.isna(area['longitude']):
                continue
                
            # Проверяем, есть ли поблизости салоны Т2
            has_nearby_tele2 = False
            for tele2_coord in tele2_coords:
                distance = geodesic(
                    (area['latitude'], area['longitude']),
                    (tele2_coord[0], tele2_coord[1])
                ).km
                
                if distance < 2.0:  # В радиусе 2 км
                    has_nearby_tele2 = True
                    break
            
            if not has_nearby_tele2:
                gap_areas.append({
                    'location': area['name'] if 'name' in area else 'Неизвестно',
                    'address': area['address'] if 'address' in area else 'Неизвестно',
                    'infrastructure_score': self._calculate_infrastructure_score(area)
                })
        
        infrastructure_gaps['gap_areas'] = gap_areas
        infrastructure_gaps['gap_count'] = len(gap_areas)
        
        return infrastructure_gaps
    
    def _calculate_infrastructure_score(self, area: pd.Series) -> float:
        """Расчет оценки инфраструктуры района."""
        score = 0
        
        if area.get('nearby_shopping_centers_count', 0) > 0:
            score += area['nearby_shopping_centers_count'] * 2
        
        if area.get('nearby_metro_count', 0) > 0:
            score += area['nearby_metro_count'] * 3
        
        if area.get('anchor_tenants_count', 0) > 0:
            score += area['anchor_tenants_count'] * 1.5
        
        if area.get('public_transport_stops_count', 0) > 0:
            score += min(area['public_transport_stops_count'] * 0.5, 3)
        
        return score
    
    def _analyze_competitive_gaps(self, all_df: pd.DataFrame, tele2_df: pd.DataFrame) -> Dict[str, Any]:
        """Анализ конкурентных пробелов."""
        competitive_gaps = {}
        
        # Идентификация операторов
        all_df['operator'] = all_df['name'].apply(self._identify_operator)
        
        # Поиск районов с конкурентами, но без салонов Т2
        competitor_areas = all_df[
            (all_df['operator'].isin(['МТС', 'Билайн', 'МегаФон'])) &
            (~all_df['operator'].isin(['Tele2', 'Другой']))
        ]
        
        # Исключаем районы, где уже есть салоны Т2
        tele2_coords = tele2_df[['latitude', 'longitude']].dropna().values
        gap_areas = []
        
        for _, area in competitor_areas.iterrows():
            if pd.isna(area['latitude']) or pd.isna(area['longitude']):
                continue
                
            # Проверяем, есть ли поблизости салоны Т2
            has_nearby_tele2 = False
            for tele2_coord in tele2_coords:
                distance = geodesic(
                    (area['latitude'], area['longitude']),
                    (tele2_coord[0], tele2_coord[1])
                ).km
                
                if distance < 1.5:  # В радиусе 1.5 км
                    has_nearby_tele2 = True
                    break
            
            if not has_nearby_tele2:
                gap_areas.append({
                    'location': area['name'],
                    'address': area['address'] if 'address' in area else 'Неизвестно',
                    'competitor': area['operator'],
                    'competitor_rating': area.get('rating', 0)
                })
        
        competitive_gaps['gap_areas'] = gap_areas
        competitive_gaps['gap_count'] = len(gap_areas)
        
        return competitive_gaps
    
    def _identify_operator(self, name: str) -> str:
        """Идентификация оператора по названию."""
        name_lower = str(name).lower()
        
        if 'tele2' in name_lower or 'т2' in name_lower:
            return 'Tele2'
        elif 'мтс' in name_lower or 'mts' in name_lower:
            return 'МТС'
        elif 'билайн' in name_lower or 'beeline' in name_lower:
            return 'Билайн'
        elif 'мегафон' in name_lower or 'megafon' in name_lower:
            return 'МегаФон'
        else:
            return 'Другой'
    
    def _generate_gap_recommendations(self, population_gaps: Dict[str, Any], 
                                    infrastructure_gaps: Dict[str, Any], 
                                    competitive_gaps: Dict[str, Any]) -> List[str]:
        """Генерация рекомендаций на основе анализа пробелов."""
        recommendations = []
        
        # Рекомендации на основе населения
        for city, data in population_gaps.items():
            if data['sufficiency'] == 'Недостаточно':
                recommendations.append(
                    f"В городе {city} недостаточное покрытие ({data['per_100k']:.2f} салонов на 100k населения). "
                    "Рекомендуется открытие новых точек"
                )
        
        # Рекомендации на основе инфраструктуры
        if infrastructure_gaps.get('gap_count', 0) > 0:
            recommendations.append(
                f"Выявлено {infrastructure_gaps['gap_count']} районов с развитой инфраструктурой, "
                "но без салонов Т2. Рекомендуется приоритетное размещение в этих районах"
            )
        
        # Рекомендации на основе конкурентов
        if competitive_gaps.get('gap_count', 0) > 0:
            recommendations.append(
                f"Выявлено {competitive_gaps['gap_count']} районов с присутствием конкурентов, "
                "но без салонов Т2. Рекомендуется анализ потенциальной конкуренции"
            )
        
        return recommendations
