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
        base_fields = ['name', 'mac_address', 'device_key', 'organization']
        if not obj:
            return ['setup_note'] + base_fields
        return ['id'] + base_fields

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['id']
        return ['setup_note']

    def status(self, obj):
        return mark_safe('<span style="color: red; font-weight: bold;">Disconnected</span>')

    status.short_description = "Status"

    def setup_note(self, _obj=None):
        return mark_safe(
            '''
            <div style="padding: 12px; background-color: #e9f7ef; color: #1e4620; border: 1px solid #c3e6cb; border-radius: 4px;">
                <strong>Raspberry Pi Device Setup Instructions:</strong><br><br>
                1. Download the image file: <a href="/media/raspberry_backup.img.gz" target="_blank">/media/raspberry_backup.img.gz</a><br>
                2. Flash it to a Raspberry Pi using your preferred tool <code>user: dp</code> and <code>password: dp2023</code><br>
                3. On the Pi, open <code>rpi-client/settings.py</code><br>
                4. Set the <code>URL</code> of OpenWISP server and <code>SHARED_SECRET</code> from the Organization<br>
                5. To reload the new values type command <code>systemctl daemon-reload</code><br>
                6. Restart the service with: <code>sudo systemctl restart rpi-client.service</code><br>
            </div>
            '''
        )