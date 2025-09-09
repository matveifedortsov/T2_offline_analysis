"""
Модуль для создания графиков и диаграмм.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class ChartGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.set_style()
        
    def set_style(self) -> None:
        """Установка стиля для графиков."""
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Настройка шрифтов для поддержки кириллицы
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def create_bar_chart(self, data: Dict[str, Any], title: str, xlabel: str, ylabel: str, 
                        output_path: str, figsize: tuple = (10, 6)) -> None:
        """
        Создание столбчатой диаграммы.
        
        Args:
            data: Данные для графика {категория: значение}
            title: Заголовок графика
            xlabel: Подпись оси X
            ylabel: Подпись оси Y
            output_path: Путь для сохранения графика
            figsize: Размер фигуры
        """
        plt.figure(figsize=figsize)
        
        categories = list(data.keys())
        values = list(data.values())
        
        bars = plt.bar(categories, values, color=sns.color_palette("husl", len(categories)))
        
        # Добавление значений на столбцы
        for bar, value in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                    f'{value}', ha='center', va='bottom')
        
        plt.title(title, fontsize=16, pad=20)
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Столбчатая диаграмма сохранена в {output_path}")
    
    def create_pie_chart(self, data: Dict[str, Any], title: str, output_path: str, 
                        figsize: tuple = (8, 8)) -> None:
        """
        Создание круговой диаграммы.
        
        Args:
            data: Данные для графика {категория: значение}
            title: Заголовок графика
            output_path: Путь для сохранения графика
            figsize: Размер фигуры
        """
        plt.figure(figsize=figsize)
        
        labels = list(data.keys())
        values = list(data.values())
        
        # Автоматическое выделение секторов с малыми значениями
        explode = [0.1 if value/sum(values) < 0.05 else 0 for value in values]
        
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, 
                explode=explode, shadow=True)
        plt.axis('equal')
        plt.title(title, fontsize=16, pad=20)
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Круговая диаграмма сохранена в {output_path}")
    
    def create_line_chart(self, x_data: List[Any], y_data: List[Any], title: str, 
                         xlabel: str, ylabel: str, output_path: str, figsize: tuple = (10, 6)) -> None:
        """
        Создание линейного графика.
        
        Args:
            x_data: Данные для оси X
            y_data: Данные для оси Y
            title: Заголовок графика
            xlabel: Подпись оси X
            ylabel: Подпись оси Y
            output_path: Путь для сохранения графика
            figsize: Размер фигуры
        """
        plt.figure(figsize=figsize)
        
        plt.plot(x_data, y_data, marker='o', linewidth=2, markersize=6)
        
        plt.title(title, fontsize=16, pad=20)
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.grid(True, alpha=0.3)
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Линейный график сохранен в {output_path}")
    
    def create_histogram(self, data: List[Any], title: str, xlabel: str, ylabel: str, 
                        output_path: str, bins: int = 10, figsize: tuple = (10, 6)) -> None:
        """
        Создание гистограммы.
        
        Args:
            data: Данные для гистограммы
            title: Заголовок графика
            xlabel: Подпись оси X
            ylabel: Подпись оси Y
            output_path: Путь для сохранения графика
            bins: Количество бинов
            figsize: Размер фигуры
        """
        plt.figure(figsize=figsize)
        
        plt.hist(data, bins=bins, alpha=0.7, edgecolor='black')
        
        plt.title(title, fontsize=16, pad=20)
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.grid(True, alpha=0.3)
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Гистограмма сохранена в {output_path}")
    
    def create_scatter_plot(self, x_data: List[Any], y_data: List[Any], title: str, 
                           xlabel: str, ylabel: str, output_path: str, figsize: tuple = (10, 6)) -> None:
        """
        Создание точечного графика.
        
        Args:
            x_data: Данные для оси X
            y_data: Данные для оси Y
            title: Заголовок графика
            xlabel: Подпись оси X
            ylabel: Подпись оси Y
            output_path: Путь для сохранения графика
            figsize: Размер фигуры
        """
        plt.figure(figsize=figsize)
        
        plt.scatter(x_data, y_data, alpha=0.6, edgecolors='w', s=50)
        
        plt.title(title, fontsize=16, pad=20)
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.grid(True, alpha=0.3)
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Точечный график сохранен в {output_path}")
    
    def create_box_plot(self, data: Dict[str, List[Any]], title: str, ylabel: str, 
                       output_path: str, figsize: tuple = (10, 6)) -> None:
        """
        Создание box-plot диаграммы.
        
        Args:
            data: Данные для графика {категория: значения}
            title: Заголовок графика
            ylabel: Подпись оси Y
            output_path: Путь для сохранения графика
            figsize: Размер фигуры
        """
        plt.figure(figsize=figsize)
        
        categories = list(data.keys())
        values = list(data.values())
        
        plt.boxplot(values, labels=categories)
        
        plt.title(title, fontsize=16, pad=20)
        plt.ylabel(ylabel, fontsize=12)
        plt.grid(True, alpha=0.3)
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Box-plot диаграмма сохранена в {output_path}")
    
    def create_competitor_comparison(self, df: pd.DataFrame, output_path: str, 
                                   metrics: List[str] = ['rating', 'reviews_count']) -> None:
        """
        Создание графиков сравнения конкурентов.
        
        Args:
            df: DataFrame с данными о салонах связи
            output_path: Путь для сохранения графиков
            metrics: Список метрик для сравнения
        """
        # Идентификация операторов
        df['operator'] = df['name'].apply(self._identify_operator)
        
        # Создание подграфиков
        n_metrics = len(metrics)
        fig, axes = plt.subplots(1, n_metrics, figsize=(5 * n_metrics, 6))
        
        if n_metrics == 1:
            axes = [axes]
        
        for i, metric in enumerate(metrics):
            if metric in df.columns:
                # Группировка по операторам и расчет средних значений
                operator_means = df.groupby('operator')[metric].mean()
                
                axes[i].bar(operator_means.index, operator_means.values, 
                           color=sns.color_palette("husl", len(operator_means)))
                axes[i].set_title(f'Сравнение по {metric}', fontsize=14)
                axes[i].set_ylabel('Среднее значение', fontsize=12)
                axes[i].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"График сравнения конкурентов сохранен в {output_path}")
    
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
    
    def create_dashboard(self, analysis_results: Dict[str, Any], output_path: str) -> None:
        """
        Создание дашборда с основными графиками.
        
        Args:
            analysis_results: Результаты анализа
            output_path: Путь для сохранения дашборда
        """
        # Создание комплексного дашборда
        fig = plt.figure(figsize=(16, 12))
        
        # Определение layout дашборда
        gs = fig.add_gridspec(3, 3)
        
        # 1. График распределения салонов по городам (верхний левый)
        ax1 = fig.add_subplot(gs[0, 0])
        if 'coverage_analysis' in analysis_results:
            city_data = analysis_results['coverage_analysis'].get('city_analysis', {})
            if city_data:
                city_counts = {city: data['location_count'] for city, data in city_data.items()}
                ax1.bar(city_counts.keys(), city_counts.values())
                ax1.set_title('Распределение салонов по городам')
                ax1.tick_params(axis='x', rotation=45)
        
        # 2. Круговая диаграмма долей рынка (верхний центральный)
        ax2 = fig.add_subplot(gs[0, 1])
        if 'competitor_analysis' in analysis_results:
            operator_data = analysis_results['competitor_analysis'].get('operator_stats', {})
            if operator_data:
                market_share = {op: stats['count'] for op, stats in operator_data.items()}
                ax2.pie(market_share.values(), labels=market_share.keys(), autopct='%1.1f%%')
                ax2.set_title('Доля рынка по операторам')
        
        # 3. График эффективности локаций (верхний правый)
        ax3 = fig.add_subplot(gs[0, 2])
        if 'location_analysis' in analysis_results:
            efficiency_data = analysis_results['location_analysis'].get('efficiency_scores', [])
            if efficiency_data:
                scores = [item['efficiency_score'] for item in efficiency_data]
                ax3.hist(scores, bins=10, alpha=0.7, edgecolor='black')
                ax3.set_title('Распределение эффективности локаций')
                ax3.set_xlabel('Оценка эффективности')
                ax3.set_ylabel('Количество')
        
        # 4. Box-plot сравнения рейтингов (нижний левый)
        ax4 = fig.add_subplot(gs[1, 0])
        if 'competitor_analysis' in analysis_results:
            operator_data = analysis_results['competitor_analysis'].get('operator_stats', {})
            if operator_data and 'rating' in df.columns:
                rating_data = {}
                for operator in operator_data.keys():
                    operator_ratings = df[df['operator'] == operator]['rating'].dropna()
                    if len(operator_ratings) > 0:
                        rating_data[operator] = operator_ratings
                
                ax4.boxplot(rating_data.values(), labels=rating_data.keys())
                ax4.set_title('Сравнение рейтингов по операторам')
                ax4.tick_params(axis='x', rotation=45)
        
        # 5. График зависимости рейтинга от количества отзывов (нижний центральный)
        ax5 = fig.add_subplot(gs[1, 1:])
        if 'rating' in df.columns and 'reviews_count' in df.columns:
            ax5.scatter(df['reviews_count'], df['rating'], alpha=0.5)
            ax5.set_title('Зависимость рейтинга от количества отзывов')
            ax5.set_xlabel('Количество отзывов')
            ax5.set_ylabel('Рейтинг')
        
        # 6. Текст с ключевыми выводами (нижний ряд)
        ax6 = fig.add_subplot(gs[2, :])
        ax6.axis('off')
        
        if 'coverage_analysis' in analysis_results:
            recommendations = analysis_results['coverage_analysis'].get('recommendations', [])
            if recommendations:
                summary_text = "Ключевые рекомендации:\n\n" + "\n".join(
                    [f"• {rec}" for rec in recommendations[:3]]  # Ограничиваем тремя рекомендациями
                )
                ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes, fontsize=10, 
                        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Дашборд сохранен в {output_path}")
