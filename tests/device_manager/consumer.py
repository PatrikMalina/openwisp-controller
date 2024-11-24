import json

from channels.generic.websocket import WebsocketConsumer

from device_manager.models import Device
import urllib.parse


class DeviceConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.device_id = None
        self.device_key = None

    def connect(self):
        query_string = self.scope['query_string'].decode()
        query_params = urllib.parse.parse_qs(query_string)

        self.device_id = query_params.get('id', [None])[0]
        self.device_key = query_params.get('key', [None])[0]


        is_authenticated = self.authenticate_device()

        if not self.device_id or not self.device_key or not is_authenticated:
            self.disconnect(301)
        else:
            self.accept()

    def authenticate_device(self):
        try:
            device = Device.objects.get(id=self.device_id)
            return device.device_key == self.device_key
        except Device.DoesNotExist:
            return False

    def disconnect(self, close_code):
        self.close()

    def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')
        if command:
            # Process the command
            response = {"status": "received", "command": command}
            self.send(text_data=json.dumps(response))

    def send_command(self, command):
        self.send(text_data=json.dumps({"command": command}))
