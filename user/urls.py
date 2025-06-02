from django.urls import path
from . import views
from .views import app_user, app_login, verify_token  
urlpatterns = [
    path('app_signup/', app_user, name='app_user'),  # Endpoint for user signup
    path('app_login/', app_login, name='app_login'),  # Endpoint for user login
    path('verify_token/', verify_token, name='verify_token'),  # Endpoint for token verification
]