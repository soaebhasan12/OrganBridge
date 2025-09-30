import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class MLModelTrainer:
    def __init__(self):
        self.dataset_path = os.path.join(settings.BASE_DIR, 'ml_model/data/KidneyData.csv')
        self.models_dir = os.path.join(settings.BASE_DIR, 'ml_model/trained_models/')
        
        # Create directories if they don't exist
        os.makedirs(self.models_dir, exist_ok=True)
        
    def load_and_preprocess_data(self):
        """Dataset load karega aur preprocess karega"""
        try:
            # Load dataset
            data = pd.read_csv(self.dataset_path)
            logger.info(f"Dataset loaded successfully. Shape: {data.shape}")
            
            # Display basic info
            print("Dataset Info:")
            print(f"Total records: {len(data)}")
            print(f"Columns: {list(data.columns)}")
            print("\nFirst 5 rows:")
            print(data.head())
            
            # Data cleaning - remove unnecessary columns
            if 'Time' in data.columns:
                data = data.drop(columns=['Time'])
            
            # Convert all columns to string for TF-IDF processing
            data = data.astype(str)
            
            # Create combined category column
            data['category'] = data['City'].str.cat(data[['Gender','Race','Age','Blood Type','PosNeg','Smoke','Drug','Alcohol','AvgSleep']], sep=',')
            
            logger.info("Data preprocessing completed successfully")
            return data
            
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            raise e
    
    def train_tfidf_model(self, data):
        """TF-IDF model train karega - FIXED VERSION"""
        try:
            # Corpus preparation
            corpus = data['category']
            print(f"\nTraining TF-IDF model on {len(corpus)} records...")
            
            # TF-IDF Vectorizer with optimized parameters
            tf_model = TfidfVectorizer(
                max_features=200,
                max_df=0.25,
                min_df=0.01,
                stop_words='english',
                lowercase=True,
                analyzer='word'
            )
            
            # Fit and transform the data - FIX: Use toarray() instead of todense()
            tf_matrix = tf_model.fit_transform(corpus).toarray()  # CHANGED: todense() -> toarray()
            
            print(f"TF-IDF Matrix shape: {tf_matrix.shape}")
            print(f"Vocabulary size: {len(tf_model.vocabulary_)}")
            
            # Calculate cosine similarity matrix - FIX: Use numpy array directly
            cosine_sim = cosine_similarity(tf_matrix)  # CHANGED: No need for conversion
            
            print(f"Cosine similarity matrix shape: {cosine_sim.shape}")
            
            return tf_model, tf_matrix, cosine_sim
            
        except Exception as e:
            logger.error(f"Error training TF-IDF model: {str(e)}")
            raise e
    
    def save_models(self, tf_model, tf_matrix, cosine_sim):
        """Trained models save karega - FIXED VERSION"""
        try:
            # Save TF-IDF model
            tf_model_path = os.path.join(self.models_dir, 'tf_model.pkl')
            with open(tf_model_path, 'wb') as f:
                pickle.dump(tf_model, f)
            
            # Save TF-IDF matrix as numpy array - FIXED
            tf_matrix_path = os.path.join(self.models_dir, 'tf_matrix.npy')  # CHANGED: .pkl -> .npy
            np.save(tf_matrix_path, tf_matrix)  # CHANGED: pickle.dump -> np.save
            
            # Save cosine similarity matrix
            cosine_sim_path = os.path.join(self.models_dir, 'cosine_sim.npy')
            np.save(cosine_sim_path, cosine_sim)
            
            print("\nModels saved successfully:")
            print(f"TF-IDF Model: {tf_model_path}")
            print(f"TF-IDF Matrix: {tf_matrix_path}")
            print(f"Cosine Similarity: {cosine_sim_path}")
            
            # Check file sizes
            print(f"\nFile sizes:")
            print(f"TF Model: {os.path.getsize(tf_model_path) / 1024:.2f} KB")
            print(f"TF Matrix: {os.path.getsize(tf_matrix_path) / 1024:.2f} KB")
            print(f"Cosine Sim: {os.path.getsize(cosine_sim_path) / 1024:.2f} KB")
            
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
            raise e
    
    def test_model(self, tf_model):
        """Trained model ka basic test karega - FIXED VERSION"""
        try:
            print("\nTesting trained model...")
            
            # Test cases
            test_cases = [
                "Seattle,Boy,White,28,O,Neg,STrue,DFalse,AFalse,6",
                "New York,Girl,Black,35,A,Pos,SFalse,DTrue,ATrue,7",
                "Los Angeles,Boy,Asian,42,B,Neg,STrue,DFalse,AFalse,8"
            ]
            
            for i, test_case in enumerate(test_cases):
                test_vector = tf_model.transform([test_case]).toarray()  # CHANGED: todense() -> toarray()
                print(f"Test case {i+1}: {test_vector.shape} - {test_case[:50]}...")
            
            print("Model testing completed successfully!")
            
        except Exception as e:
            logger.error(f"Error testing model: {str(e)}")
            raise e
    
    def train_complete_pipeline(self):
        """Complete training pipeline run karega"""
        try:
            print("🚀 Starting ML Model Training Pipeline...")
            print("=" * 50)
            
            # Step 1: Load and preprocess data
            data = self.load_and_preprocess_data()
            
            # Step 2: Train TF-IDF model
            tf_model, tf_matrix, cosine_sim = self.train_tfidf_model(data)
            
            # Step 3: Save trained models
            self.save_models(tf_model, tf_matrix, cosine_sim)
            
            # Step 4: Test the model
            self.test_model(tf_model)
            
            print("\n✅ Training completed successfully!")
            print("=" * 50)
            
            return True
            
        except Exception as e:
            logger.error(f"Training pipeline failed: {str(e)}")
            print(f"❌ Training failed: {str(e)}")
            return False


# Django management command ke liye utility function
def train_ml_model():
    """Django se call karne ke liye function"""
    trainer = MLModelTrainer()
    return trainer.train_complete_pipeline()


# Standalone run ke liye
if __name__ == "__main__":
    print("🧠 OrganBridge ML Model Training")
    print("This script trains the matching algorithm using KidneyData.csv")
    
    # Django settings configure karo agar standalone run karna ho
    import django
    import os
    import sys
    
    # Django project root add karo
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'organBridge.settings')
    
    try:
        django.setup()
        success = train_ml_model()
        if success:
            print("\n🎉 ML Model ready for use in OrganBridge!")
        else:
            print("\n💥 ML Model training failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Make sure Django is properly configured")
        sys.exit(1)