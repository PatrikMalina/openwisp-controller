from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.hello_view, name='hello_view'),
    path('', views.hello_view, name='hello_view'),
]
