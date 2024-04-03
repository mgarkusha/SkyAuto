from django.urls import path
from .views import login, logout, gibdd, gibdd_cu, gibdd_delete, gibdd_update, company_penalty_cu, \
    company_penalty_update, company_penalty, company_penalty_delete, gibdd_company_stat, find_incident_number

urlpatterns = [
    path('user/login/', login, name='login'),
    path('user/logout/', logout, name='logout'),
    path('gibdd/', gibdd, name='gibdd'),
    path('company_penalty/', company_penalty, name='company_penalty'),
    path('gibdd/gibdd_delete/<int:gibdd_id>', gibdd_delete, name='gibdd_delete'),
    path('gibdd_cu/', gibdd_cu, name='gibdd_cu'),
    path('gibdd_cu/<int:year>/<int:month>/<int:day>/<int:hour>/<int:minute>/', gibdd_cu, name='gibdd_cu'),
    path('gibdd/<int:gibdd_id>/', gibdd_update, name='gibdd_update'),
    path('company_penalty_cu/', company_penalty_cu, name='company_penalty_cu'),
    path('company_penalty_cu/<int:year>/<int:month>/<int:day>/<int:hour>/<int:minute>/<int:second>', company_penalty_cu,
         name='company_penalty_cu'),
    path('company_penalty_cu/<int:company_penalty_id>/', company_penalty_update, name='company_penalty_update'),
    path('company_penalty_cu/company_penalty_delete/<int:company_penalty_id>', company_penalty_delete,
         name='company_penalty_delete'),
    path('gibdd_company_stat/', gibdd_company_stat, name='gibdd_company_stat'),
    path('gibdd_company_stat/<int:in_driver_id>', gibdd_company_stat, name='gibdd_company_stat'),
    path('find_incident_number/<int:incident_number_in>', find_incident_number, name='find_incident_number'),
]
