"""
Анализ покрытия дистрибуционной сети.
"""

import pandas as pd
import numpy as np
from geopy.distance import geodesic
from sklearn.cluster import DBSCAN
import folium
from typing import Dict, List, Any, Tuple
from utils.logger import get_logger

logger = get_logger(__name__)

class CoverageAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.coverage_radius_km = config.get('coverage_radius_km', 1.5)
        
    def analyze_coverage(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Анализ покрытия дистрибуционной сети.
        
        Args:
            df: DataFrame с данными о салонах связи
            
        Returns:
            Словарь с результатами анализа покрытия
        """
        logger.info("Запуск анализа покрытия дистрибуционной сети")
        
        # Фильтрация салонов Т2
        tele2_df = self._filter_tele2_locations(df)
        
        # Расчет метрик покрытия
        coverage_metrics = self._calculate_coverage_metrics(tele2_df)
        
        # Выявление пробелов в покрытии
        gap_analysis = self._identify_coverage_gaps(df, tele2_df)
        
        # Анализ по городам
        city_analysis = self._analyze_city_coverage(tele2_df)
        
        return {
            'metrics': coverage_metrics,
            'gaps': gap_analysis,
            'city_analysis': city_analysis,
            'recommendations': self._generate_coverage_recommendations(coverage_metrics, gap_analysis)
        }
    
    def _filter_tele2_locations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Фильтрация салонов Т2."""
        return df[df['name'].str.contains('Tele2|Т2', case=False, na=False)]
    
    def _calculate_coverage_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Расчет метрик покрытия."""
        if len(df) == 0:
            return {}
            
        # Основные метрики
        metrics = {
            'total_locations': len(df),
            'cities_covered': df['city'].nunique(),
            'avg_locations_per_city': len(df) / df['city'].nunique() if df['city'].nunique() > 0 else 0
        }
        
        # Анализ плотности покрытия
        metrics.update(self._calculate_density_metrics(df))
        
        return metrics
    
    def _calculate_density_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Расчет метрик плотности покрытия."""
        density_metrics = {}
        
        for city in df['city'].unique():
            city_df = df[df['city'] == city]
            if len(city_df) > 1:
                # Расчет среднего расстояния между салонами в городе
                coords = city_df[['latitude', 'longitude']].dropna().values
                distances = []
                
                for i in range(len(coords)):
                    for j in range(i + 1, len(coords)):
                        dist = geodesic(coords[i], coords[j]).km
                        distances.append(dist)
                
                if distances:
                    avg_distance = np.mean(distances)
                    density_metrics[f'{city}_avg_distance_km'] = avg_distance
                    
                    # Оценка плотности покрытия
                    if avg_distance > 5:
                        density_metrics[f'{city}_coverage_density'] = 'Низкая'
                    elif avg_distance > 2:
                        density_metrics[f'{city}_coverage_density'] = 'Средняя'
                    else:
                        density_metrics[f'{city}_coverage_density'] = 'Высокая'
        
        return density_metrics
    
    def _identify_coverage_gaps(self, all_df: pd.DataFrame, tele2_df: pd.DataFrame) -> Dict[str, Any]:
        """Выявление пробелов в покрытии."""
        # Поиск кластеров всех салонов связи
        all_coords = all_df[['latitude', 'longitude']].dropna().values
        
        if len(all_coords) < 2:
            return {'gap_locations': []}
        
        # Кластеризация для выявления центров спроса
        clustering = DBSCAN(eps=0.02, min_samples=3).fit(all_coords)
        all_df = all_df.copy()
        all_df['cluster'] = clustering.labels_
        
        # Поиск кластеров без салонов Т2
        tele2_clusters = set()
        for _, row in tele2_df.iterrows():
            if not pd.isna(row['latitude']) and not pd.isna(row['longitude']):
                # Находим ближайший кластер
                distances = [geodesic((row['latitude'], row['longitude']), center).km 
                            for center in all_coords]
                if distances:
                    min_idx = np.argmin(distances)
                    tele2_clusters.add(clustering.labels_[min_idx])
        
        # Кластеры без салонов Т2
        gap_clusters = set(clustering.labels_) - tele2_clusters
        gap_coords = all_coords[[i for i, label in enumerate(clustering.labels_) if label in gap_clusters]]
        
        return {
            'gap_clusters_count': len(gap_clusters),
            'gap_locations_count': len(gap_coords),
            'gap_locations': gap_coords.tolist() if len(gap_coords) > 0 else []
        }
    
    def _analyze_city_coverage(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Анализ покрытия по городам."""
        city_analysis = {}
        
        for city in df['city'].unique():
            city_df = df[df['city'] == city]
            city_analysis[city] = {
                'location_count': len(city_df),
                'avg_rating': city_df['rating'].mean() if 'rating' in city_df.columns else 0,
                'avg_reviews': city_df['reviews_count'].mean() if 'reviews_count' in city_df.columns else 0
            }
        
        return city_analysis
    
    def _generate_coverage_recommendations(self, metrics: Dict[str, Any], gap_analysis: Dict[str, Any]) -> List[str]:
        """Генерация рекомендаций по улучшению покрытия."""
        recommendations = []
        
        # Рекомендации на основе пробелов в покрытии
        if gap_analysis.get('gap_locations_count', 0) > 0:
            recommendations.append(
                f"Выявлено {gap_analysis['gap_locations_count']} потенциальных 'белых пятен' для размещения новых салонов"
            )
        
        # Рекомендации на основе плотности покрытия
        for key, value in metrics.items():
            if key.endswith('_coverage_density'):
                city = key.replace('_coverage_density', '')
                if value == 'Низкая':
                    recommendations.append(
                        f"В городе {city} низкая плотность покрытия. Рекомендуется открытие новых точек"
                    )
                elif value == 'Высокая':
                    recommendations.append(
                        f"В городе {city} высокая плотность покрытия. Возможна каннибализация трафика между точками"
                    )
        
        return recommendations
    
    def create_coverage_map(self, df: pd.DataFrame, output_path: str) -> None:
        """Создание карты покрытия."""
        # Фильтрация салонов Т2 и конкурентов
        tele2_df = self._filter_tele2_locations(df)
        competitors_df = df[~df['name'].str.contains('Tele2|Т2', case=False, na=False)]
        
        # Создание базовой карты
        center_lat = tele2_df['latitude'].mean() if not tele2_df.empty else 55.7558
        center_lon = tele2_df['longitude'].mean() if not tele2_df.empty else 37.6173
        
        coverage_map = folium.Map(location=[center_lat, center_lon], zoom_start=10)
        
        # Добавление салонов Т2
        for _, row in tele2_df.iterrows():
            if not pd.isna(row['latitude']) and not pd.isna(row['longitude']):
                folium.Marker(
                    [row['latitude'], row['longitude']],
                    popup=row['name'],
                    icon=folium.Icon(color='green', icon='info-sign')
                ).add_to(coverage_map)
        
        # Добавление салонов конкурентов
        for _, row in competitors_df.iterrows():
            if not pd.isna(row['latitude']) and not pd.isna(row['longitude']):
                folium.Marker(
                    [row['latitude'], row['longitude']],
                    popup=row['name'],
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(coverage_map)
        
        # Сохранение карты
        coverage_map.save(output_path)
        logger.info(f"Карта покрытия сохранена в {output_path}")
