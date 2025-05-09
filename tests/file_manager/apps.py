from django.apps import AppConfig
from openwisp_notifications.types import register_notification_type
from django.utils.translation import gettext_lazy as _

class FileRecord(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "file_manager"

    def ready(self):
        from file_manager.models import FileRecord

        register_notification_type(
            'new_file_uploaded',
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
                    'A new file [{notification.target}]'
                    '({notification.target_link}) has been uploaded from laboratory \"{lab}\".'
                ),
            },
            models=[FileRecord],
        )
