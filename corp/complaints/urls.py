from django.conf.urls import url
from django.urls import path
from .views import index, complaint_create, complaint_delete, complaint_update, complaint_archive, complaint_manager, \
    complaint_view_archive, complaint_return, complaint_report, driver_stat, login, logout

urlpatterns = [
    url(r'^user/login/$', login, name='login'),
    url(r'^user/logout/$', logout, name='logout'),
    url(r'^$', index, name='index'),
    path('complaint/<int:in_month>/<int:in_driver_id>', index, name='index'),
    path('complaint/stat/', driver_stat, name='driver_stat'),
    path('complaint/stat/<int:in_driver_id>', driver_stat, name='driver_stat'),
    url(r'^complaint_create/$', complaint_create, name='complaint_create_url'),
    url(r'^complaint_delete/(\d+)/$', complaint_delete, name='complaint_delete'),
    url(r'^complaint_update/(\d+)/$', complaint_update, name='complaint_update'),
    url(r'^complaint_archive/(\d+)/$', complaint_archive, name='complaint_archive'),
    url(r'^complaint_manager/(\d+)/$', complaint_manager, name='complaint_manager_url'),
    url(r'^complaint_view_archive/$', complaint_view_archive, name='complaint_view_archive_url'),
    url(r'^complaint_return/(\d+)/$', complaint_return, name='complaint_return'),
    url(r'^complaint_report/$', complaint_report, name='complaint_report_url'),
]
