import pandas as pd
import numpy as np
import os
import pickle
from django.conf import settings

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError as e:
    print(f"Scikit-learn import error: {e}")
    SKLEARN_AVAILABLE = False

class OrganMatchingEngine:
    def __init__(self):
        if not SKLEARN_AVAILABLE:
            raise ImportError("Scikit-learn is not available. Please install it.")
        
        self.tf_model = None
        self.tf_matrix = None
        self.cosine_sim = None
        self.load_models()
    
    def load_models(self):
        """Load trained ML models - FIXED VERSION"""
        try:
            model_path = os.path.join(settings.BASE_DIR, 'ml_model/trained_models/')
            
            if not os.path.exists(model_path):
                raise FileNotFoundError("Model files not found. Please train the model first.")
            
            # Load TF-IDF model
            with open(os.path.join(model_path, 'tf_model.pkl'), 'rb') as f:
                self.tf_model = pickle.load(f)
            
            # Load TF-IDF matrix as numpy array - FIXED
            self.tf_matrix = np.load(os.path.join(model_path, 'tf_matrix.npy'))  # CHANGED: .pkl -> .npy
            
            # Load cosine similarity matrix
            self.cosine_sim = np.load(os.path.join(model_path, 'cosine_sim.npy'))
            
            print("ML models loaded successfully!")
            
        except Exception as e:
            print(f"Error loading models: {e}")
            # Fallback to basic matching without ML
            self.tf_model = None
    
    def calculate_similarity_score(self, donor, recipient):
        """ML-based similarity score calculate karega - FIXED VERSION"""
        try:
            if self.tf_model is None:
                # Fallback to basic scoring if ML model not available
                return self.basic_similarity_score(donor, recipient)
            
            # Prepare data strings
            donor_str = self.prepare_donor_data(donor)
            recipient_str = self.prepare_recipient_data(recipient)
            
            # Transform to TF-IDF vectors - FIXED
            donor_vector = self.tf_model.transform([donor_str]).toarray()  # CHANGED: todense() -> toarray()
            recipient_vector = self.tf_model.transform([recipient_str]).toarray()  # CHANGED: todense() -> toarray()
            
            # Calculate cosine similarity
            similarity = cosine_similarity(donor_vector, recipient_vector)[0][0]
            
            # Convert to percentage (0-100%)
            match_score = max(0, min(100, round(similarity * 100, 2)))
            
            return match_score
            
        except Exception as e:
            print(f"ML similarity calculation failed: {e}")
            # Fallback to basic scoring
            return self.basic_similarity_score(donor, recipient)
    
    # ... (rest of the methods remain same)
    def prepare_donor_data(self, donor):
        """Donor data ko ML format mein convert karega"""
        return f"{donor.user.city},{donor.user.gender},{donor.user.race},{donor.user.age}," \
               f"{donor.user.blood_type},{donor.health_status},{donor.smoking_status}," \
               f"{donor.drug_use},{donor.alcohol_use},{donor.avg_sleep}"
    
    def prepare_recipient_data(self, recipient):
        """Recipient data ko ML format mein convert karega"""
        return f"{recipient.user.city},{recipient.user.gender},{recipient.user.race},{recipient.user.age}," \
               f"{recipient.user.blood_type},{recipient.urgency_level}"
    
    def basic_similarity_score(self, donor, recipient):
        """Basic similarity scoring (ML model unavailable hone par)"""
        score = 50  # Base score
        
        # Blood type compatibility
        if self.check_blood_compatibility(donor.user.blood_type, recipient.user.blood_type):
            score += 20
        
        # Location bonus (same city)
        if donor.user.city == recipient.user.city:
            score += 15
        
        # Health factors
        if donor.health_status == 'excellent':
            score += 10
        elif donor.health_status == 'good':
            score += 5
        
        # Urgency bonus
        if recipient.urgency_level in ['high', 'critical']:
            score += 5
        
        return min(100, score)
    
    def check_blood_compatibility(self, donor_blood, recipient_blood):
        """Blood type compatibility check"""
        compatibility_map = {
            'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
            'O+': ['O+', 'A+', 'B+', 'AB+'],
            'A-': ['A-', 'A+', 'AB-', 'AB+'],
            'A+': ['A+', 'AB+'],
            'B-': ['B-', 'B+', 'AB-', 'AB+'],
            'B+': ['B+', 'AB+'],
            'AB-': ['AB-', 'AB+'],
            'AB+': ['AB+']
        }
        return donor_blood in compatibility_map.get(recipient_blood, [])
    
    def find_matches(self, recipient, donors, top_n=10):
        """Find best matches for a recipient"""
        matches = []
        
        for donor in donors:
            # Check organ compatibility first
            if not any(organ in donor.organs_donating for organ in recipient.organs_needed):
                continue
            
            # Calculate match score
            ml_score = self.calculate_similarity_score(donor, recipient)
            
            # Apply business rules
            final_score = self.apply_business_rules(ml_score, donor, recipient)
            
            matches.append({
                'donor': donor,
                'ml_score': ml_score,
                'final_score': final_score,
                'compatibility_details': {
                    'blood_match': self.check_blood_compatibility(donor.user.blood_type, recipient.user.blood_type),
                    'organs_matched': list(set(donor.organs_donating) & set(recipient.organs_needed)),
                    'location_same': donor.user.city == recipient.user.city
                }
            })
        
        # Sort by final score
        matches.sort(key=lambda x: x['final_score'], reverse=True)
        return matches[:top_n]
    
    def apply_business_rules(self, ml_score, donor, recipient):
        """Apply additional business rules to ML score"""
        final_score = ml_score
        
        # Blood type compatibility bonus
        if self.check_blood_compatibility(donor.user.blood_type, recipient.user.blood_type):
            final_score += 10
        
        # Distance penalty (simplified)
        if donor.user.city != recipient.user.city:
            final_score -= 5
        
        # Health bonus
        if donor.health_status == 'excellent':
            final_score += 8
        elif donor.health_status == 'good':
            final_score += 4
        
        # Urgency bonus
        if recipient.urgency_level == 'critical':
            final_score += 12
        elif recipient.urgency_level == 'high':
            final_score += 8
        
        return max(0, min(100, final_score))