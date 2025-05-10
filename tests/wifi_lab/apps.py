from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from openwisp_utils.admin_theme.menu import register_menu_group


def register_laboratory_menu():
    register_menu_group(
        position=22,
        config={
            'label': _('Laboratory'),
            'name': 'laboratory',
            'icon': 'icon-laboratory',
            'items': {
                1: {
                    'label': _('Laboratory Exercises'),  # Label displayed in the menu
                    'url': '/admin/wifi_lab/labexercise/',  # URL to the admin changelist page
                    'name': 'labexercise',  # A unique identifier for this menu item
                    'icon': 'icon-lab-exercise',
                },
                2: {
                    'label': _('Scripts'),
                    'url': '/admin/script_manager/scriptrecord/',
                    'name': 'scriptrecord',
                    'icon': 'icon-script',
                },
                3: {
                    'label': _('Custom Clients'),
                    'url': '/admin/device_manager/device/',
                    'name': 'customdevice',
                    'icon': 'icon-custom-device',
                },
                4:{
                    'label': _('File Uploads'),
                    'url': '/admin/file_manager/filerecord/',
                    'name': 'filerecord',
                    'icon': 'ow-template',
                }
            }
        }
    )


def register_notification_types():
    from device_manager.models import Device
    from wifi_lab.models import LabExercise
    from openwisp_notifications.types import register_notification_type

    register_notification_type(
        'custom_device_registered',
        {
            'verbose_name': _('Custom Device Registration'),
            'verb': _('custom device registered successfully'),
            'level': 'success',
            'email_subject': _(
                '[{site.name}] SUCCESS: "{notification.target}"'
                ' {notification.verb}'
            ),
            'email_notification': False,
            'message': _(
                'A new custom device [{notification.target}]'
                '({notification.target_link}) has registered successfully.'
            ),
        },
        models=[Device],
    )

    register_notification_type(
        'lab_exercise_started',
        {
            'verbose_name': _('Laboratory Exercise Started'),
            'verb': _('laboratory exercise started successfully'),
            'level': 'success',
            'email_subject': _(
                '[{site.name}] SUCCESS: "{notification.target}"'
                ' {notification.verb}'
            ),
            'email_notification': False,
            'message': _(
                'A laboratory [{notification.target}]'
                '({notification.target_link}) has started successfully.'
            ),
        },
        models=[LabExercise],
    )

    register_notification_type(
        'lab_exercise_stopped',
        {
            'verbose_name': _('Laboratory Exercise Stopped'),
            'verb': _('laboratory exercise stopped successfully'),
            'level': 'success',
            'email_subject': _(
                '[{site.name}] SUCCESS: "{notification.target}"'
                ' {notification.verb}'
            ),
            'email_notification': False,
            'message': _(
                'A laboratory [{notification.target}]'
                '({notification.target_link}) has stopped successfully.'
            ),
        },
        models=[LabExercise],
    )

    register_notification_type(
        'lab_exercise_error',
        {
            'verbose_name': _('Laboratory Exercise Error'),
            'verb': _('laboratory exercise error'),
            'level': 'success',
            'email_subject': _(
                '[{site.name}] SUCCESS: "{notification.target}"'
                ' {notification.verb}'
            ),
            'email_notification': False,
            'message': _(
                'A laboratory [{notification.target}]'
                '({notification.target_link}) has error on one or more devices.'
            ),
        },
        models=[LabExercise],
    )


class WifiLabConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wifi_lab"

    def ready(self):
        register_laboratory_menu()
        register_notification_types()

        import wifi_lab.signals # noqa: F401
