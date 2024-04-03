from django.urls import path
from .views import login, logout, drivers, cars

urlpatterns = [
    path('user/login/', login, name='login'),
    path('user/logout/', logout, name='logout'),
    path('directory/drivers/', drivers, name='drivers'),
    path('directory/cars/', cars, name='cars'),
]
