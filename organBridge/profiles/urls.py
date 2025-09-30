from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('dashboard/', views.profile_dashboard, name='profile_dashboard'),
    path('donor/dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('recipient/dashboard/', views.recipient_dashboard, name='recipient_dashboard'),
    path('setup/', views.profile_setup, name='profile_setup'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('view/<int:user_id>/', views.profile_view, name='public_profile'),
    path('toggle-availability/', views.toggle_availability, name='toggle_availability'),
]