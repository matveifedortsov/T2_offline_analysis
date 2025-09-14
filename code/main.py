#!/usr/bin/env python3
"""
Основной скрипт для запуска полного цикла анализа дистрибуции Т2.
"""

import argparse
import logging
from data_collection.comprehensive_parser import ComprehensiveParser
from data_processing.data_combiner import DataCombiner
from analysis.coverage_analysis import CoverageAnalyzer
from analysis.location_analysis import LocationAnalyzer
from visualization.report_generator import ReportGenerator
from utils.logger import setup_logger
from utils.config_loader import load_config

def main():
    """Основная функция для запуска анализа."""
    # Настройка аргументов командной строки
    parser = argparse.ArgumentParser(description='Анализ дистрибуции Т2')
    parser.add_argument('--city', help='Город для анализа')
    parser.add_argument('--type', default='tele2', help='Тип организаций')
    parser.add_argument('--full', action='store_true', help='Полный цикл анализа')
    parser.add_argument('--config', default='config.py', help='Путь к файлу конфигурации')
    
    args = parser.parse_args()
    
    # Загрузка конфигурации
    config = load_config(args.config)
    
    # Настройка логирования
    logger = setup_logger(config['LOGGING_CONFIG'])
    
    if args.full:
        logger.info("Запуск полного цикла анализа")
        
        
        # 2. Парсинг детальной информации
        logger.info("Этап 2: Парсинг детальной информации")
        parser = ComprehensiveParser(config)
        parser.parse_data(args.type)
        
        # 3. Объединение и обработка данных
        logger.info("Этап 3: Обработка данных")
        combiner = DataCombiner(config)
        combiner.combine_datasets()
        
        # 4. Анализ покрытия
        logger.info("Этап 4: Анализ покрытия")
        analyzer = CoverageAnalyzer(config)
        analyzer.analyze_coverage()
        
        # 5. Анализ эффективности локаций
        logger.info("Этап 5: Анализ эффективности локаций")
        location_analyzer = LocationAnalyzer(config)
        location_analyzer.analyze_efficiency()
        
        # 6. Генерация отчетов
        logger.info("Этап 6: Генерация отчетов")
        report_generator = ReportGenerator(config)
        report_generator.generate_reports()
        
        logger.info("Анализ завершен успешно")
    else:
        logger.info("Запуск в режиме отдельных операций")
        # Реализация выбора отдельных операций

if __name__ == "__main__":
    main()
