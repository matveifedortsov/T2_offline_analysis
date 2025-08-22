"""
Анализ конкурентов.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class CompetitorAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    def analyze_competitors(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Анализ конкурентной среды.
        
        Args:
            df: DataFrame с данными о салонах связи
            
        Returns:
            Словарь с результатами анализа конкурентов
        """
        logger.info("Запуск анализа конкурентной среды")
        
        # Идентификация операторов
        df['operator'] = df['name'].apply(self._identify_operator)
        
        # Основные метрики по операторам
        operator_stats = self._calculate_operator_stats(df)
        
        # Анализ расположения относительно конкурентов
        proximity_analysis = self._analyze_competitor_proximity(df)
        
        # Сравнительный анализ
        comparative_analysis = self._comparative_analysis(df)
        
        return {
            'operator_stats': operator_stats,
            'proximity_analysis': proximity_analysis,
            'comparative_analysis': comparative_analysis,
            'recommendations': self._generate_competitor_recommendations(operator_stats, proximity_analysis)
        }
    
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
    
    def _calculate_operator_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Расчет статистики по операторам."""
        if 'operator' not in df.columns:
            return {}
            
        stats = {}
        
        for operator in df['operator'].unique():
            operator_df = df[df['operator'] == operator]
            stats[operator] = {
                'count': len(operator_df),
                'avg_rating': operator_df['rating'].mean() if 'rating' in operator_df.columns else 0,
                'avg_reviews': operator_df['reviews_count'].mean() if 'reviews_count' in operator_df.columns else 0,
                'cities_covered': operator_df['city'].nunique()
            }
        
        return stats
    
    def _analyze_competitor_proximity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Анализ близости к конкурентам."""
        # Фильтрация салонов Т2
        tele2_df = df[df['operator'] == 'Tele2']
        
        proximity_analysis = {}
        
        for _, tele2_row in tele2_df.iterrows():
            if pd.isna(tele2_row['latitude']) or pd.isna(tele2_row['longitude']):
                continue
                
            # Поиск ближайших конкурентов
            competitors = df[(df['operator'] != 'Tele2') & 
                            (df['operator'] != 'Другой') &
                            (~pd.isna(df['latitude'])) & 
                            (~pd.isna(df['longitude']))]
            
            min_distance = float('inf')
            closest_competitor = None
            
            for _, competitor_row in competitors.iterrows():
                distance = self._calculate_distance(
                    tele2_row['latitude'], tele2_row['longitude'],
                    competitor_row['latitude'], competitor_row['longitude']
                )
                
                if distance < min_distance:
                    min_distance = distance
                    closest_competitor = competitor_row['operator']
            
            location_key = f"{tele2_row['name']} - {tele2_row['address']}"
            proximity_analysis[location_key] = {
                'closest_competitor': closest_competitor,
                'distance_km': min_distance
            }
        
        return proximity_analysis
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Расчет расстояния между двумя точками."""
        from geopy.distance import geodesic
        return geodesic((lat1, lon1), (lat2, lon2)).km
    
    def _comparative_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Сравнительный анализ с конкурентами."""
        comparative_data = {}
        
        for metric in ['rating', 'reviews_count', 'photos_count']:
            if metric in df.columns:
                operator_means = df.groupby('operator')[metric].mean()
                comparative_data[metric] = operator_means.to_dict()
        
        return comparative_data
    
    def _generate_competitor_recommendations(self, operator_stats: Dict[str, Any], 
                                           proximity_analysis: Dict[str, Any]) -> List[str]:
        """Генерация рекомендаций на основе анализа конкурентов."""
        recommendations = []
        
        # Анализ доли рынка
        total_locations = sum(stats['count'] for stats in operator_stats.values())
        
        for operator, stats in operator_stats.items():
            if operator == 'Tele2':
                market_share = stats['count'] / total_locations if total_locations > 0 else 0
                
                if market_share < 0.2:
                    recommendations.append("Низкая доля рынка. Необходима агрессивная экспансия")
                elif market_share > 0.4:
                    recommendations.append("Высокая доля рынка. Сфокусироваться на удержании позиций")
        
        # Анализ близости к конкурентам
        close_competitors = {k: v for k, v in proximity_analysis.items() if v['distance_km'] < 0.1}
        
        if close_competitors:
            recommendations.append(
                f"Обнаружено {len(close_competitors)} точек в непосредственной близости от конкурентов. "
                "Рекомендуется анализ каннибализации трафика"
            )
        
        return recommendations
