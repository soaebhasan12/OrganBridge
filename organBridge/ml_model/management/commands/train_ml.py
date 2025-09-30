# ml_model/management/commands/train_ml.py banayein
from django.core.management.base import BaseCommand
from ml_model.train_model import train_ml_model

class Command(BaseCommand):
    help = 'Train the ML model for organ matching'
    
    def handle(self, *args, **options):
        self.stdout.write('Training ML model...')
        if train_ml_model():
            self.stdout.write(self.style.SUCCESS('ML model trained successfully!'))
        else:
            self.stdout.write(self.style.ERROR('ML model training failed!'))