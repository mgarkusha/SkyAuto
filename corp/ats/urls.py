from django.urls import path
from .views import login, logout, sms

urlpatterns = [
    path('user/login/', login, name='login'),
    path('user/logout/', logout, name='logout'),
    path('ats/sms/', sms, name='sms'),
    path('ats/sms/<int:in_year>/<int:in_month>/<int:in_day>/', sms, name='sms_archive'),
]
