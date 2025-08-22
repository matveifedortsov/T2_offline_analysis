"""
Анализ трендов и временных рядов.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class TrendAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    def analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Анализ трендов дистрибуционной сети.
        
        Args:
            df: DataFrame с данными о салонах связи
            
        Returns:
            Словарь с результатами анализа трендов
        """
        logger.info("Запуск анализа трендов")
        
        # Добавление временных меток (если данные имеют временную компоненту)
        df_with_dates = self._add_temporal_features(df)
        
        # Анализ временных трендов
        time_analysis = self._analyze_time_trends(df_with_dates)
        
        # Анализ пространственных трендов
        spatial_analysis = self._analyze_spatial_trends(df)
        
        # Прогнозирование трендов
        forecast = self._forecast_trends(df)
        
        return {
            'time_analysis': time_analysis,
            'spatial_analysis': spatial_analysis,
            'forecast': forecast,
            'recommendations': self._generate_trend_recommendations(time_analysis, spatial_analysis, forecast)
        }
    
    def _add_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Добавление временных меток к данным."""
        df = df.copy()
        
        # Если в данных есть информация о дате открытия
        if 'established_year' in df.columns:
            df['age_years'] = datetime.now().year - df['established_year']
        
        # Добавление временной метки анализа
        df['analysis_date'] = datetime.now()
        
        return df
    
    def _analyze_time_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Анализ временных трендов."""
        time_analysis = {}
        
        # Анализ по годам открытия (если данные доступны)
        if 'established_year' in df.columns:
            yearly_trend = df.groupby('established_year').size()
            time_analysis['yearly_trend'] = yearly_trend.to_dict()
            
            # Расчет роста/сокращения
            if len(yearly_trend) > 1:
                growth_rates = yearly_trend.pct_change() * 100
                time_analysis['growth_rates'] = growth_rates.to_dict()
        
        return time_analysis
    
    def _analyze_spatial_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Анализ пространственных трендов."""
        spatial_analysis = {}
        
        # Анализ распределения по городам
        city_distribution = df['city'].value_counts()
        spatial_analysis['city_distribution'] = city_distribution.to_dict()
        
        # Анализ плотности по регионам
        # (здесь можно добавить более сложный анализ по географическим регионам)
        
        return spatial_analysis
    
    def _forecast_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Прогнозирование будущих трендов."""
        forecast = {}
        
        # Простое прогнозирование на основе исторических данных
        if 'established_year' in df.columns:
            # Прогноз количества новых точек на следующий год
            recent_years = df[df['established_year'] >= datetime.now().year - 3]
            yearly_counts = recent_years.groupby('established_year').size()
            
            if len(yearly_counts) > 0:
                avg_growth = yearly_counts.mean()
                forecast['next_year_prediction'] = avg_growth
        
        return forecast
    
    def _generate_trend_recommendations(self, time_analysis: Dict[str, Any], 
                                      spatial_analysis: Dict[str, Any], 
                                      forecast: Dict[str, Any]) -> List[str]:
        """Генерация рекомендаций на основе анализа трендов."""
        recommendations = []
        
        # Рекомендации на основе временных трендов
        if 'growth_rates' in time_analysis:
            recent_growth = list(time_analysis['growth_rates'].values())[-1] if time_analysis['growth_rates'] else 0
            
            if recent_growth < 0:
                recommendations.append("Отрицательный рост сети. Необходима стратегия расширения")
            elif recent_growth > 10:
                recommendations.append("Высокий рост сети. Убедитесь в качестве новых точек")
        
        # Рекомендации на основе пространственного распределения
        city_distribution = spatial_analysis.get('city_distribution', {})
        if city_distribution:
            top_cities = sorted(city_distribution.items(), key=lambda x: x[1], reverse=True)[:3]
            recommendations.append(f"Основная концентрация точек в городах: {', '.join([city for city, _ in top_cities])}")
        
        return recommendations
