from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from device_manager.models import Device
from script_manager.models import ScriptRecord


# Create your models here.
class LabExerciseDeviceStatus(models.TextChoices):
    APPLIED = 'applied', 'Applied'
    PENDING = 'pending', 'Pending'
    ERROR = 'error', 'Error'

def start_lab(lab):
    from device_manager.consumer import send_to_specific_device

    device_type = ContentType.objects.get_for_model(Device)

    lab_devices = lab.devices.filter(
        content_type=device_type,
        script__isnull=False,
        lab_exercise_id=lab.pk,
    )

    for lab_device in lab_devices:
        lab_device.configuration_status = LabExerciseDeviceStatus.PENDING
        lab_device.save()

        message = {
            "command": "start_lab",
            "data": {
                "lab_id": lab.pk,
                "script_data": "test"
            }}

        send_to_specific_device(lab_device.object_id, message)


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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        previous_status = None

        if not is_new:
            previous = LabExercise.objects.get(pk=self.pk)
            previous_status = previous.status

        super().save(*args, **kwargs)

        if previous_status == self.Status.INACTIVE and self.status == self.Status.PENDING:
            start_lab(self)


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
