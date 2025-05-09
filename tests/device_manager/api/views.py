import json

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from openwisp_notifications.signals import notify
from swapper import load_model

from device_manager.consumer import WebclientConsumer, DeviceCommands
from device_manager.models import Device

OrganizationConfigSettings = load_model('config', 'OrganizationConfigSettings')


@csrf_exempt
def register_device(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        mac_address = data.get('mac_address')
        secret_key = data.get('secret_key')

        organizations = OrganizationConfigSettings.objects.filter(shared_secret=secret_key)

        # Verify the secret key matches
        if not organizations.exists():
            return JsonResponse({'error': 'Invalid secret key'}, status=403)

        organization_settings = organizations.first()

        if organization_settings.registration_enabled != 1:
            return JsonResponse({'error': 'Registration for this organization is not enabled!'}, status=403)

        # Check if device already exists
        device, created = Device.objects.get_or_create(mac_address=mac_address, defaults={
            'organization_id': organization_settings.organization_id  # Use organization_id here
        })

        if created:
            device.device_key = get_random_string(32)
            device.save()

            message = {
                "command": DeviceCommands.NEW_DEVICE,
                "data": {
                    "id": device.id
                }
            }

            WebclientConsumer.send_to_web(message)

            admins = get_user_model().objects.filter(is_superuser=True)

            notify.send(sender=device, type='custom_device_registered', target=device, recipient=admins)

        return JsonResponse({'id': device.id, 'key': device.device_key})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
