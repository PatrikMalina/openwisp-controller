from django.urls import path

from .views import device_manager, device_detail

app_name = 'device_manager'

urlpatterns = [
    path('', device_manager, name='device_manager'),
    path('device/id=<int:device_id>/', device_detail, name='device_detail'),
]
