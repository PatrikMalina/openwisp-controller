from django import forms
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from swapper import load_model

from device_manager.models import Device
from .models import LabExercise, LabExerciseDevice

OpenWISPDevice = load_model("config", "Device")


@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    search_fields = ['model']


class LabExerciseDeviceInlineForm(forms.ModelForm):
    device = forms.ChoiceField(
        required=True,
        label="Device",
    )

    class Meta:
        model = LabExerciseDevice
        exclude = ['lab_exercise', 'content_type', 'object_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        custom_devices = Device.objects.all()
        openwisp_devices = OpenWISPDevice.objects.all()

        custom = [
            (f"custom_{device.id}", f"{device.mac_address} (Custom Device)") for device
            in custom_devices
        ]

        openwisp = [
            (f"openwisp_{device.id}", f"{device.name} (OpenWISP Device)") for device in
            openwisp_devices
        ]

        self.fields['device'].choices = custom + openwisp


class LabExerciseDeviceInline(GenericTabularInline):
    model = LabExerciseDevice
    form = LabExerciseDeviceInlineForm
    extra = 1
    autocomplete_fields = ['content_type']


@admin.register(LabExercise)
class LabExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'description', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['status']

    def has_change_permission(self, request, obj=None):
        if obj and obj.status != 'inactive':
            return False
        return super().has_change_permission(request, obj=obj)

    def get_inlines(self, request, obj=None):
        if obj:
            return [LabExerciseDeviceInline]
        return []
