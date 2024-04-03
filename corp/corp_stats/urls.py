from django.urls import path
from .views import login, logout, corp_y_m, billing_y_m, smena_y_m, billing_current_m, profit

urlpatterns = [
    path('user/login/', login, name='login'),
    path('user/logout/', logout, name='logout'),
    path('stat/corp_y_m/', corp_y_m, name='corp_y_m'),
    path('stat/corp_y_m/<int:in_year>/<int:in_month>/', corp_y_m, name='corp_y_m'),
    path('stat/corp_y_m/<int:in_year>/<int:in_month>/<int:in_corp_id>/', corp_y_m, name='corp_y_m'),
    path('stat/billing_y_m/', billing_y_m, name='billing_y_m'),
    path('stat/billing_current_m/', billing_current_m, name='billing_current_m'),
    path('stat/billing_current_m/<int:in_month>/', billing_current_m, name='billing_current_m'),
    path('stat/smena_y_m/', smena_y_m, name='smena_y_m'),
    path('stat/smena_y_m/<int:in_year>/', smena_y_m, name='smena_y_m'),
    path('stat/profit/', profit, name='profit'),
]
