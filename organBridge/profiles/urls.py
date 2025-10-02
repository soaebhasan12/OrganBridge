from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.home, name='home'),  # Main landing page
    path('home/', views.profile_home, name='home_legacy'),  # Legacy home route
    
    # Existing profile routes
    path('profile/dashboard', views.profile_dashboard, name='profile_dashboard'),
    path('edit/profile', views.edit_profile, name='edit_profile'),
    path('profile/setup/', views.profile_setup, name='profile_setup'),
    path('donor/dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('recipient/dashboard/', views.recipient_dashboard, name='recipient_dashboard'),
    path('view/<int:user_id>/', views.profile_view, name='public_profile'),
    path('toggle-availability/', views.toggle_availability, name='toggle_availability'),
]