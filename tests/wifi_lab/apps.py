from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from openwisp_utils.admin_theme.menu import register_menu_group


class WifiLabConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wifi_lab"

    def ready(self):
        self.register_menu_groups()

    def register_menu_groups(self):
        register_menu_group(
            position=22,  # Position in the menu order
            config={
                'label': _('Lab Exercises'),  # Label displayed in the menu
                'url': '/admin/wifi_lab/labexercise/',  # URL to the admin changelist page
                'name': 'labexercise',  # A unique identifier for this menu item
                'icon': 'ow-device',  # Optional icon class (from OpenWISP themes)
            },
        )
