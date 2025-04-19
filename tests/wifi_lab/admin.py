from django import forms
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin import TabularInline
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction, OperationalError
from django.utils.translation import ngettext
from swapper import load_model

from device_manager.models import Device
from script_manager.models import ScriptRecord
from .models import LabExercise, LabExerciseDevice, LabExerciseDeviceStatus

OpenWISPDevice = load_model('config', 'Device')
Config = load_model('config', 'Config')
Template = load_model('config', 'Template')


@admin.action(description='Start selected labs')
def start_lab(modeladmin, request, queryset):
    updated = queryset.count()
    openwisp_type = ContentType.objects.get_for_model(OpenWISPDevice)

    try:
        with transaction.atomic():
            for lab in queryset:
                lab.status = LabExercise.Status.PENDING
                lab.save(update_fields=['status'])

                lab_devices = lab.devices.filter(
                    content_type=openwisp_type,
                    configuration_template__isnull=False
                )

                lab_devices.update(configuration_status=LabExerciseDeviceStatus.PENDING)

                for lab_device in lab_devices:
                    device = lab_device.device
                    template = lab_device.configuration_template

                    config, created = Config.objects.get_or_create(device=device)

                    config.templates.add(template)
                    lab_device.configuration_status = LabExerciseDeviceStatus.PENDING
                    lab_device.save()

        modeladmin.message_user(
            request,
            ngettext(
                '%d lab is starting.',
                '%d labs are starting.',
                updated,
            ) % updated,
            messages.SUCCESS
        )

    except OperationalError:
        modeladmin.message_user(
            request,
            "Database is locked. Please try again later.",
            messages.ERROR
        )


@admin.action(description='Stop selected labs')
def stop_lab(modeladmin, request, queryset):
    updated = queryset.update(status=LabExercise.Status.INACTIVE)

    for lab in queryset:
        for lab_device in lab.devices.all():
            if lab_device.content_type.model_class() == OpenWISPDevice and lab_device.configuration_template:
                device = lab_device.device
                template = lab_device.configuration_template

                try:
                    config = Config.objects.get(device=device)
                    config.templates.remove(template)
                except Config.DoesNotExist:
                    pass  # If no config exists, just skip

    modeladmin.message_user(
        request,
        ngettext(
            '%d lab is stopping.',
            '%d labs are stopping.',
            updated,
        ) % updated,
        messages.SUCCESS
    )


@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    search_fields = ['model']


class LabExerciseDeviceInlineForm(forms.ModelForm):
    device_selector = forms.ChoiceField(
        required=True,
        label="Device",
    )

    configuration_selector = forms.ChoiceField(
        required=False,
        label="Configuration",
    )

    class Meta:
        model = LabExerciseDevice
        exclude = ['lab_exercise', 'content_type', 'object_id', 'configuration_template', 'script',
                   'configuration_status']

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
            (f"openwisp_{device.id}", f"{device.name} (OpenWRT Device)")
            for device in openwisp_devices
        ]

        self.fields['device_selector'].choices = [('', '---------')] + custom + openwisp
        self.fields['device_selector'].widget.attrs.update({'class': 'device-selector'})

        script_choices = [
            (f"script_{script.id}", f"{script.name} (Script)") for script in ScriptRecord.objects.all()
        ]
        template_choices = [
            (f"template_{template.id}", f"{template.name} (Template)") for template in Template.objects.all()
        ]
        all_choices = [('', '---------')] + script_choices + template_choices
        self.fields['configuration_selector'].choices = all_choices
        self.fields['configuration_selector'].widget.attrs.update({'class': 'configuration-selector'})

        if self.instance.pk:
            if self.instance.script:
                self.fields['configuration_selector'].initial = f"script_{self.instance.script.id}"
            elif self.instance.configuration_template:
                self.fields['configuration_selector'].initial = f"template_{self.instance.configuration_template.id}"

            model_class = self.instance.content_type.model_class()
            prefix = 'custom' if model_class == Device else 'openwisp'
            self.fields['device_selector'].initial = f"{prefix}_{self.instance.object_id}"

    def save(self, commit=True):
        instance = super().save(commit=False)

        selected_device = self.cleaned_data.get('device_selector')
        selected_config = self.cleaned_data.get('configuration_selector')

        if selected_device:
            kind, id_str = selected_device.split('_')
            model = Device if kind == "custom" else OpenWISPDevice
            obj = model.objects.get(id=id_str)
            content_type = ContentType.objects.get_for_model(model)

            instance.object_id = obj.id
            instance.content_type = content_type

        instance.script = None
        instance.configuration_template = None

        if selected_config:
            kind, id_str = selected_config.split('_')
            if kind == 'script':
                instance.script = ScriptRecord.objects.get(id=id_str)
            elif kind == 'template':
                instance.configuration_template = Template.objects.get(id=id_str)

        return instance

    def clean(self):
        cleaned_data = super().clean()

        selected_device = cleaned_data.get('device_selector')
        selected_config = cleaned_data.get('configuration_selector')

        if not selected_device or not selected_config:
            return cleaned_data

        device_kind, device_id = selected_device.split('_')
        config_kind, config_id = selected_config.split('_')

        if device_kind == 'custom' and config_kind != 'script':
            raise ValidationError("Only scripts are allowed for Custom devices.")
        if device_kind == 'openwisp' and config_kind != 'template':
            raise ValidationError("Only configuration templates are allowed for OpenWRT devices.")

        return cleaned_data


class LabExerciseDeviceInline(TabularInline):
    model = LabExerciseDevice
    form = LabExerciseDeviceInlineForm
    extra = 0
    can_delete = True


class ReadonlyLabExerciseDeviceInline(admin.TabularInline):
    model = LabExerciseDevice
    can_delete = False
    extra = 0
    verbose_name_plural = "Devices in this Lab"

    readonly_fields = ['device_display', 'configuration']
    fields = ['device_display', 'configuration']  # Show only these columns

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def device_display(self, obj):
        return str(obj.device) if obj.device else '-'

    device_display.short_description = "Device"

    def configuration(self, obj):
        if obj.configuration_template:
            return f"{str(obj.configuration_template)} (Template)"
        elif obj.script:
            return f"{str(obj.script)} (Script)"

        return "-"

    configuration.short_description = "Configuration"


@admin.register(LabExercise)
class LabExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'description', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['status']
    actions = [start_lab, stop_lab]

    def has_change_permission(self, request, obj=None):
        if obj and obj.status != LabExercise.Status.INACTIVE:
            return False
        return super().has_change_permission(request, obj=obj)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        if obj.status == LabExercise.Status.INACTIVE:
            return [LabExerciseDeviceInline(self.model, self.admin_site)]
        else:
            return [ReadonlyLabExerciseDeviceInline(self.model, self.admin_site)]

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
