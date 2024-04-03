from django.urls import path
from .views import login, logout, order, order_update, order_delete, price, report_park, report_enemy, report_all

urlpatterns = [
    path('user/login/', login, name='login'),
    path('user/logout/', logout, name='logout'),
    path('wash/', order, name='order'),
    path('wash/<int:wash_id>', order_update, name='order_update'),
    path('wash/wash_delete/<int:wash_id>', order_delete, name='order_delete'),
    path('wash/price', price, name='price'),
    path('wash/report_park', report_park, name='report_park'),
    path('wash/report_park/<int:in_year>/<int:in_month>/', report_park, name='report_park'),
    path('wash/report_park/<int:in_year>/<int:in_month>/<int:in_car_id>/', report_park, name='report_park'),
    path('wash/report_enemy', report_enemy, name='report_enemy'),
    path('wash/report_enemy/<int:in_year>/<int:in_month>/', report_enemy, name='report_enemy'),
    path('wash/report_enemy/<int:in_year>/<int:in_month>/<str:car_number>/', report_enemy, name='report_enemy'),
    path('wash/report_all', report_all, name='report_all'),
    path('wash/report_all/<int:in_year>/<int:in_month>/', report_all, name='report_all'),
]
