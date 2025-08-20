"""
Модуль для управления WebDriver.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

class WebDriverManager:
    def __init__(self, config):
        self.config = config
        
    def get_driver(self, browser_type="chrome"):
        """Получение настроенного WebDriver."""
        if browser_type.lower() == "chrome":
            return self._get_chrome_driver()
        elif browser_type.lower() == "firefox":
            return self._get_firefox_driver()
        else:
            raise ValueError(f"Unsupported browser type: {browser_type}")
    
    def _get_chrome_driver(self):
        """Настройка ChromeDriver."""
        chrome_options = Options()
        
        # Добавление опций из конфига
        if self.config.get('CHROME_OPTIONS'):
            for option in self.config['CHROME_OPTIONS']:
                chrome_options.add_argument(option)
                
        # Настройка для headless-режима
        if self.config.get('HEADLESS', False):
            chrome_options.add_argument("--headless")
            
        return webdriver.Chrome(
            ChromeDriverManager().install(),
            options=chrome_options
        )
    
    def _get_firefox_driver(self):
        """Настройка FirefoxDriver."""
        # Реализация для Firefox
        pass
