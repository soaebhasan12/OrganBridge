# organBridge/urls.py
from django.urls import path, include
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from profiles.views import home  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Direct home view
    path('profiles/', include('profiles.urls', namespace='profiles')),
    path('accounts/', include('accounts.urls')),
    path('matches/', include('matches.urls')),
    path('ml_model/', staff_member_required(include('ml_model.urls'))),
]