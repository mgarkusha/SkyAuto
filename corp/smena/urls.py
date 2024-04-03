from django.urls import path
from .views import login, logout, smena, smena_create, smena_update, smena_delete

urlpatterns = [
    path('user/login/', login, name='login'),
    path('user/logout/', logout, name='logout'),
    path('smena/', smena, name='smena'),
    path('smena/<int:driver_id>/<int:status>/', smena_create, name='smena_create'),
    path('smena/<int:smena_id>/', smena_update, name='smena_update'),
    path('smena/smena_delete/<int:smena_id>', smena_delete, name='smena_delete'),
    path('smena/<int:driver_id>/<int:status>/<int:year>/<int:month>/<int:day>/<int:hour>/<int:min>/', smena_create,
         name='smena_create'),
]
