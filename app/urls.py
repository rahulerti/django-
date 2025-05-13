from django.urls import path
from . import views
from .views import save_order
from .views import get_orders


urlpatterns = [
     path('order/', save_order),
      path('get-orders/', get_orders),  # New endpoint to fetch data
]
