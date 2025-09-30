# ml_model/apps.py mein
from django.apps import AppConfig
import os

class MlModelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ml_model'
    
    def ready(self):
        # Check if models already exist
        models_dir = os.path.join(os.path.dirname(__file__), 'trained_models')
        if not os.path.exists(models_dir) or not os.listdir(models_dir):
            from .train_model import train_ml_model
            print("Training ML model for first time...")
            train_ml_model()