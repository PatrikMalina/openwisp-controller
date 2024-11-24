from django.urls import re_path

from . import consumer

websocket_urlpatterns = [
   re_path(r"ws/device/?$", consumer.DeviceConsumer.as_asgi()),
]
