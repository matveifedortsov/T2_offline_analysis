"""
Константы проекта.
"""

# Селекторы для парсинга Яндекс.Карт
SELECTORS = {
    "name": "h1.orgpage-header-view__header",
    "address": "a.business-contacts-view__address-link",
    "phone": "div.card-phones-view__number",
    "website": "span.business-urls-view__text",
    "hours": "meta[itemprop='openingHours']",
    "rating": "span.business-summary-rating-badge-view__rating-text",
    "reviews_count": "span.business-reviews-view__review-count",
    "social_links": "a.button._view_secondary-gray._ui._size_medium._link",
    "categories": "span.breadcrumbs__item",
    "features": "div.business-features-view__feature",
    "description": "div.business-description-view__text"
}

# Типы организаций
ORG_TYPES = {
    "tele2": "салон связи Tele2",
    "mts": "салон связи МТС",
    "beeline": "салон связи Билайн",
    "megafon": "салон связи МегаФон",
    "electronics": "магазин электроники",
    "shopping_center": "торговый центр",
    "bank": "банк",
    "atm": "банкомат"
}

# Коды городов
CITY_CODES = {
    "Москва": "msk",
    "Санкт-Петербург": "spb",
    "Новосибирск": "nsk",
    "Екатеринбург": "ekb",
    "Казань": "kzn",
    "Нижний Новгород": "nnv",
    "Челябинск": "che",
    "Самара": "sam",
    "Омск": "oms",
    "Ростов-на-Дону": "rnd"
}

# Стандартные настройки
DEFAULT_CONFIG = {
    "delay_min": 2,
    "delay_max": 5,
    "max_retries": 3,
    "timeout": 30,
    "radius": 1000
}
