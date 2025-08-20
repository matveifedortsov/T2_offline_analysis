"""
Модуль для сбора данных с Яндекс.Карт и других источников.
"""

from .link_parser import LinksCollector
from .comprehensive_parser import ComprehensiveParser

__all__ = ['LinksCollector', 'ComprehensiveParser']
