"""
Модуль для подбора гиперпараметров моделей.
"""

from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor

class HyperparameterTuner:
    def __init__(self, config):
        self.config = config
        
    def tune_random_forest(self, X, y):
        """Подбор гиперпараметров для Random Forest"""
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20, 30],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        model = RandomForestRegressor(random_state=42)
        grid_search = GridSearchCV(
            estimator=model,
            param_grid=param_grid,
            cv=5,
            scoring='r2',
            n_jobs=-1
        )
        
        grid_search.fit(X, y)
        return grid_search.best_estimator_, grid_search.best_params_
        
    def tune_xgboost(self, X, y):
        """Подбор гиперпараметров для XGBoost"""
        param_dist = {
            'learning_rate': [0.01, 0.05, 0.1],
            'max_depth': [3, 5, 7],
            'subsample': [0.8, 0.9, 1.0],
            'colsample_bytree': [0.8, 0.9, 1.0],
            'n_estimators': [100, 200, 300]
        }
        
        model = xgb.XGBRegressor(random_state=42)
        random_search = RandomizedSearchCV(
            estimator=model,
            param_distributions=param_dist,
            n_iter=25,
            cv=5,
            scoring='r2',
            random_state=42,
            n_jobs=-1
        )
        
        random_search.fit(X, y)
        return random_search.best_estimator_, random_search.best_params_
