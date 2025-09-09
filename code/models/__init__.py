"""
Модуль машинного обучения для анализа дистрибуции Т2.
Содержит инструменты для обучения, оценки и обслуживания моделей.
"""

from .model_trainer import ModelTrainer
from .model_evaluator import ModelEvaluator
from .model_serving import ModelServer
from .feature_selector import FeatureSelector
from .hyperparameter_tuner import HyperparameterTuner

# Версия модуля
__version__ = "1.0.0"

# Определяем, что будет доступно при импорте *
__all__ = [
    'ModelTrainer',
    'ModelEvaluator', 
    'ModelServer',
    'FeatureSelector',
    'HyperparameterTuner',
    'load_model',
    'save_model'
]

# Утилитарные функции для быстрого доступа
def load_model(model_path, model_name):
    """Быстрая загрузка модели по имени"""
    from .model_serving import ModelServer
    server = ModelServer()
    return server.load_model(model_path, model_name)

def save_model(model, model_path, model_name):
    """Быстрое сохранение модели"""
    import joblib
    import os
    os.makedirs(model_path, exist_ok=True)
    joblib.dump(model, f"{model_path}/{model_name}.pkl")
