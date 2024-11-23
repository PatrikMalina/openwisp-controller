from django.contrib import admin

from device_manager.models import Device


# Register your models here.
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['mac_address', 'device_key', 'organization']
    search_fields = ['mac_address', 'device_key']
