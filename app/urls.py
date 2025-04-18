from django.urls import path
from . import views
''' path('web/', views.web),
   path('app2/', views.index2),'''
# Register your models here. path for app views
urlpatterns = [
   path('save_use/', views.save_use),
]