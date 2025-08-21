#!/usr/bin/env python3
"""
Скрипт для запуска полного цикла анализа дистрибуции Т2
"""

import argparse
import logging
import sys
import os

# Добавление src в путь для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_collection.link_parser import LinksCollector
from data_collection.comprehensive_parser import ComprehensiveParser
from data_processing.data_combiner import DataCombiner
from analysis.coverage_analysis import CoverageAnalyzer
from analysis.location_analysis import LocationAnalyzer
from visualization.report_generator import ReportGenerator
from utils.logger import setup_logger
from utils.config_loader import load_config

def main():
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description='Анализ дистрибуции Т2')
    parser.add_argument('--city', required=True, help='Город для анализа')
    parser.add_argument('--types', nargs='+', default=['tele2', 'mts', 'beeline', 'megafon'],
                       help='Типы организаций для анализа')
    parser.add_argument('--config', default='config.py', help='Путь к файлу конфигурации')
    parser.add_argument('--headless', action='store_true', help='Запуск браузера в фоновом режиме')
    parser.add_argument('--skip-collection', action='store_true', help='Пропустить сбор данных')
    parser.add_argument('--skip-analysis', action='store_true', help='Пропустить анализ')
    
    args = parser.parse_args()
    
    # Загрузка конфигурации
    config = load_config(args.config)
    
    # Обновление конфигурации из аргументов
    if args.headless:
        config['BROWSER_CONFIG']['headless'] = True
    
    # Настройка логирования
    logger = setup_logger(config.get('LOGGING_CONFIG', {}))
    
    try:
        # Этап 1: Сбор данных (если не пропущен)
        if not args.skip_collection:
            logger.info("=== ЭТАП 1: СБОР ДАННЫХ ===")
            
            for org_type in args.types:
                logger.info(f"Сбор ссылок для {org_type} в {args.city}")
                
                # Сбор ссылок
                collector = LinksCollector(config)
                links = collector.collect_links(args.city, org_type)
                
                logger.info(f"Найдено {len(links)} ссылок для {org_type}")
                
                # Парсинг детальной информации
                logger.info(f"Парсинг детальной информации для {org_type}")
                parser = ComprehensiveParser(config)
                parser.parse_data(org_type, links)
        
        # Этап 2: Обработка данных
        logger.info("=== ЭТАП 2: ОБРАБОТКА ДАННЫХ ===")
        combiner = DataCombiner(config)
        combined_data = combiner.combine_datasets()
        logger.info(f"Объединено данных: {len(combined_data)} записей")
        
        # Этап 3: Анализ (если не пропущен)
        if not args.skip_analysis:
            logger.info("=== ЭТАП 3: АНАЛИЗ ===")
            
            # Анализ покрытия
            logger.info("Анализ покрытия дистрибуционной сети")
            coverage_analyzer = CoverageAnalyzer(config)
            coverage_results = coverage_analyzer.analyze_coverage(combined_data)
            
            # Анализ эффективности локаций
            logger.info("Анализ эффективности локаций")
            location_analyzer = LocationAnalyzer(config)
            efficiency_results = location_analyzer.analyze_efficiency(combined_data)
            
            # Этап 4: Генерация отчетов
            logger.info("=== ЭТАП 4: ГЕНЕРАЦИЯ ОТЧЕТОВ ===")
            report_generator = ReportGenerator(config)
            report_generator.generate_reports({
                'coverage': coverage_results,
                'efficiency': efficiency_results,
                'city': args.city
            })
        
        logger.info("Анализ завершен успешно!")
        
    except Exception as e:
        logger.error(f"Ошибка при выполнении анализа: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
