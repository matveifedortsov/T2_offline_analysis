"""
Модуль для обслуживания моделей (API и прогнозирование).
"""

import joblib
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify

class ModelServer:
    def __init__(self, config):
        self.config = config
        self.loaded_models = {}
        
    def load_model(self, model_path, model_name):
        """Загрузка обученной модели"""
        model = joblib.load(f"{model_path}/{model_name}.pkl")
        self.loaded_models[model_name] = model
        return model
        
    def predict_coverage(self, features):
        """Прогнозирование покрытия для новых данных"""
        if 'coverage_predictor' not in self.loaded_models:
            raise ValueError("Модель прогнозирования покрытия не загружена")
            
        model = self.loaded_models['coverage_predictor']
        prediction = model.predict(features)
        return prediction
        
    def recommend_locations(self, features):
        """Рекомендация локаций на основе кластеризации"""
        if 'location_recommender' not in self.loaded_models:
            raise ValueError("Модель рекомендации локаций не загружена")
            
        model = self.loaded_models['location_recommender']
        cluster = model.predict(features)
        return cluster

# Пример Flask API для обслуживания моделей
app = Flask(__name__)
model_server = ModelServer()

@app.route('/predict/coverage', methods=['POST'])
def predict_coverage():
    data = request.get_json()
    features = np.array(data['features']).reshape(1, -1)
    prediction = model_server.predict_coverage(features)
    return jsonify({'prediction': prediction.tolist()})
