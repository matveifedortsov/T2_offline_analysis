import subprocess
import sys
import time
import os
from config import CITIES

def run_analysis_for_city(city):
    """Запуск анализа для конкретного города"""
    print(f"Запуск анализа для города: {city}")
    
    try:
        # Формирование команды
        cmd = [sys.executable, "run_analysis.py", "--city", city, "--headless"]
        
        # Запуск процесса
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Чтение вывода в реальном времени
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # Проверка кода возврата
        return_code = process.poll()
        if return_code != 0:
            print(f"Ошибка при обработке города {city}. Код возврата: {return_code}")
            # Вывод ошибок
            for line in process.stderr:
                print(f"ERROR: {line.strip()}")
            
        return return_code == 0
        
    except Exception as e:
        print(f"Исключение при обработке города {city}: {str(e)}")
        return False

def main():
    """Основная функция для запуска анализа всех городов"""
    print("Запуск анализа для всех городов из config.py")
    
    # Проверяем, существует ли config.py и содержит ли CITIES
    try:
        from config import CITIES
        print(f"Найдено городов: {len(CITIES)}")
    except ImportError:
        print("Ошибка: Не удалось импортировать config.py")
        return
    except AttributeError:
        print("Ошибка: В config.py не определен список CITIES")
        return
    
    successful_cities = []
    failed_cities = []
    
    # Запуск для каждого города
    for i, city in enumerate(CITIES, 1):
        print(f"\n--- Обработка города {i}/{len(CITIES)}: {city} ---")
        
        success = run_analysis_for_city(city)
        
        if success:
            successful_cities.append(city)
            print(f"Город {city} успешно обработан")
        else:
            failed_cities.append(city)
            print(f"Ошибка при обработке города {city}")
        
        # Пауза между городами для избежания блокировок
        if i < len(CITIES):
            print("Ожидание 15 секунд перед следующим городом...")
            time.sleep(15)
    
    # Вывод итогов
    print("\n" + "="*50)
    print("ИТОГИ ВЫПОЛНЕНИЯ:")
    print(f"Успешно обработано: {len(successful_cities)} городов")
    print(f"Не удалось обработать: {len(failed_cities)} городов")
    
    if failed_cities:
        print("Города с ошибками:")
        for city in failed_cities:
            print(f"  - {city}")
    
    if successful_cities:
        print("Успешно обработанные города:")
        for city in successful_cities:
            print(f"  - {city}")

if __name__ == "__main__":
    main()
