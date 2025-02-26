import json
import urllib.parse

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer

from device_manager.models import Device

connected_devices_cache = set()


def broadcast_message(data):
    async_to_sync(get_channel_layer().group_send)(
        "connected_devices",
        {
            "type": "send_message",
            "message": data
        }
    )


def get_connected_devices():
    return [
        {"id": device, "status": "connected"}
        for device in list(connected_devices_cache)
    ]


def send_current_devices_status():
    connected_devices = get_connected_devices()

    broadcast_message({"command": "connected_devices", "data": connected_devices})


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

            # Send list of currently connected devices
            send_current_devices_status()

        else:
            is_authenticated = self.authenticate_device()

            if not self.device_id or not self.device_key or not is_authenticated:
                self.disconnect(301)
            else:
                self.accept()
                async_to_sync(get_channel_layer().group_add)("connected_devices", self.channel_name)
                connected_devices_cache.add(self.device_id)

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

        if self.device_id in connected_devices_cache:
            connected_devices_cache.remove(self.device_id)

        self.close()

    def receive(self, text_data):
        try:
            message = json.loads(text_data)

            if message.get("type") == "broadcast":
                broadcast_message(message)

            elif message.get("command") == "device_info":
                self.send_current_device_metrics(message.get("data"))

            else:
                print("Received command: ", message.get("command"))

        except json.JSONDecodeError:
            print("Failed to decode JSON message.")

    def send_current_device_metrics(self, data):
        data["id"] = self.device_id

        broadcast_message({"command": "device_metrics", "data": data})

    def notify_device_status(self, status):
        device_info = {
            "id": self.device_id,
            "status": status
        }

        broadcast_message({"command": "status", "data": device_info})

    # Handle messages in the WebSocket group
    def send_message(self, event):
        self.send(text_data=json.dumps(event["message"]))
