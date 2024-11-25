from django.shortcuts import render

from device_manager.models import Device

# Create your views here.

site_title = 'OpenWISP Admin'


def device_manager(request):
    return render(request, 'device_manager/home.html', {'title': 'Connected Devices', 'site_title': site_title})


def device_detail(request, device_id):
    if not device_id:
        return render(request, 'device_manager/device_not_found.html', {
            'message': 'Device ID is missing.',
            'site_title': site_title
        })

    try:
        device = Device.objects.get(id=device_id)
    except Device.DoesNotExist:
        # If the device is not found, render the 'device_not_found' template
        return render(request, 'device_manager/device_not_found.html', {
            'message': f'Device with ID {device_id} does not exist.',
            'site_title': site_title
        })

    return render(request, 'device_manager/device_detail.html', {
        'device': device,
        'title': f"Device {device.id} Details",
        'site_title': site_title
    })
