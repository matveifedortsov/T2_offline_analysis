"""
Модуль для создания интерактивных карт с использованием Plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class InteractiveMapBuilder:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    def create_interactive_coverage_map(self, df: pd.DataFrame, output_path: str = None) -> go.Figure:
        """
        Создание интерактивной карты покрытия.
        
        Args:
            df: DataFrame с данными
            output_path: Путь для сохранения карты (опционально)
            
        Returns:
            Интерактивная карта Plotly
        """
        logger.info("Создание интерактивной карты покрытия")
        
        # Фильтрация салонов Т2
        tele2_df = df[df['name'].str.contains('Tele2|Т2', case=False, na=False)]
        
        # Создание карты
        fig = px.scatter_mapbox(
            tele2_df,
            lat='latitude',
            lon='longitude',
            hover_name='name',
            hover_data=['address', 'rating', 'reviews_count'],
            color='rating',
            color_continuous_scale=px.colors.sequential.Viridis,
            zoom=10,
            title='Интерактивная карта покрытия Т2'
        )
        
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})
        
        if output_path:
            fig.write_html(output_path)
            logger.info(f"Интерактивная карта сохранена в {output_path}")
        
        return fig
    
    def create_animated_map(self, df: pd.DataFrame, output_path: str = None) -> go.Figure:
        """
        Создание анимированной карты развития сети.
        
        Args:
            df: DataFrame с данными
            output_path: Путь для сохранения карты (опционально)
            
        Returns:
            Анимированная карта Plotly
        """
        logger.info("Создание анимированной карты развития сети")
        
        # Фильтрация салонов Т2
        tele2_df = df[df['name'].str.contains('Tele2|Т2', case=False, na=False)].copy()
        
        # Добавление данных для анимации (заглушка)
        # В реальном проекте здесь должны быть исторические данные
        if 'established_year' not in tele2_df.columns:
            tele2_df['established_year'] = 2020  # Заглушка
        
        # Создание анимированной карты
        fig = px.scatter_mapbox(
            tele2_df,
            lat='latitude',
            lon='longitude',
            hover_name='name',
            hover_data=['address', 'rating'],
            animation_frame='established_year',
            color='rating',
            color_continuous_scale=px.colors.sequential.Viridis,
            zoom=10,
            title='Развитие сети Т2 по годам'
        )
        
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})
        
        if output_path:
            fig.write_html(output_path)
            logger.info(f"Анимированная карта сохранена в {output_path}")
        
        return fig
    
    def create_competitor_map(self, df: pd.DataFrame, output_path: str = None) -> go.Figure:
        """
        Создание карты с отображением конкурентов.
        
        Args:
            df: DataFrame с данными
            output_path: Путь для сохранения карты (опционально)
            
        Returns:
            Карта конкурентов Plotly
        """
        logger.info("Создание карты с отображением конкурентов")
        
        # Идентификация операторов
        df['operator'] = df['name'].apply(self._identify_operator)
        
        # Создание карты
        fig = px.scatter_mapbox(
            df,
            lat='latitude',
            lon='longitude',
            hover_name='name',
            hover_data=['address', 'rating'],
            color='operator',
            zoom=10,
            title='Карта конкурентов'
        )
        
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})
        
        if output_path:
            fig.write_html(output_path)
            logger.info(f"Карта конкурентов сохранена в {output_path}")
        
        return fig
    
    def _identify_operator(self, name: str) -> str:
        """
        Идентификация оператора по названию.
        
        Args:
            name: Название салона связи
            
        Returns:
            Идентифицированный оператор
        """
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
