"""
Модуль для отбора и преобразования признаков.
"""

from sklearn.feature_selection import SelectKBest, f_regression, RFE
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
import pandas as pd

class FeatureSelector:
    def __init__(self, config):
        self.config = config
        
    def select_features_rfe(self, X, y, estimator, n_features):
        """Отбор признаков с помощью RFE"""
        selector = RFE(estimator, n_features_to_select=n_features)
        selector.fit(X, y)
        return selector.transform(X), selector.support_
        
    def select_features_kbest(self, X, y, k=10):
        """Отбор признаков с помощью SelectKBest"""
        selector = SelectKBest(score_func=f_regression, k=k)
        selector.fit(X, y)
        return selector.transform(X), selector.get_support()
        
    def create_polynomial_features(self, X, degree=2):
        """Создание полиномиальных признаков"""
        poly = PolynomialFeatures(degree=degree, include_bias=False)
        return poly.fit_transform(X)
