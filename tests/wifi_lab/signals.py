import os

from django.apps import apps
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from device_manager.models import Device
from file_manager.models import FileRecord
from script_manager.models import ScriptRecord
from wifi_lab.models import LabExerciseDevice, LabExercise

Config = apps.get_model('config', 'Config')
OpenWISPDevice = apps.get_model('config', 'Device')

@receiver(post_delete, sender=ScriptRecord)
def delete_script_file(sender, instance, **kwargs):
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)

@receiver(post_delete, sender=FileRecord)
def delete_upload_file(sender, instance, **kwargs):
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)

@receiver(post_delete, sender=Device)
@receiver(post_delete, sender=OpenWISPDevice)
def delete_lab_device(sender, instance, **kwargs):
    lab_devices = LabExerciseDevice.objects.filter(
        object_id=str(instance.pk)
    )

    if lab_devices.count() > 0:
        for lab_device in lab_devices:
            lab = lab_device.lab_exercise

            if lab.status == LabExercise.Status.PENDING:
                if lab.devices.count() == 1:
                    lab.status = LabExercise.Status.INACTIVE
                    lab.save(update_fields=['status'])

                else:
                    lab.handle_device_config_status(instance.pk, True)

                lab_device.delete()

            else:
                if lab.devices.count() == 1:
                    lab.status = LabExercise.Status.INACTIVE
                    lab.save(update_fields=['status'])

                lab_device.delete()


@receiver(post_save, sender=Config)
def handle_config_applied(sender, instance, created, **kwargs):
    # Skip if just created
    if created:
        return

    previous_status = getattr(instance, '_initial_status', None)

    if previous_status != 'applied' and (instance.status == 'applied' or instance.status == 'error'):
        from wifi_lab.models import LabExerciseDevice, LabExercise

        lab_ids = LabExerciseDevice.objects.filter(
            object_id=instance.device.pk,
            lab_exercise__status__in=[
                LabExercise.Status.PENDING,
                LabExercise.Status.ERROR
            ]
        ).values_list('lab_exercise_id', flat=True).distinct()

        for lab in LabExercise.objects.filter(pk__in=lab_ids):
            lab.handle_device_config_status(device_id=instance.device.pk, success=instance.status == 'applied')
