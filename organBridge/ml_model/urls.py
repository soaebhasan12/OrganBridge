from django.urls import path
from . import views

urlpatterns = [
    # ML Model Training and Management
    path('train/', views.train_model_view, name='train_model'),
    path('retrain/', views.retrain_model_view, name='retrain_model'),
    path('status/', views.model_status_view, name='model_status'),
    
    # ML Prediction APIs
    path('predict-match/', views.predict_match_api, name='predict_match'),
    path('batch-predict/', views.batch_predict_api, name='batch_predict'),
    
    # Model Analytics
    path('stats/', views.model_stats_view, name='model_stats'),
    path('test/', views.test_model_view, name='test_model'),
    
    # Admin ML Tools
    path('admin/update-dataset/', views.update_dataset_view, name='update_dataset'),
]








# now write model_stats.html using views.py wich should work properly as our views.py. don't forget about our frontend stack, which you use in model_status.html and train_model.html . 
# page must be looks professional. as previous pages.
# add hackathon question related to this page in the model_stats.html, as a comment which interviewee can ask.
# clear the why, where and how related to this file, as a comment in this files.
# do this approach in every chat solution.