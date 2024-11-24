import json
import urllib.parse

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer

from device_manager.models import Device


class DeviceConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.device_id = None
        self.device_key = None

    def connect(self):
        query_string = self.scope['query_string'].decode()
        query_params = urllib.parse.parse_qs(query_string)

        self.device_id = query_params.get('id', [None])[-1]
        self.device_key = query_params.get('key', [None])[-1]

        if self.device_id == '0' and self.device_key == '0':
            self.accept()
            async_to_sync(get_channel_layer().group_add)("connected_devices", self.channel_name)

        else:
            is_authenticated = self.authenticate_device()

            if not self.device_id or not self.device_key or not is_authenticated:
                self.disconnect(301)
            else:
                self.accept()
                async_to_sync(get_channel_layer().group_add)("connected_devices", self.channel_name)

                self.notify_device_status("connected")

    def authenticate_device(self):
        try:
            device = Device.objects.get(id=self.device_id)
            return device.device_key == self.device_key
        except Device.DoesNotExist:
            return False

    def disconnect(self, close_code):
        async_to_sync(get_channel_layer().group_discard)("connected_devices", self.channel_name)

        self.notify_device_status("disconnected")
        self.close()

    def notify_device_status(self, status):
        device_info = {
            "id": self.device_id,
            "status": status
        }

        # Send the update to the WebSocket group
        async_to_sync(get_channel_layer().group_send)(
            "connected_devices",
            {
                "type": "device_status_update",
                "message": {"command": "status", "data": device_info}
            }
        )

    # Handle messages in the WebSocket group
    def device_status_update(self, event):
        self.send(text_data=json.dumps(event["message"]))
