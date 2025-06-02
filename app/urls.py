from django.urls import path
from . import views
from .views import save_order
from .views import get_orders,  signup_user, login_user


urlpatterns = [
     path('order/', save_order),
      path('get-orders/', get_orders),
        path('signup/', signup_user),  # New endpoint to fetch data
         path('login/', login_user)  
]
