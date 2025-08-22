"""
Прогнозное моделирование для анализа дистрибуции.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
from typing import Dict, List, Any, Tuple
from utils.logger import get_logger

logger = get_logger(__name__)

class PredictiveModeling:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models = {}
        
    def build_models(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Построение прогнозных моделей.
        
        Args:
            df: DataFrame с данными о салонах связи
            
        Returns:
            Словарь с результатами моделирования
        """
        logger.info("Запуск прогнозного моделирования")
        
        # Фильтрация салонов Т2
        tele2_df = df[df['name'].str.contains('Tele2|Т2', case=False, na=False)].copy()
        
        if len(tele2_df) < 20:
            logger.warning("Недостаточно данных для построения моделей")
            return {}
        
        # Подготовка данных
        X, y = self._prepare_modeling_data(tele2_df)
        
        # Построение и оценка моделей
        results = {}
        
        # Линейная регрессия
        linear_results = self._build_linear_model(X, y)
        results['linear_regression'] = linear_results
        
        # Случайный лес
        rf_results = self._build_random_forest(X, y)
        results['random_forest'] = rf_results
        
        # Градиентный бустинг
        gb_results = self._build_gradient_boosting(X, y)
        results['gradient_boosting'] = gb_results
        
        # Выбор лучшей модели
        best_model = self._select_best_model(results)
        
        return {
            'model_results': results,
            'best_model': best_model,
            'feature_importance': self._get_feature_importance(rf_results['model'], X.columns),
            'recommendations': self._generate_modeling_recommendations(results, best_model)
        }
    
    def _prepare_modeling_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Подготовка данных для моделирования."""
        # Выбор признаков и целевой переменной
        feature_columns = [
            'rating', 'reviews_count', 'photos_count',
            'nearby_shopping_centers_count', 'nearby_cafes_count',
            'nearby_restaurants_count', 'nearby_banks_count',
            'nearby_metro_count', 'public_transport_stops_count',
            'anchor_tenants_count', 'walkability_score',
            'is_modern_facade', 'has_parking', 'has_delivery'
        ]
        
        # Оставляем только существующие колонки
        available_columns = [col for col in feature_columns if col in df.columns]
        X = df[available_columns].fillna(0)
        
        # Целевая переменная - оценка эффективности (можно заменить на реальные бизнес-метрики)
        y = df['rating'].fillna(0) * 2 + np.log1p(df['reviews_count'].fillna(0))
        
        return X, y
    
    def _build_linear_model(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Построение модели линейной регрессии."""
        # Масштабирование признаков
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Разделение данных
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        
        # Обучение модели
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Оценка модели
        y_pred = model.predict(X_test)
        
        return {
            'model': model,
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'r2': r2_score(y_test, y_pred),
            'cross_val_scores': cross_val_score(model, X_scaled, y, cv=5).tolist()
        }
    
    def _build_random_forest(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Построение модели случайного леса."""
        # Разделение данных
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Обучение модели
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Оценка модели
        y_pred = model.predict(X_test)
        
        return {
            'model': model,
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'r2': r2_score(y_test, y_pred),
            'cross_val_scores': cross_val_score(model, X, y, cv=5).tolist()
        }
    
    def _build_gradient_boosting(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Построение модели градиентного бустинга."""
        # Разделение данных
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Обучение модели
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Оценка модели
        y_pred = model.predict(X_test)
        
        return {
            'model': model,
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'r2': r2_score(y_test, y_pred),
            'cross_val_scores': cross_val_score(model, X, y, cv=5).tolist()
        }
    
    def _select_best_model(self, results: Dict[str, Any]) -> str:
        """Выбор лучшей модели на основе R²."""
        best_model = None
        best_r2 = -float('inf')
        
        for model_name, model_results in results.items():
            if model_results['r2'] > best_r2:
                best_r2 = model_results['r2']
                best_model = model_name
        
        return best_model
    
    def _get_feature_importance(self, model: Any, feature_names: pd.Index) -> List[Dict[str, Any]]:
        """Получение важности признаков."""
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1]
            
            return [{
                'feature': feature_names[i],
                'importance': float(importances[i])
            } for i in indices]
        
        return []
    
    def _generate_modeling_recommendations(self, results: Dict[str, Any], best_model: str) -> List[str]:
        """Генерация рекомендаций на основе моделирования."""
        recommendations = []
        
        # Рекомендации на основе точности моделей
        best_r2 = results[best_model]['r2']
        
        if best_r2 < 0.3:
            recommendations.append("Низкая точность моделей. Необходимы дополнительные данные или признаки")
        elif best_r2 < 0.6:
            recommendations.append("Умеренная точность моделей. Рассмотрите добавление дополнительных признаков")
        else:
            recommendations.append("Высокая точность моделей. Модели можно использовать для прогнозирования")
        
        # Рекомендации на основе важности признаков
        if 'random_forest' in results:
            feature_importance = self._get_feature_importance(
                results['random_forest']['model'], 
                results['random_forest']['model'].feature_names_in_
            )
            
            if feature_importance:
                top_features = feature_importance[:3]
                recommendations.append(
                    f"Наиболее важные признаки: {', '.join([f['feature'] for f in top_features])}. "
                    "Сфокусируйтесь на улучшении этих параметров"
                )
        
        return recommendations
    
    def predict_location_success(self, location_data: Dict[str, Any], model_type: str = 'random_forest') -> float:
        """
        Прогнозирование успешности локации.
        
        Args:
            location_data: Данные о локации
            model_type: Тип модели для прогнозирования
            
        Returns:
            Прогнозируемая оценка успешности
        """
        if model_type not in self.models:
            logger.warning(f"Модель {model_type} не обучена")
            return 0.0
        
        # Подготовка данных для прогнозирования
        # (реализация зависит от структуры location_data)
        
        # Прогнозирование
        prediction = self.models[model_type].predict([list(location_data.values())])[0]
        
        return prediction
