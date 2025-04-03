from django.urls import path
from . import views

# Register your models here. path for app views
urlpatterns = [
   path('app/', views.index),
   path('app2/', views.index2),
   path('web/', views.web),
]