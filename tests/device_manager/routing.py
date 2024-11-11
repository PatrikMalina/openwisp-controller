from django.urls import re_path

from .consumer import DeviceConsumer

websocket_urlpatterns = [
    re_path(r"ws/device/?$", DeviceConsumer.as_asgi()),
]
