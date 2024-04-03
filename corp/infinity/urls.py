from django.urls import path
from .views import login, logout, chart, chart_driver, chart_corp

urlpatterns = [
    path('user/login/', login, name='login'),
    path('user/logout/', logout, name='logout'),
    path('chart/', chart, name='chart'),
    path('chart/driver/<int:driver_id>/', chart_driver, name='chart_driver'),
    path('chart/corp/<int:corp_id>/', chart_corp, name='chart_corp'),
]
