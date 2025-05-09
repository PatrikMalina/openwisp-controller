from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from openwisp_notifications.signals import notify

from device_manager.models import Device
from script_manager.models import ScriptRecord


# Create your models here.
class LabExerciseDeviceStatus(models.TextChoices):
    APPLIED = 'applied', 'Applied'
    PENDING = 'pending', 'Pending'
    ERROR = 'error', 'Error'


def inform_devices(lab, is_start):
    from device_manager.consumer import DeviceConsumer, DeviceCommands

    device_type = ContentType.objects.get_for_model(Device)

    lab_devices = lab.devices.filter(
        content_type=device_type,
        script__isnull=False,
        lab_exercise_id=lab.pk,
    )

    for lab_device in lab_devices:
        lab_device.configuration_status = LabExerciseDeviceStatus.PENDING
        lab_device.save()

        if lab_device.script is not None:
            with lab_device.script.file.open("r") as f:
                script_content = f.read()
        else:
            script_content = None

        start_message = {
            "command": DeviceCommands.START_LAB,
            "data": {
                "lab_id": lab.pk,
                "script_data": script_content,
            }
        }

        stop_message = {
            "command": DeviceCommands.STOP_LAB,
            "data": {
                "lab_id": lab.pk
            }}

        message = start_message if is_start else stop_message

        DeviceConsumer.send_to_device(lab_device.object_id, message)


class LabExercise(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        PENDING = 'pending', 'Pending'
        ERROR = 'error', 'Error'

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.INACTIVE)
    previous_status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.INACTIVE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if not is_new:
            if self.status != LabExercise.Status.PENDING:
                self.previous_status = self.status

        super().save(*args, **kwargs)

        if self.previous_status in [self.Status.ACTIVE, self.Status.INACTIVE,
                                    self.Status.ERROR] and self.status == self.Status.PENDING:
            is_start = self.previous_status == self.Status.INACTIVE
            inform_devices(self, is_start)

    def handle_device_config_status(self, device_id, success: bool):
        lab_device = self.devices.get(object_id=device_id)

        lab_device.configuration_status = (
            LabExerciseDeviceStatus.APPLIED if success else LabExerciseDeviceStatus.ERROR
        )
        lab_device.save()

        if not success:
            self.status = self.Status.ERROR
            self.save()

            admins = get_user_model().objects.filter(is_superuser=True)
            notify.send(sender=self, type='lab_exercise_error', target=self, recipient=admins)
            return

        self.check_all_applied()

    def check_all_applied(self):
        all_applied = not self.devices.exclude(
            configuration_status=LabExerciseDeviceStatus.APPLIED
        ).exists()

        if all_applied:
            self.status = self.Status.INACTIVE if self.previous_status == self.Status.ACTIVE else self.Status.ACTIVE
            self.save()

            notify_type = 'lab_exercise_started' if self.status == self.Status.ACTIVE else 'lab_exercise_stopped'

            admins = get_user_model().objects.filter(is_superuser=True)

            notify.send(sender=self, type=notify_type, target=self, recipient=admins)


class LabExerciseDevice(models.Model):
    lab_exercise = models.ForeignKey(LabExercise, on_delete=models.CASCADE, related_name='devices')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.TextField()
    device = GenericForeignKey('content_type', 'object_id')
    configuration_template = models.ForeignKey(
        'config.Template',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Only applies to OpenWISP devices"
    )
    script = models.ForeignKey(
        ScriptRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Only applies to Custom devices"
    )
    configuration_status = models.CharField(
        max_length=10,
        choices=LabExerciseDeviceStatus.choices,
        default=LabExerciseDeviceStatus.APPLIED)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.device)
