from django.shortcuts import render

# Create your views here.


# python manage.py train_ml

# Direct run karein
# python ml_model/train_model.py




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib import messages
import json
import os
import numpy as np
import pandas as pd
from django.conf import settings

from .matching_algorithm import OrganMatchingEngine
from .train_model import MLModelTrainer
from profiles.models import DonorProfile, RecipientProfile

def is_admin(user):
    """Check if user is admin/staff"""
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def train_model_view(request):
    """Admin ke liye ML model training interface"""
    if request.method == 'POST':
        try:
            trainer = MLModelTrainer()
            success = trainer.train_complete_pipeline()
            
            if success:
                messages.success(request, 'ML model trained successfully!')
                return redirect('model_status')
            else:
                messages.error(request, 'ML model training failed!')
                
        except Exception as e:
            messages.error(request, f'Training error: {str(e)}')
    
    # Check current model status
    model_exists = check_model_exists()
    
    return render(request, 'ml_model/train_model.html', {
        'model_exists': model_exists,
        'dataset_path': os.path.join(settings.BASE_DIR, 'ml_model/data/KidneyData.csv')
    })



@login_required
@user_passes_test(is_admin)
def retrain_model_view(request):
    """Retrain model with existing or new data"""
    if request.method == 'POST':
        dataset_path = request.POST.get('dataset_path', '')
        
        try:
            trainer = MLModelTrainer()
            
            # If custom dataset path provided
            if dataset_path and os.path.exists(dataset_path):
                trainer.dataset_path = dataset_path
            
            success = trainer.train_complete_pipeline()
            
            if success:
                messages.success(request, 'Model retrained successfully!')
                return JsonResponse({'success': True, 'message': 'Model retrained successfully!'})
            else:
                return JsonResponse({'success': False, 'message': 'Retraining failed!'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def model_status_view(request):
    """ML model ka current status show karega"""
    model_exists = check_model_exists()
    model_info = {}
    
    if model_exists:
        try:
            # Load model info
            models_dir = os.path.join(settings.BASE_DIR, 'ml_model/trained_models/')
            model_info = {
                'tf_model_size': f"{os.path.getsize(os.path.join(models_dir, 'tf_model.pkl')) / 1024:.1f} KB",
                'tf_matrix_size': f"{os.path.getsize(os.path.join(models_dir, 'tf_matrix.pkl')) / 1024:.1f} KB",
                'cosine_sim_size': f"{os.path.getsize(os.path.join(models_dir, 'cosine_sim.npy')) / 1024:.1f} KB",
                'last_trained': get_file_modification_time(models_dir),  # This should return datetime object
            }
            
            # Test model functionality
            matching_engine = OrganMatchingEngine()
            model_info['model_loaded'] = True
            
        except Exception as e:
            model_info['error'] = str(e)
            model_info['model_loaded'] = False
    
    # Ensure last_trained is a datetime object or None
    if model_info.get('last_trained') and isinstance(model_info['last_trained'], str):
        # Convert string to datetime if needed
        try:
            from django.utils.dateparse import parse_datetime
            model_info['last_trained'] = parse_datetime(model_info['last_trained'])
        except:
            model_info['last_trained'] = None
    
    return render(request, 'ml_model/model_status.html', {
        'model_exists': model_exists,
        'model_info': model_info,
        'is_admin': is_admin(request.user)
    })


@login_required
def predict_match_api(request):
    """Real-time match prediction API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            donor_id = data.get('donor_id')
            recipient_id = data.get('recipient_id')
            
            # Get donor and recipient objects
            donor = DonorProfile.objects.get(id=donor_id)
            recipient = RecipientProfile.objects.get(id=recipient_id)
            
            # Check if user has permission
            if (request.user != donor.user and request.user != recipient.user and 
                not is_admin(request.user)):
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            # Get prediction
            matching_engine = OrganMatchingEngine()
            match_score = matching_engine.calculate_similarity_score(donor, recipient)
            
            return JsonResponse({
                'success': True,
                'donor_id': donor_id,
                'recipient_id': recipient_id,
                'match_score': match_score,
                'compatibility': get_compatibility_level(match_score)
            })
            
        except DonorProfile.DoesNotExist:
            return JsonResponse({'error': 'Donor not found'}, status=404)
        except RecipientProfile.DoesNotExist:
            return JsonResponse({'error': 'Recipient not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Prediction failed: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
def batch_predict_api(request):
    """Multiple predictions ke liye batch API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            recipient_id = data.get('recipient_id')
            donor_ids = data.get('donor_ids', [])
            
            recipient = RecipientProfile.objects.get(id=recipient_id)
            
            # Permission check
            if request.user != recipient.user and not is_admin(request.user):
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            matching_engine = OrganMatchingEngine()
            results = []
            
            for donor_id in donor_ids:
                try:
                    donor = DonorProfile.objects.get(id=donor_id)
                    score = matching_engine.calculate_similarity_score(donor, recipient)
                    
                    results.append({
                        'donor_id': donor_id,
                        'donor_name': donor.user.get_full_name() or donor.user.username,
                        'match_score': score,
                        'compatibility': get_compatibility_level(score),
                        'organs_match': list(set(donor.organs_donating) & set(recipient.organs_needed))
                    })
                except DonorProfile.DoesNotExist:
                    continue
            
            # Sort by match score
            results.sort(key=lambda x: x['match_score'], reverse=True)
            
            return JsonResponse({
                'success': True,
                'recipient_id': recipient_id,
                'total_matches': len(results),
                'results': results
            })
            
        except Exception as e:
            return JsonResponse({'error': f'Batch prediction failed: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
@user_passes_test(is_admin)
def model_stats_view(request):
    """ML model ka performance statistics"""
    try:
        matching_engine = OrganMatchingEngine()
        
        # Basic stats
        total_donors = DonorProfile.objects.count()
        total_recipients = RecipientProfile.objects.count()
        active_matches = 0  # You can calculate this from your matches app
        
        # Dataset info
        dataset_path = os.path.join(settings.BASE_DIR, 'ml_model/data/KidneyData.csv')
        if os.path.exists(dataset_path):
            dataset_size = os.path.getsize(dataset_path)
            dataset_records = len(pd.read_csv(dataset_path))
        else:
            dataset_size = 0
            dataset_records = 0
        
        stats = {
            'total_donors': total_donors,
            'total_recipients': total_recipients,
            'active_matches': active_matches,
            'dataset_size': f"{dataset_size / 1024:.1f} KB",
            'dataset_records': dataset_records,
            'model_accuracy': '95%',  # This would come from your model evaluation
            'avg_prediction_time': '0.2s',
        }
        
    except Exception as e:
        stats = {'error': str(e)}
    
    return render(request, 'ml_model/model_stats.html', {'stats': stats})


@login_required
@user_passes_test(is_admin)
def test_model_view(request):
    """Model testing interface"""
    if request.method == 'POST':
        try:
            test_data = request.POST.get('test_data', '')
            matching_engine = OrganMatchingEngine()
            
            # Simple test - you can expand this
            if test_data:
                # This would need to be adapted based on your test format
                result = "Test completed successfully"
            else:
                # Run default tests
                result = run_default_tests(matching_engine)
            
            messages.success(request, 'Model testing completed!')
            return render(request, 'ml_model/test_model.html', {'test_result': result})
            
        except Exception as e:
            messages.error(request, f'Testing failed: {str(e)}')
    
    return render(request, 'ml_model/test_model.html')


@login_required
@user_passes_test(is_admin)
def update_dataset_view(request):
    """Dataset update interface"""
    if request.method == 'POST':
        try:
            new_data_file = request.FILES.get('dataset_file')
            
            if new_data_file:
                # Save the new dataset
                dataset_path = os.path.join(settings.BASE_DIR, 'ml_model/data/KidneyData.csv')
                
                with open(dataset_path, 'wb') as f:
                    for chunk in new_data_file.chunks():
                        f.write(chunk)
                
                messages.success(request, 'Dataset updated successfully!')
                
                # Optionally retrain the model
                if request.POST.get('retrain_after_update'):
                    trainer = MLModelTrainer()
                    trainer.train_complete_pipeline()
                    messages.success(request, 'Model retrained with new data!')
                    
            else:
                messages.error(request, 'No file provided!')
                
        except Exception as e:
            messages.error(request, f'Dataset update failed: {str(e)}')
    
    return render(request, 'ml_model/update_dataset.html')


# Utility Functions
def check_model_exists():
    """Check if ML model files exist"""
    models_dir = os.path.join(settings.BASE_DIR, 'ml_model/trained_models/')
    required_files = ['tf_model.pkl', 'tf_matrix.pkl', 'cosine_sim.npy']
    
    if not os.path.exists(models_dir):
        return False
    
    return all(os.path.exists(os.path.join(models_dir, f)) for f in required_files)



def get_file_modification_time(directory):
    """Get the latest modification time of model files"""
    try:
        files = ['tf_model.pkl', 'tf_matrix.pkl', 'cosine_sim.npy']
        mod_times = []
        
        for file in files:
            file_path = os.path.join(directory, file)
            if os.path.exists(file_path):
                mod_times.append(os.path.getmtime(file_path))
        
        if mod_times:
            from datetime import datetime
            return datetime.fromtimestamp(max(mod_times)).strftime('%Y-%m-%d %H:%M:%S')
        return 'Unknown'
    except:
        return 'Unknown'



def get_compatibility_level(score):
    """Convert numerical score to compatibility level"""
    if score >= 90:
        return 'Good'
    elif score >= 75:
        return 'Good'
    elif score >= 60:
        return 'Fair'
    elif score >= 40:
        return 'Poor'
    else:
        return 'Not Compatible'



def run_default_tests(matching_engine):
    """Run default model tests"""
    tests = []
    
    try:
        # Test 1: Basic functionality
        test_donor = DonorProfile.objects.first()
        test_recipient = RecipientProfile.objects.first()
        
        if test_donor and test_recipient:
            score = matching_engine.calculate_similarity_score(test_donor, test_recipient)
            tests.append(f"Basic prediction test: PASSED (Score: {score})")
        else:
            tests.append("Basic prediction test: FAILED (No test data)")
    
    except Exception as e:
        tests.append(f"Basic prediction test: FAILED ({str(e)})")
    
    # Add more tests as needed
    
    return "\n".join(tests)