from django.urls import path
from . import views

app_name = 'device_manager'

urlpatterns = [
    path('', views.home, name='home'),
]
