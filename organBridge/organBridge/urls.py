# organBridge/urls.py
from django.urls import path, include
from django.contrib import admin
from profiles.views import home  # Import your home view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Direct home view
    path('profiles/', include('profiles.urls', namespace='profiles')),
    path('accounts/', include('accounts.urls')),
    path('matches/', include('matches.urls')),
    path('ml_model/', include('ml_model.urls')),
]