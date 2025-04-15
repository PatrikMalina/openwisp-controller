from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from openwisp_utils.admin_theme.menu import register_menu_group


class DeviceManagerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "device_manager"

    def ready(self):
        self.register_menu_groups()

    def register_menu_groups(self):
        register_menu_group(
            position=21,
            config={
                'label': _('Custom clients'),
                'url': '/admin/device_manager/device',
                'name': 'customdevice',
                'icon': 'ow-device',
            },
        )

        # register_menu_group(
        #     position=23,
        #     config={
        #         'label': _('Custom clients'),
        #         'url': '/device_manager',
        #         'name': 'custom_device',
        #         'icon': 'ow-device',
        #     },
        # )
