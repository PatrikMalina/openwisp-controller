from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from openwisp_utils.admin_theme.menu import register_menu_group


def register_laboratory_menu():
    register_menu_group(
        position=22,
        config={
            'label': _('Laboratory'),
            'name': 'laboratory',
            'icon': 'ow-device',
            'items': {
                1: {
                    'label': _('Lab Exercises'),  # Label displayed in the menu
                    'url': '/admin/wifi_lab/labexercise/',  # URL to the admin changelist page
                    'name': 'labexercise',  # A unique identifier for this menu item
                    'icon': 'ow-device',  # Optional icon class (from OpenWISP themes)
                },
                2: {
                    'label': _('Scripts'),
                    'url': '/admin/script_manager/scriptrecord/',
                    'name': 'scriptrecord',
                    'icon': 'ow-template',
                },
                3: {
                    'label': _('Custom clients'),
                    'url': '/admin/device_manager/device',
                    'name': 'customdevice',
                    'icon': 'ow-device',
                }
            }
        }
    )


class WifiLabConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wifi_lab"

    def ready(self):
        register_laboratory_menu()
