"""
Модуль для оценки качества моделей.
"""

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import pandas as pd
import numpy as np

class ModelEvaluator:
    def __init__(self, config):
        self.config = config
        
    def evaluate_regression_model(self, model, X_test, y_test):
        """Оценка регрессионной модели"""
        predictions = model.predict(X_test)
        
        metrics = {
            'mse': mean_squared_error(y_test, predictions),
            'mae': mean_absolute_error(y_test, predictions),
            'r2': r2_score(y_test, predictions)
        }
        
        return metrics, predictions
        
    def evaluate_clustering_model(self, model, X):
        """Оценка кластеризации"""
        labels = model.labels_
        
        metrics = {
            'silhouette_score': silhouette_score(X, labels),
            'calinski_harabasz_score': calinski_harabasz_score(X, labels)
        }
        
        return metrics, labels
        
    def feature_importance_analysis(self, model, feature_names):
        """Анализ важности признаков"""
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            feature_importance = pd.DataFrame({
                'feature': feature_names,
                'importance': importance
            }).sort_values('importance', ascending=False)
            
            return feature_importance
