from django.apps import AppConfig
from django.urls import reverse
from openwisp_utils.admin_theme.menu import register_menu_group


class DeviceManagerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "device_manager"

    def ready(self):
        register_menu_group(
            position=21,
            config={
                "label": "Custom clients",
                "url": "http://localhost:8000/device_manager",
                "icon": "link-icon",
            },

        )