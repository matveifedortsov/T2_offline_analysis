"""
Генерация отчетов на основе аналитических данных.
"""

import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any
from utils.logger import get_logger
from utils.file_operations import write_json, write_csv

logger = get_logger(__name__)

class ReportGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    def generate_reports(self, analysis_results: Dict[str, Any], output_dir: str = 'reports') -> Dict[str, Any]:
        """
        Генерация отчетов на основе результатов анализа.
        
        Args:
            analysis_results: Результаты анализов
            output_dir: Директория для сохранения отчетов
            
        Returns:
            Словарь с путями к сгенерированным отчетам
        """
        logger.info("Генерация отчетов")
        
        report_paths = {}
        
        # Создание директории для отчетов
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Генерация различных форматов отчетов
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON-отчет
        json_report_path = f"{output_dir}/analysis_report_{timestamp}.json"
        self._generate_json_report(analysis_results, json_report_path)
        report_paths['json'] = json_report_path
        
        # CSV-отчет
        csv_report_path = f"{output_dir}/analysis_report_{timestamp}.csv"
        self._generate_csv_report(analysis_results, csv_report_path)
        report_paths['csv'] = csv_report_path
        
        # Текстовый отчет
        text_report_path = f"{output_dir}/analysis_report_{timestamp}.txt"
        self._generate_text_report(analysis_results, text_report_path)
        report_paths['text'] = text_report_path
        
        # Визуальный отчет (дашборд)
        dashboard_path = f"{output_dir}/dashboard_{timestamp}.html"
        self._generate_dashboard(analysis_results, dashboard_path)
        report_paths['dashboard'] = dashboard_path
        
        logger.info(f"Отчеты сохранены в директории {output_dir}")
        return report_paths
    
    def _generate_json_report(self, analysis_results: Dict[str, Any], output_path: str) -> None:
        """Генерация отчета в формате JSON."""
        write_json(analysis_results, output_path)
        logger.info(f"JSON-отчет сохранен в {output_path}")
    
    def _generate_csv_report(self, analysis_results: Dict[str, Any], output_path: str) -> None:
        """Генерация отчета в формате CSV."""
        # Преобразование данных в плоский формат для CSV
        csv_data = []
        
        # Добавление данных о покрытии
        if 'coverage_analysis' in analysis_results:
            coverage = analysis_results['coverage_analysis']
            for metric, value in coverage.get('metrics', {}).items():
                csv_data.append({'category': 'coverage', 'metric': metric, 'value': value})
        
        # Добавление данных об эффективности
        if 'location_analysis' in analysis_results:
            efficiency = analysis_results['location_analysis']
            for item in efficiency.get('efficiency_scores', []):
                csv_data.append({
                    'category': 'efficiency',
                    'location': item.get('name', ''),
                    'address': item.get('address', ''),
                    'score': item.get('efficiency_score', 0),
                    'category': item.get('efficiency_category', '')
                })
        
        # Сохранение CSV
        if csv_data:
            df = pd.DataFrame(csv_data)
            df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"CSV-отчет сохранен в {output_path}")
    
    def _generate_text_report(self, analysis_results: Dict[str, Any], output_path: str) -> None:
        """Генерация текстового отчета."""
        report_lines = []
        
        # Заголовок отчета
        report_lines.append("ОТЧЕТ ПО АНАЛИЗУ ДИСТРИБУЦИОННОЙ СЕТИ Т2")
        report_lines.append("=" * 50)
        report_lines.append(f"Дата генерации: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Раздел анализа покрытия
        if 'coverage_analysis' in analysis_results:
            coverage = analysis_results['coverage_analysis']
            report_lines.append("АНАЛИЗ ПОКРЫТИЯ")
            report_lines.append("-" * 30)
            
            for metric, value in coverage.get('metrics', {}).items():
                report_lines.append(f"{metric}: {value}")
            
            report_lines.append("")
            report_lines.append("РЕКОМЕНДАЦИИ ПО ПОКРЫТИЮ:")
            for recommendation in coverage.get('recommendations', []):
                report_lines.append(f"- {recommendation}")
            
            report_lines.append("")
        
        # Раздел анализа эффективности
        if 'location_analysis' in analysis_results:
            efficiency = analysis_results['location_analysis']
            report_lines.append("АНАЛИЗ ЭФФЕКТИВНОСТИ ЛОКАЦИЙ")
            report_lines.append("-" * 40)
            
            # Топ-5 самых эффективных локаций
            efficiency_scores = efficiency.get('efficiency_scores', [])
            if efficiency_scores:
                sorted_scores = sorted(efficiency_scores, key=lambda x: x.get('efficiency_score', 0), reverse=True)
                report_lines.append("Топ-5 самых эффективных локаций:")
                for i, item in enumerate(sorted_scores[:5], 1):
                    report_lines.append(f"{i}. {item.get('name', '')} - {item.get('efficiency_score', 0):.2f}")
            
            report_lines.append("")
            report_lines.append("РЕКОМЕНДАЦИИ ПО ЭФФЕКТИВНОСТИ:")
            for recommendation in efficiency.get('recommendations', []):
                report_lines.append(f"- {recommendation}")
            
            report_lines.append("")
        
        # Сохранение текстового отчета
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"Текстовый отчет сохранен в {output_path}")
    
    def _generate_dashboard(self, analysis_results: Dict[str, Any], output_path: str) -> None:
        """Генерация интерактивного дашборда."""
        # Здесь можно реализовать генерацию дашборда с использованием библиотек
        # like Plotly Dash, Panel, или просто HTML с JavaScript
        # Пока создаем простой HTML-отчет
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Анализ дистрибуционной сети Т2</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
                .section { margin-bottom: 30px; }
                .metric { background-color: #f5f5f5; padding: 10px; margin: 5px 0; }
            </style>
        </head>
        <body>
            <h1>Анализ дистрибуционной сети Т2</h1>
            <p>Дата генерации: {date}</p>
        """.format(date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Добавление секций анализа
        if 'coverage_analysis' in analysis_results:
            coverage = analysis_results['coverage_analysis']
            html_content += """
            <div class="section">
                <h2>Анализ покрытия</h2>
            """
            
            for metric, value in coverage.get('metrics', {}).items():
                html_content += f'<div class="metric"><strong>{metric}:</strong> {value}</div>'
            
            html_content += "</div>"
        
        html_content += """
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Дашборд сохранен в {output_path}")
    
    def generate_executive_summary(self, analysis_results: Dict[str, Any]) -> str:
        """
        Генерация краткого резюме для руководства.
        
        Args:
            analysis_results: Результаты анализов
            
        Returns:
            Краткое резюме в формате текста
        """
        summary_lines = []
        summary_lines.append("КРАТКОЕ РЕЗЮМЕ АНАЛИЗА ДИСТРИБУЦИОННОЙ СЕТИ Т2")
        summary_lines.append("=" * 60)
        
        # Ключевые метрики
        if 'coverage_analysis' in analysis_results:
            coverage = analysis_results['coverage_analysis']
            metrics = coverage.get('metrics', {})
            
            summary_lines.append(f"Общее количество точек: {metrics.get('total_locations', 0)}")
            summary_lines.append(f"Городов с покрытием: {metrics.get('cities_covered', 0)}")
            summary_lines.append(f"Среднее количество точек на город: {metrics.get('avg_locations_per_city', 0):.2f}")
        
        # Ключевые рекомендации
        summary_lines.append("")
        summary_lines.append("КЛЮЧЕВЫЕ РЕКОМЕНДАЦИИ:")
        summary_lines.append("")
        
        # Сбор рекомендаций из всех анализов
        all_recommendations = []
        
        for analysis_name, analysis_data in analysis_results.items():
            if 'recommendations' in analysis_data:
                all_recommendations.extend(analysis_data['recommendations'])
        
        # Вывод топ-5 самых важных рекомендаций
        for i, recommendation in enumerate(all_recommendations[:5], 1):
            summary_lines.append(f"{i}. {recommendation}")
        
        return '\n'.join(summary_lines)
