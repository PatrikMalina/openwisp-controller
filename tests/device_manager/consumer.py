import base64
import json
import urllib.parse
from enum import Enum

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from openwisp_notifications.signals import notify

from device_manager.models import Device
from file_manager.models import FileRecord
from wifi_lab.models import LabExercise, LabExerciseDevice, LabExerciseDeviceStatus

connected_devices_cache = set()

WEB_GROUP = 'webclient'


# Frontend side websocket
class WebclientConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def connect(self):
        self.user = self.scope["user"]

        if self.user.is_authenticated:
            self.accept()
            async_to_sync(get_channel_layer().group_add)(WEB_GROUP, self.channel_name)

            self.send_connected_devices()
        else:
            self.close()

    def disconnect(self, close_code):
        async_to_sync(get_channel_layer().group_discard)(WEB_GROUP, self.channel_name)

        self.close()

    def receive(self, text_data=None, bytes_data=None):
        try:
            message = json.loads(text_data)
            command = message.get("command")
            data = message.get("data")


            if command == DeviceCommands.SCRIPT_LOG:
                message = {
                    "command": DeviceCommands.SCRIPT_LOG,
                }

                DeviceConsumer.send_to_device(data, message)

            else:
                print(f"Received command: {command}")

        except json.JSONDecodeError:
            print("Failed to decode JSON message.")

    def send_message(self, event):
        self.send(text_data=json.dumps(event["message"]))

    @staticmethod
    def send_connected_devices():
        connected_devices = [
            {"id": device, "status": DeviceStatus.CONNECTED}
            for device in list(connected_devices_cache)
        ]

        WebclientConsumer.send_to_web({"command": DeviceCommands.CONNECTED_DEVICES, "data": connected_devices})

    # Send message to all web clients
    @staticmethod
    def send_to_web(message):
        async_to_sync(get_channel_layer().group_send)(
            WEB_GROUP,
            {
                "type": "send_message",
                "message": message
            }
        )


class DeviceStatus(str, Enum):
    CONNECTED = 'connected'
    DISCONNECTED = 'disconnected'


# Valid commands for websockets
class DeviceCommands(str, Enum):
    CONNECTED_DEVICES = 'connected_devices'
    STATUS = 'status'
    METRICS = 'metrics'  # Metrics of device like CPU, GPU usage and similar
    CONFIG_STATUS = 'config_status'  # Status of device configuration e.g. if it started the script and so on
    NEW_DEVICE = 'new_device'

    START_LAB = 'start_lab'
    STOP_LAB = 'stop_lab'
    SCRIPT_LOG = 'script_log'
    FILE_UPLOAD = 'file_upload'


# Device side websocket
class DeviceConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.device_id = None
        self.device_key = None

        self.device_group_name = None

    def connect(self):
        query_string = self.scope['query_string'].decode()
        query_params = urllib.parse.parse_qs(query_string)

        self.device_id = query_params.get('id', [None])[-1]
        self.device_key = query_params.get('key', [None])[-1]

        if not self.authenticate_device():
            self.disconnect(301)
            return

        self.accept()

        # Each device to different group for easier commands sending
        self.device_group_name = f"device_{self.device_id}"

        async_to_sync(get_channel_layer().group_add)(self.device_group_name, self.channel_name)
        connected_devices_cache.add(self.device_id)

        self.send_status_to_web(DeviceStatus.CONNECTED)

        # If reconnect happens to not get stuck on pending or error
        lab_devices = LabExerciseDevice.objects.filter(object_id=self.device_id).exclude(
            configuration_status=LabExerciseDeviceStatus.APPLIED
        )

        for lab_device in lab_devices:
            lab = lab_device.lab_exercise
            lab.handle_device_config_status(self.device_id, True)

    def disconnect(self, close_code):
        async_to_sync(get_channel_layer().group_discard)(self.device_group_name, self.channel_name)

        self.send_status_to_web(DeviceStatus.DISCONNECTED)

        if self.device_id in connected_devices_cache:
            connected_devices_cache.remove(self.device_id)

        self.close()

    def receive(self, text_data=None, bytes_data=None):
        try:
            message = json.loads(text_data)
            command = message.get("command")
            data = message.get("data")

            if command == DeviceCommands.METRICS:
                self.send_metrics_to_web(data)
                return

            elif command == DeviceCommands.CONFIG_STATUS:
                self.update_config_status(data)

            elif command == DeviceCommands.SCRIPT_LOG:
                self.send_log_to_web(data)

            elif command == DeviceCommands.FILE_UPLOAD:
                self.save_file_record(data)

            else:
                print(f"Received command: {command}")

        except json.JSONDecodeError:
            print("Failed to decode JSON message.")

    def save_file_record(self, data):
        lab_id = data.get('lab_id', None)
        filename = data.get('filename', None)
        content = data.get('content', None)

        if content:
            content = base64.b64decode(content)

            content_file = ContentFile(content, name=filename)

            device = Device.objects.get(id=self.device_id)
            lab = LabExercise.objects.get(id=lab_id)

            des = f"File uploaded by device \"{device.name}\" for laboratory exercise \"{lab.name}\". "

            if lab.description:
                des += f"Laboratory description \"{lab.description}\"."

            file_record = FileRecord.objects.create(
                name=filename,
                description=des,
                file=content_file
            )

            admins = get_user_model().objects.filter(is_superuser=True)

            notify.send(sender=file_record, type="new_file_uploaded", target=file_record, recipient=admins, lab=lab.name)

    def send_metrics_to_web(self, data):
        data["id"] = self.device_id
        message = {"command": DeviceCommands.METRICS, "data": data}

        WebclientConsumer.send_to_web(message)

    def send_status_to_web(self, status):
        message = {"command": DeviceCommands.STATUS, "data": {
            "id": self.device_id,
            "status": status
        }}

        WebclientConsumer.send_to_web(message)

    def send_log_to_web(self, data):
        message = {"command": DeviceCommands.SCRIPT_LOG, "data": data, "id": self.device_id}

        WebclientConsumer.send_to_web(message)

    def update_config_status(self, data):
        success = data.get('success', False)
        lab_id = data.get('lab_id', None)

        if lab_id:
            lab = LabExercise.objects.get(id=lab_id)
            lab.handle_device_config_status(self.device_id, success)

    def authenticate_device(self):
        try:
            device = Device.objects.get(id=self.device_id)
            return device.device_key == self.device_key

        except Device.DoesNotExist:
            return False

    # Send message to specific device
    @staticmethod
    def send_to_device(device_id, message):
        async_to_sync(get_channel_layer().group_send)(
            f"device_{device_id}",
            {
                "type": "send_message",
                "message": message,
            }
        )

    def send_message(self, event):
        self.send(text_data=json.dumps(event["message"]))
