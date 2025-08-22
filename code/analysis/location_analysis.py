"""
Анализ эффективности локаций.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from typing import Dict, List, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class LocationAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = None
        
    def analyze_efficiency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Анализ эффективности локаций.
        
        Args:
            df: DataFrame с данными о салонах связи
            
        Returns:
            Словарь с результатами анализа эффективности
        """
        logger.info("Запуск анализа эффективности локаций")
        
        # Фильтрация салонов Т2
        tele2_df = df[df['name'].str.contains('Tele2|Т2', case=False, na=False)].copy()
        
        if len(tele2_df) < 10:
            logger.warning("Недостаточно данных для анализа эффективности")
            return {}
        
        # Подготовка данных для моделирования
        X, y = self._prepare_features(tele2_df)
        
        # Обучение или загрузка модели
        self.model = self._train_or_load_model(X, y)
        
        # Предсказание эффективности
        predictions = self.model.predict(X)
        tele2_df['efficiency_score'] = predictions
        
        # Категоризация эффективности
        tele2_df['efficiency_category'] = pd.cut(
            tele2_df['efficiency_score'],
            bins=[0, 10, 15, 20, 25],
            labels=['Низкая', 'Средняя', 'Высокая', 'Очень высокая']
        )
        
        # Генерация рекомендаций
        recommendations = self._generate_recommendations(tele2_df)
        
        return {
            'efficiency_scores': tele2_df[['name', 'address', 'efficiency_score', 'efficiency_category']].to_dict('records'),
            'feature_importance': self._get_feature_importance(X.columns),
            'recommendations': recommendations,
            'model_performance': self._evaluate_model(X, y)
        }
    
    def _prepare_features(self, df: pd.DataFrame) -> tuple:
        """Подготовка признаков для модели."""
        # Выбор и преобразование признаков
        feature_columns = [
            'rating', 'reviews_count', 'photos_count',
            'nearby_shopping_centers_count', 'nearby_cafes_count',
            'nearby_restaurants_count', 'nearby_banks_count',
            'nearby_metro_count', 'public_transport_stops_count',
            'anchor_tenants_count', 'walkability_score'
        ]
        
        # Оставляем только существующие колонки
        available_columns = [col for col in feature_columns if col in df.columns]
        X = df[available_columns].fillna(0)
        
        # Целевая переменная - комбинация рейтинга и отзывов
        y = df['rating'].fillna(0) * 2 + np.log1p(df['reviews_count'].fillna(0))
        
        return X, y
    
    def _train_or_load_model(self, X: pd.DataFrame, y: pd.Series) -> RandomForestRegressor:
        """Обучение или загрузка модели."""
        model_path = self.config.get('model_path', 'models/location_efficiency_model.pkl')
        
        try:
            # Попытка загрузки существующей модели
            model = joblib.load(model_path)
            logger.info("Загружена существующая модель")
        except:
            # Обучение новой модели
            logger.info("Обучение новой модели")
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Сохранение модели
            import os
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            joblib.dump(model, model_path)
            logger.info(f"Модель сохранена в {model_path}")
        
        return model
    
    def _evaluate_model(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """Оценка производительности модели."""
        y_pred = self.model.predict(X)
        
        return {
            'mse': mean_squared_error(y, y_pred),
            'rmse': np.sqrt(mean_squared_error(y, y_pred)),
            'r2': r2_score(y, y_pred)
        }
    
    def _get_feature_importance(self, feature_names: pd.Index) -> List[Dict[str, Any]]:
        """Получение важности признаков."""
        if self.model is None:
            return []
            
        importances = self.model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        return [{
            'feature': feature_names[i],
            'importance': float(importances[i])
        } for i in indices]
    
    def _generate_recommendations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Генерация рекомендаций по оптимизации."""
        recommendations = []
        
        # Анализ точек с низкой эффективностью
        low_efficiency = df[df['efficiency_category'] == 'Низкая']
        
        for _, row in low_efficiency.iterrows():
            rec = {
                'location': row['name'],
                'address': row['address'],
                'current_score': row['efficiency_score'],
                'recommendations': self._analyze_single_location(row)
            }
            recommendations.append(rec)
        
        return recommendations
    
    def _analyze_single_location(self, row: pd.Series) -> List[str]:
        """Анализ отдельной локации и генерация рекомендаций."""
        recommendations = []
        
        # Анализ и рекомендации на основе доступных данных
        if row.get('rating', 0) < 3:
            recommendations.append("Улучшить качество обслуживания для повышения рейтинга")
        
        if row.get('reviews_count', 0) < 5:
            recommendations.append("Стимулировать клиентов оставлять отзывы")
        
        if row.get('walkability_score', 0) < 5:
            recommendations.append("Улучшить доступность локации")
        
        if row.get('nearby_shopping_centers_count', 0) == 0:
            recommendations.append("Рассмотреть возможность размещения в ТЦ")
        
        return recommendations
