from django.contrib import admin
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from device_manager.models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'mac_address', 'organization', 'status']
    search_fields = ['name', 'mac_address', 'device_key']

    class Media:
        js = (
            static("custom_device_websocket.js"),
            "https://cdn.jsdelivr.net/npm/chart.js",
        )

    def get_fields(self, request, obj=None):
        if obj:
            return ['id', 'name', 'mac_address', 'device_key', 'organization']
        return ['name', 'mac_address', 'device_key', 'organization']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['id']
        return []

    def status(self, obj):
        return mark_safe('<span style="color: red; font-weight: bold;">Disconnected</span>')

    status.short_description = "Status"
