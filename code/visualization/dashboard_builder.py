"""
Модуль для создания интерактивных дашбордов.
"""

import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class DashboardBuilder:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.app = dash.Dash(__name__)
        
    def create_interactive_dashboard(self, df: pd.DataFrame, analysis_results: Dict[str, Any], 
                                   output_path: str = None) -> dash.Dash:
        """
        Создание интерактивного дашборда.
        
        Args:
            df: DataFrame с данными
            analysis_results: Результаты анализа
            output_path: Путь для сохранения дашборда (опционально)
            
        Returns:
            Объект дашборда Dash
        """
        logger.info("Создание интерактивного дашборда")
        
        # Идентификация операторов
        df['operator'] = df['name'].apply(self._identify_operator)
        
        # Создание layout дашборда
        self.app.layout = self._create_dashboard_layout(df, analysis_results)
        
        # Добавление callback'ов
        self._add_callbacks(df)
        
        if output_path:
            # Сохранение дашборда как HTML
            self._save_dashboard_as_html(output_path)
        
        return self.app
    
    def _create_dashboard_layout(self, df: pd.DataFrame, analysis_results: Dict[str, Any]) -> html.Div:
        """
        Создание layout дашборда.
        
        Args:
            df: DataFrame с данными
            analysis_results: Результаты анализа
            
        Returns:
            Layout дашборда
        """
        # Создание графиков для дашборда
        graphs = self._create_dashboard_graphs(df, analysis_results)
        
        layout = html.Div([
            html.H1("Анализ дистрибуционной сети Т2", style={'textAlign': 'center'}),
            
            # Первый ряд: Общая статистика
            html.Div([
                html.Div([
                    html.H3("Общая статистика"),
                    self._create_summary_cards(analysis_results)
                ], className='row'),
                
                # Второй ряд: Графики
                html.Div([
                    html.Div([
                        dcc.Graph(figure=graphs['market_share'])
                    ], className='six columns'),
                    
                    html.Div([
                        dcc.Graph(figure=graphs['city_distribution'])
                    ], className='six columns')
                ], className='row'),
                
                # Третий ряд: Графики
                html.Div([
                    html.Div([
                        dcc.Graph(figure=graphs['rating_comparison'])
                    ], className='six columns'),
                    
                    html.Div([
                        dcc.Graph(figure=graphs['efficiency_distribution'])
                    ], className='six columns')
                ], className='row'),
                
                # Четвертый ряд: Карта
                html.Div([
                    html.Div([
                        dcc.Graph(figure=graphs['coverage_map'])
                    ], className='twelve columns')
                ], className='row'),
                
                # Пятый ряд: Фильтры и контролы
                html.Div([
                    html.Div([
                        html.Label("Выберите город:"),
                        dcc.Dropdown(
                            id='city-filter',
                            options=[{'label': city, 'value': city} for city in df['city'].unique()],
                            value=df['city'].iloc[0] if len(df) > 0 else '',
                            multi=True
                        )
                    ], className='six columns'),
                    
                    html.Div([
                        html.Label("Выберите оператора:"),
                        dcc.Dropdown(
                            id='operator-filter',
                            options=[{'label': op, 'value': op} for op in df['operator'].unique()],
                            value='Tele2',
                            multi=True
                        )
                    ], className='six columns')
                ], className='row')
            ], className='container')
        ])
        
        return layout
    
    def _create_dashboard_graphs(self, df: pd.DataFrame, analysis_results: Dict[str, Any]) -> Dict[str, go.Figure]:
        """
        Создание графиков для дашборда.
        
        Args:
            df: DataFrame с данными
            analysis_results: Результаты анализа
            
        Returns:
            Словарь с графиками Plotly
        """
        graphs = {}
        
        # 1. Круговая диаграмма долей рынка
        operator_counts = df['operator'].value_counts()
        graphs['market_share'] = px.pie(
            values=operator_counts.values,
            names=operator_counts.index,
            title='Доля рынка по операторам'
        )
        
        # 2. Столбчатая диаграмма распределения по городам
        city_counts = df['city'].value_counts().head(10)  # Топ-10 городов
        graphs['city_distribution'] = px.bar(
            x=city_counts.index,
            y=city_counts.values,
            title='Распределение салонов по городам (Топ-10)',
            labels={'x': 'Город', 'y': 'Количество салонов'}
        )
        
        # 3. Box-plot сравнения рейтингов
        rating_data = []
        for operator in df['operator'].unique():
            operator_ratings = df[df['operator'] == operator]['rating'].dropna()
            for rating in operator_ratings:
                rating_data.append({'operator': operator, 'rating': rating})
        
        rating_df = pd.DataFrame(rating_data)
        graphs['rating_comparison'] = px.box(
            rating_df, 
            x='operator', 
            y='rating',
            title='Сравнение рейтингов по операторам'
        )
        
        # 4. Распределение эффективности локаций (если есть данные)
        if 'location_analysis' in analysis_results:
            efficiency_data = analysis_results['location_analysis'].get('efficiency_scores', [])
            if efficiency_data:
                efficiency_df = pd.DataFrame(efficiency_data)
                graphs['efficiency_distribution'] = px.histogram(
                    efficiency_df,
                    x='efficiency_score',
                    title='Распределение эффективности локаций Т2',
                    labels={'efficiency_score': 'Оценка эффективности'}
                )
        
        # 5. Карта покрытия
        tele2_df = df[df['operator'] == 'Tele2']
        graphs['coverage_map'] = px.scatter_mapbox(
            tele2_df,
            lat='latitude',
            lon='longitude',
            hover_name='name',
            hover_data=['address', 'rating'],
            zoom=10,
            title='Карта покрытия Т2'
        )
        graphs['coverage_map'].update_layout(mapbox_style="open-street-map")
        
        return graphs
    
    def _create_summary_cards(self, analysis_results: Dict[str, Any]) -> html.Div:
        """
        Создание карточек с общей статистикой.
        
        Args:
            analysis_results: Результаты анализа
            
        Returns:
            Div с карточками статистики
        """
        # Извлечение данных для карточек
        total_locations = 0
        cities_covered = 0
        avg_rating = 0
        
        if 'coverage_analysis' in analysis_results:
            coverage = analysis_results['coverage_analysis']
            total_locations = coverage.get('metrics', {}).get('total_locations', 0)
            cities_covered = coverage.get('metrics', {}).get('cities_covered', 0)
        
        if 'competitor_analysis' in analysis_results:
            competitor = analysis_results['competitor_analysis']
            tele2_stats = competitor.get('operator_stats', {}).get('Tele2', {})
            avg_rating = tele2_stats.get('avg_rating', 0)
        
        # Создание карточек
        cards = html.Div([
            html.Div([
                html.Div([
                    html.H4("Всего салонов Т2"),
                    html.P(f"{total_locations}")
                ], className='card')
            ], className='three columns'),
            
            html.Div([
                html.Div([
                    html.H4("Городов с покрытием"),
                    html.P(f"{cities_covered}")
                ], className='card')
            ], className='three columns'),
            
            html.Div([
                html.Div([
                    html.H4("Средний рейтинг"),
                    html.P(f"{avg_rating:.2f}")
                ], className='card')
            ], className='three columns'),
            
            html.Div([
                html.Div([
                    html.H4("Рекомендаций"),
                    html.P("15")  # Заглушка
                ], className='card')
            ], className='three columns')
        ], className='row')
        
        return cards
    
    def _add_callbacks(self, df: pd.DataFrame) -> None:
        """
        Добавление callback'ов для интерактивности.
        
        Args:
            df: DataFrame с данными
        """
        @self.app.callback(
            Output('market_share', 'figure'),
            [Input('city-filter', 'value'),
             Input('operator-filter', 'value')]
        )
        def update_market_share(selected_cities, selected_operators):
            # Фильтрация данных
            filtered_df = df.copy()
            
            if selected_cities:
                if isinstance(selected_cities, str):
                    selected_cities = [selected_cities]
                filtered_df = filtered_df[filtered_df['city'].isin(selected_cities)]
            
            if selected_operators:
                if isinstance(selected_operators, str):
                    selected_operators = [selected_operators]
                filtered_df = filtered_df[filtered_df['operator'].isin(selected_operators)]
            
            # Обновление графика
            operator_counts = filtered_df['operator'].value_counts()
            fig = px.pie(
                values=operator_counts.values,
                names=operator_counts.index,
                title='Доля рынка по операторам'
            )
            
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
    
    def _save_dashboard_as_html(self, output_path: str) -> None:
        """
        Сохранение дашборда как HTML-файла.
        
        Args:
            output_path: Путь для сохранения
        """
        # Для сохранения дашборда как HTML, нам нужно отрендерить его
        # В реальном проекте это может быть сложнее, поэтому здесь упрощенная версия
        with open(output_path, 'w') as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Дашборд анализа дистрибуции Т2</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            </head>
            <body>
                <h1>Дашборд анализа дистрибуции Т2</h1>
                <p>Для полной функциональности запустите дашборд через Dash сервер</p>
            </body>
            </html>
            """)
        
        logger.info(f"Дашборд сохранен в {output_path}")
    
    def run_server(self, host: str = '0.0.0.0', port: int = 8050, debug: bool = True) -> None:
        """
        Запуск сервера дашборда.
        
        Args:
            host: Хост для запуска
            port: Порт для запуска
            debug: Режим отладки
        """
        logger.info(f"Запуск дашборда на http://{host}:{port}")
        self.app.run_server(host=host, port=port, debug=debug)
