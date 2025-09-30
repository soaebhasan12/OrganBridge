from django.urls import path
from . import views

urlpatterns = [
    path('find/', views.find_matches, name='find_matches'),
    path('my-matches/', views.my_matches, name='my_matches'),
    path('match/<int:match_id>/', views.match_detail, name='match_detail'),
    path('match/<int:match_id>/<str:status>/', views.update_match_status, name='update_match_status'),
    path('preferences/', views.match_preferences, name='match_preferences'),
    path('match/<int:match_id>/message/', views.send_message_ajax, name='send_message_ajax'),
]












# 2) reciepient_dashboard is not create yet

# 3) URL: http://127.0.0.1:8000/profiles/donor/dashboard/ - not opening

# 4) http://127.0.0.1:8000/profiles/recipient/dashboard/ - not opening

# 5) Donor and Reciepient dashbord is not opening

# 6) http://127.0.0.1:8000/accounts/profile/edit/  - edit_profile.html not created yet

# 7) http://127.0.0.1:8000/accounts/profile/edit/ - TemplateDoesNotExist

# 8) http://127.0.0.1:8000/matches/preferences/ - TemplateDoesNotExist 

# 9) http://127.0.0.1:8000/profiles/setup/ - TemplateDoesNotExist


