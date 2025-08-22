"""
Кластеризация данных для выявления паттернов.
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from typing import Dict, List, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class DataClustering:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    def perform_clustering(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Выполнение кластеризации данных.
        
        Args:
            df: DataFrame с данными о салонах связи
            
        Returns:
            Словарь с результатами кластеризации
        """
        logger.info("Запуск кластеризации данных")
        
        # Подготовка данных для кластеризации
        X = self._prepare_clustering_data(df)
        
        if len(X) < 10:
            logger.warning("Недостаточно данных для кластеризации")
            return {}
        
        # Выполнение кластеризации
        kmeans_results = self._kmeans_clustering(X)
        dbscan_results = self._dbscan_clustering(X)
        
        # Визуализация результатов
        self._visualize_clusters(X, kmeans_results['labels'], 'kmeans')
        self._visualize_clusters(X, dbscan_results['labels'], 'dbscan')
        
        return {
            'kmeans': kmeans_results,
            'dbscan': dbscan_results,
            'interpretation': self._interpret_clusters(df, kmeans_results['labels']),
            'recommendations': self._generate_clustering_recommendations(kmeans_results, dbscan_results)
        }
    
    def _prepare_clustering_data(self, df: pd.DataFrame) -> np.ndarray:
        """Подготовка данных для кластеризации."""
        # Выбор числовых признаков для кластеризации
        numeric_features = [
            'rating', 'reviews_count', 'photos_count',
            'nearby_shopping_centers_count', 'nearby_cafes_count',
            'nearby_restaurants_count', 'nearby_banks_count',
            'nearby_metro_count', 'public_transport_stops_count',
            'anchor_tenants_count', 'walkability_score'
        ]
        
        # Оставляем только существующие и числовые колонки
        available_features = [f for f in numeric_features if f in df.columns and pd.api.types.is_numeric_dtype(df[f])]
        
        if not available_features:
            return np.array([])
            
        # Заполнение пропущенных значений
        X = df[available_features].fillna(0).values
        
        # Масштабирование данных
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        return X_scaled
    
    def _kmeans_clustering(self, X: np.ndarray) -> Dict[str, Any]:
        """Кластеризация методом K-means."""
        # Определение оптимального количества кластеров методом локтя
        wcss = []
        max_clusters = min(10, len(X))
        
        for i in range(1, max_clusters + 1):
            kmeans = KMeans(n_clusters=i, random_state=42)
            kmeans.fit(X)
            wcss.append(kmeans.inertia_)
        
        # Выбор оптимального количества кластеров (упрощенная версия)
        optimal_clusters = 3  # В реальном проекте нужно использовать более сложный метод
        
        # Кластеризация с оптимальным количеством кластеров
        kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
        labels = kmeans.fit_predict(X)
        
        return {
            'method': 'kmeans',
            'n_clusters': optimal_clusters,
            'labels': labels.tolist(),
            'centers': kmeans.cluster_centers_.tolist(),
            'wcss': wcss
        }
    
    def _dbscan_clustering(self, X: np.ndarray) -> Dict[str, Any]:
        """Кластеризация методом DBSCAN."""
        # Кластеризация DBSCAN
        dbscan = DBSCAN(eps=0.5, min_samples=5)
        labels = dbscan.fit_predict(X)
        
        # Количество кластеров (исключая шум)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        
        return {
            'method': 'dbscan',
            'n_clusters': n_clusters,
            'labels': labels.tolist(),
            'noise_points': np.sum(labels == -1) if len(labels) > 0 else 0
        }
    
    def _visualize_clusters(self, X: np.ndarray, labels: List[int], method: str) -> None:
        """Визуализация результатов кластеризации."""
        if len(X) == 0 or len(labels) == 0:
            return
            
        # Уменьшение размерности для визуализации
        pca = PCA(n_components=2)
        X_reduced = pca.fit_transform(X)
        
        # Создание графика
        plt.figure(figsize=(10, 7))
        scatter = plt.scatter(X_reduced[:, 0], X_reduced[:, 1], c=labels, cmap='viridis', alpha=0.6)
        plt.colorbar(scatter)
        plt.title(f'Кластеризация методом {method.upper()}')
        plt.xlabel('Компонента 1')
        plt.ylabel('Компонента 2')
        
        # Сохранение графика
        import os
        os.makedirs('reports/visualizations', exist_ok=True)
        plt.savefig(f'reports/visualizations/{method}_clustering.png')
        plt.close()
    
    def _interpret_clusters(self, df: pd.DataFrame, labels: List[int]) -> Dict[str, Any]:
        """Интерпретация результатов кластеризации."""
        if len(labels) == 0 or len(df) != len(labels):
            return {}
            
        df = df.copy()
        df['cluster'] = labels
        
        interpretation = {}
        
        for cluster_id in set(labels):
            cluster_df = df[df['cluster'] == cluster_id]
            
            # Характеристики кластера
            interpretation[cluster_id] = {
                'size': len(cluster_df),
                'avg_rating': cluster_df['rating'].mean() if 'rating' in cluster_df.columns else 0,
                'avg_reviews': cluster_df['reviews_count'].mean() if 'reviews_count' in cluster_df.columns else 0,
                'cities': cluster_df['city'].value_counts().to_dict()
            }
        
        return interpretation
    
    def _generate_clustering_recommendations(self, kmeans_results: Dict[str, Any], 
                                           dbscan_results: Dict[str, Any]) -> List[str]:
        """Генерация рекомендаций на основе кластеризации."""
        recommendations = []
        
        # Рекомендации на основе K-means
        if kmeans_results.get('n_clusters', 0) > 1:
            recommendations.append(
                f"Выявлено {kmeans_results['n_clusters']} distinct кластеров локаций. "
                "Рекомендуется разработка отдельных стратегий для каждого кластера"
            )
        
        # Рекомендации на основе DBSCAN
        if dbscan_results.get('noise_points', 0) > 0:
            recommendations.append(
                f"Обнаружено {dbscan_results['noise_points']} точек, не входящих в кластеры. "
                "Рекомендуется дополнительный анализ этих аномальных точек"
            )
        
        return recommendations
