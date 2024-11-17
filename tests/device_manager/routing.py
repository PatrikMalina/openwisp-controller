from django.urls import path

from . import consumer

websocket_urlpatterns = [
    path("ws/device/", consumer.DeviceConsumer.as_asgi()),
]
