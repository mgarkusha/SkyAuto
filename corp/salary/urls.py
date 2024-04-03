from django.urls import path
from .views import login, logout, salary, salary_refresh, salary_create, payslip, payment_d, salary_driver_create

urlpatterns = [
    path('user/login/', login, name='login'),
    path('user/logout/', logout, name='logout'),
    path('salary/', salary, name='salary'),
    path('salary/refresh/', salary_refresh, name='salary_refresh'),
    path('salary/create/', salary_create, name='salary_create'),
    path('salary/create/<int:driver_id>/', salary_driver_create, name='salary_driver_create'),
    path('salary/<int:driver_id>/<int:salary_id>/', payslip, name='payslip'),
    path('payment_del/<int:payment_id>/<int:driver_id>/<int:salary_id>/', payment_d, name='payment_d'),
]
