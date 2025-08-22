"""
Модуль для парсинга данных с помощью BeautifulSoup.
"""

from bs4 import BeautifulSoup
import re
from typing import Dict, List, Any, Optional 
from .logger import get_logger

logger = get_logger(__name__)

class ExtendedSoupContentParser:
    def __init__(self):
        self.rating_map = {
            'плохо': 1, 'удовлетворительно': 2, 'хорошо': 3, 
            'отлично': 4, 'восхитительно': 5
        }
        self.modern_keywords = ['новый', 'modern', 'стиль', 'премиум', 'люкс', 'стекло', 'светодиодный']
        
    def parse_basic_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Парсинг основной информации об организации."""
        result = {}
        
        try:
            # Название организации
            name_elem = soup.find("h1", {"class": "orgpage-header-view__header"})
            result['name'] = name_elem.getText().strip() if name_elem else ""
            
            # Адрес
            address_elem = soup.find("a", {"class": "business-contacts-view__address-link"})
            result['address'] = address_elem.getText().strip() if address_elem else ""
            
            # Телефоны
            phone_elems = soup.find_all("div", {"class": "card-phones-view__number"})
            result['phones'] = [phone.getText().strip() for phone in phone_elems] if phone_elems else []
            
            # Сайт
            website_elem = soup.find("span", {"class": "business-urls-view__text"})
            result['website'] = website_elem.getText().strip() if website_elem else ""
            
            # Время работы
            hours_elems = soup.find_all("meta", {"itemprop": "openingHours"})
            result['hours'] = [time.get('content') for time in hours_elems] if hours_elems else []
            
            # Рейтинг
            rating_elem = soup.find("span", {"class": "business-summary-rating-badge-view__rating-text"})
            if rating_elem:
                rating_text = rating_elem.getText().strip()
                result['rating'] = float(rating_text) if rating_text else 0
            else:
                result['rating'] = 0
            
            # Количество отзывов
            reviews_elem = soup.find("span", {"class": "business-reviews-view__review-count"})
            if reviews_elem:
                reviews_text = reviews_elem.getText().strip()
                result['reviews_count'] = int(''.join(filter(str.isdigit, reviews_text))) if reviews_text else 0
            else:
                result['reviews_count'] = 0
            
            # Социальные сети
            social_elems = soup.find_all("a", {"class": "button _view_secondary-gray _ui _size_medium _link"})
            result['social_links'] = [link['href'] for link in social_elems] if social_elems else []
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге основной информации: {str(e)}")
        
        return result
    
    def parse_additional_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Парсинг дополнительной информации об организации."""
        result = {}
        
        try:
            # Категории
            category_elems = soup.find_all("span", {"class": "breadcrumbs__item"})
            result['categories'] = [cat.getText().strip() for cat in category_elems][1:] if category_elems else []
            
            # Особенности
            feature_elems = soup.find_all("div", {"class": "business-features-view__feature"})
            result['features'] = [feature.getText().strip() for feature in feature_elems] if feature_elems else []
            
            # Описание
            desc_elem = soup.find("div", {"class": "business-description-view__text"})
            result['description'] = desc_elem.getText().strip() if desc_elem else ""
            
            # Оценка современности фасада
            name = result.get('name', '').lower()
            description = result.get('description', '').lower()
            result['is_modern_facade'] = any(keyword in name or keyword in description 
                                           for keyword in self.modern_keywords)
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге дополнительной информации: {str(e)}")
        
        return result
    
    def extract_coordinates(self, soup: BeautifulSoup) -> Dict[str, Optional[float]]:
        """Извлечение координат из мета-тегов."""
        try:
            meta_image = soup.find("meta", {"property": "og:image"})
            if meta_image and 'content' in meta_image.attrs:
                image_url = meta_image['content']
                coord_match = re.search(r'll=([\d\.]+)%2C([\d\.]+)', image_url)
                if coord_match:
                    return {
                        'longitude': float(coord_match.group(1)),
                        'latitude': float(coord_match.group(2))
                    }
        except Exception as e:
            logger.error(f"Ошибка при извлечении координат: {str(e)}")
        
        return {'longitude': None, 'latitude': None}
