from django.urls import re_path

from .consumer import DeviceConsumer, WebclientConsumer

websocket_urlpatterns = [
    re_path(r"ws/device/?$", DeviceConsumer.as_asgi()),
    re_path(r"ws/webclient/", WebclientConsumer.as_asgi()),
]
