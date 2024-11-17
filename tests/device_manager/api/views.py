from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from device_manager.models import Device  # Assuming you have a Device model
from django.http import HttpResponse
import json

@csrf_exempt
def register_device(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        mac_address = data.get('mac_address')
        secret_key = data.get('secret_key')
        print('data')

        # Verify the secret key matches (you may want to use environment variable for security)
        if secret_key != "123":
            return JsonResponse({'error': 'Invalid secret key'}, status=403)

        print('key')
        # Check if device already exists
        device, created = Device.objects.get_or_create(mac_address=mac_address)

        if created:
            device.device_key = get_random_string(32)  # Generate a random key for the device
            device.save()

        return JsonResponse({'id': device.id, 'key': device.device_key})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
