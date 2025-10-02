from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('my/account/', views.account_view, name='account'),
    path('update/', views.udpate_account, name='edit_account'),
]