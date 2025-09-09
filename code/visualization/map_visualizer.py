"""
Модуль для создания статических карт покрытия.
"""

import folium
from folium import plugins
import pandas as pd
from typing import Dict, List, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class MapVisualizer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.colors = config.get('colors', {
            'tele2': '#00A2FF',  # Синий - Tele2
            'mts': '#E30613',    # Красный - МТС
            'beeline': '#FFDE00',# Желтый - Билайн
            'megafon': '#5C33CF' # Фиолетовый - МегаФон
        })
        
    def create_coverage_map(self, df: pd.DataFrame, output_path: str) -> folium.Map:
        """
        Создание карты покрытия дистрибуционной сети.
        
        Args:
            df: DataFrame с данными о салонах связи
            output_path: Путь для сохранения карты
            
        Returns:
            Объект карты folium
        """
        logger.info("Создание карты покрытия")
        
        # Фильтрация салонов по операторам
        tele2_df = df[df['name'].str.contains('Tele2|Т2', case=False, na=False)]
        mts_df = df[df['name'].str.contains('МТС|MTS', case=False, na=False)]
        beeline_df = df[df['name'].str.contains('Билайн|Beeline', case=False, na=False)]
        megafon_df = df[df['name'].str.contains('МегаФон|Megafon', case=False, na=False)]
        
        # Определение центра карты
        center_lat, center_lon = self._calculate_map_center(tele2_df)
        
        # Создание базовой карты
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=10,
            tiles='OpenStreetMap'
        )
        
        # Добавление слоя с салонами Т2
        self._add_locations_to_map(m, tele2_df, 'Tele2', self.colors['tele2'], 'star')
        
        # Добавление слоев с конкурентами
        self._add_locations_to_map(m, mts_df, 'МТС', self.colors['mts'], 'info-sign')
        self._add_locations_to_map(m, beeline_df, 'Билайн', self.colors['beeline'], 'info-sign')
        self._add_locations_to_map(m, megafon_df, 'МегаФон', self.colors['megafon'], 'info-sign')
        
        # Добавление контроля слоев
        self._add_layer_control(m)
        
        # Сохранение карты
        m.save(output_path)
        logger.info(f"Карта покрытия сохранена в {output_path}")
        
        return m
    
    def create_heatmap(self, df: pd.DataFrame, output_path: str, intensity_column: str = 'rating') -> folium.Map:
        """
        Создание тепловой карты на основе данных.
        
        Args:
            df: DataFrame с данными
            output_path: Путь для сохранения карты
            intensity_column: Колонка для определения интенсивности
            
        Returns:
            Объект карты folium с тепловой картой
        """
        logger.info("Создание тепловой карты")
        
        # Фильтрация салонов Т2
        tele2_df = df[df['name'].str.contains('Tele2|Т2', case=False, na=False)]
        
        # Подготовка данных для тепловой карты
        heat_data = []
        for _, row in tele2_df.iterrows():
            if not pd.isna(row['latitude']) and not pd.isna(row['longitude']):
                intensity = row.get(intensity_column, 1) if intensity_column in row else 1
                heat_data.append([row['latitude'], row['longitude'], intensity])
        
        # Создание базовой карты
        center_lat, center_lon = self._calculate_map_center(tele2_df)
        m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
        
        # Добавление тепловой карты
        plugins.HeatMap(heat_data, min_opacity=0.2, max_zoom=18).add_to(m)
        
        # Сохранение карты
        m.save(output_path)
        logger.info(f"Тепловая карта сохранена в {output_path}")
        
        return m
    
    def create_cluster_map(self, df: pd.DataFrame, output_path: str) -> folium.Map:
        """
        Создание кластерной карты для визуализации плотности точек.
        
        Args:
            df: DataFrame с данными
            output_path: Путь для сохранения карты
            
        Returns:
            Объект карты folium с кластерами
        """
        logger.info("Создание кластерной карты")
        
        # Фильтрация салонов Т2
        tele2_df = df[df['name'].str.contains('Tele2|Т2', case=False, na=False)]
        
        # Создание базовой карты
        center_lat, center_lon = self._calculate_map_center(tele2_df)
        m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
        
        # Создание кластеров
        marker_cluster = plugins.MarkerCluster().add_to(m)
        
        # Добавление маркеров в кластеры
        for _, row in tele2_df.iterrows():
            if not pd.isna(row['latitude']) and not pd.isna(row['longitude']):
                popup_text = f"""
                <b>{row.get('name', 'Неизвестно')}</b><br>
                Адрес: {row.get('address', 'Неизвестно')}<br>
                Рейтинг: {row.get('rating', 'Нет данных')}<br>
                Отзывы: {row.get('reviews_count', 0)}
                """
                
                folium.Marker(
                    [row['latitude'], row['longitude']],
                    popup=folium.Popup(popup_text, max_width=300),
                    icon=folium.Icon(color=self.colors['tele2'], icon='info-sign')
                ).add_to(marker_cluster)
        
        # Сохранение карты
        m.save(output_path)
        logger.info(f"Кластерная карта сохранена в {output_path}")
        
        return m
    
    def _calculate_map_center(self, df: pd.DataFrame) -> tuple:
        """
        Расчет центра карты на основе данных.
        
        Args:
            df: DataFrame с координатами
            
        Returns:
            Кортеж (широта, долгота) центра карты
        """
        if len(df) == 0:
            return (55.7558, 37.6173)  # Москва по умолчанию
        
        valid_coords = df[~pd.isna(df['latitude']) & ~pd.isna(df['longitude'])]
        
        if len(valid_coords) == 0:
            return (55.7558, 37.6173)  # Москва по умолчанию
        
        center_lat = valid_coords['latitude'].mean()
        center_lon = valid_coords['longitude'].mean()
        
        return (center_lat, center_lon)
    
    def _add_locations_to_map(self, map_obj: folium.Map, df: pd.DataFrame, 
                             layer_name: str, color: str, icon: str) -> None:
        """
        Добавление локаций на карту.
        
        Args:
            map_obj: Объект карты folium
            df: DataFrame с данными о локациях
            layer_name: Название слоя
            color: Цвет маркеров
            icon: Иконка маркеров
        """
        feature_group = folium.FeatureGroup(name=layer_name)
        
        for _, row in df.iterrows():
            if not pd.isna(row['latitude']) and not pd.isna(row['longitude']):
                popup_text = f"""
                <b>{row.get('name', 'Неизвестно')}</b><br>
                Адрес: {row.get('address', 'Неизвестно')}<br>
                Рейтинг: {row.get('rating', 'Нет данных')}<br>
                Отзывы: {row.get('reviews_count', 0)}
                """
                
                folium.Marker(
                    [row['latitude'], row['longitude']],
                    popup=folium.Popup(popup_text, max_width=300),
                    icon=folium.Icon(color=color, icon=icon)
                ).add_to(feature_group)
        
        feature_group.add_to(map_obj)
    
    def _add_layer_control(self, map_obj: folium.Map) -> None:
        """
        Добавление контроля слоев на карту.
        
        Args:
            map_obj: Объект карты folium
        """
        folium.LayerControl().add_to(map_obj)
