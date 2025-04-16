from django import forms
from django.contrib import admin
from django.contrib.admin import TabularInline
from django.contrib.contenttypes.models import ContentType
from swapper import load_model

from device_manager.models import Device
from .models import LabExercise, LabExerciseDevice

OpenWISPDevice = load_model("config", "Device")


@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    search_fields = ['model']


class LabExerciseDeviceInlineForm(forms.ModelForm):
    device_selector = forms.ChoiceField(
        required=True,
        label="Device",
    )

    class Meta:
        model = LabExerciseDevice
        exclude = ['lab_exercise', 'content_type', 'object_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        lab_exercise = self.initial.get('lab_exercise') or getattr(self.instance, 'lab_exercise', None)

        used_custom_ids = []
        used_openwisp_ids = []

        if lab_exercise and lab_exercise.pk:
            used_devices = LabExerciseDevice.objects.filter(lab_exercise=lab_exercise)

            for device in used_devices:
                if self.instance and self.instance.pk and device.pk == self.instance.pk:
                    continue

                model = device.content_type.model_class()
                if model == Device:
                    used_custom_ids.append(str(device.object_id))
                elif model == OpenWISPDevice:
                    used_openwisp_ids.append(str(device.object_id))

        custom_devices = Device.objects.exclude(id__in=used_custom_ids)
        openwisp_devices = OpenWISPDevice.objects.exclude(id__in=used_openwisp_ids)

        custom = [
            (f"custom_{device.id}", f"{device.name} (Custom Device)")
            for device in custom_devices
        ]

        openwisp = [
            (f"openwisp_{device.id}", f"{device.name} (OpenWISP Device)")
            for device in openwisp_devices
        ]

        self.fields['device_selector'].choices = [('', '---------')] + custom + openwisp

        if self.instance and self.instance.pk and self.instance.device:
            model_class = self.instance.content_type.model_class()
            prefix = 'custom' if model_class == Device else 'openwisp'

            self.fields['device_selector'].initial = f"{prefix}_{self.instance.object_id}"

        self.fields['device_selector'].widget.attrs.update({
            'class': 'device-selector',
        })

    def save(self, commit=True):
        instance = super().save(commit=False)
        selected = self.cleaned_data.get('device_selector')

        if selected:
            kind, id_str = selected.split('_')
            model = Device if kind == "custom" else OpenWISPDevice
            obj = model.objects.get(id=id_str)
            content_type = ContentType.objects.get_for_model(model)

            instance.object_id = obj.id
            instance.content_type = content_type

        return instance


class LabExerciseDeviceInline(TabularInline):
    model = LabExerciseDevice
    form = LabExerciseDeviceInlineForm
    extra = 0
    can_delete = True


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

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            instance.lab_exercise = form.instance
            instance.save()

        for obj in formset.deleted_objects:
            obj.delete()

        formset.save_m2m()

    class Media:
        css = {
            'all': ('css/admin-fixes.css',)
        }
        js = ('js/admin-device-filter.js',)
