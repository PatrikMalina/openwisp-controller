import json

from channels.generic.websocket import WebsocketConsumer

from device_manager.models import Device


class DeviceConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.device_id = None
        self.device_key = None

    def connect(self):
        self.accept()
        self.device_id = self.scope['query_string'].decode().split("id=")[1].split("&")[0]
        self.device_key = self.scope['query_string'].decode().split("key=")[1]

        # Verify the device ID and key
        if not self.authenticate_device(self.device_id, self.device_key):
            # Close connection if authentication fails
            print('close')
            self.close()
        else:
            self.accept()

    def authenticate_device(self, device_id, device_key):
        try:
            device = Device.objects.get(id=device_id)
            return device.device_key == device_key
        except Device.DoesNotExist:
            return False

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')
        if command:
            # Process the command
            response = {"status": "received", "command": command}
            self.send(text_data=json.dumps(response))

    def send_command(self, command):
        self.send(text_data=json.dumps({"command": command}))
