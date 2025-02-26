from django.core.validators import RegexValidator
from django.db import models


# Create your models here.

class Device(models.Model):
    MAC_ADDRESS_REGEX = r'^[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}$'  # Enforce format XX:XX:XX:XX:XX:XX

    name = models.CharField(max_length=255, blank=True, null=True)
    mac_address = models.CharField(
        max_length=17,
        unique=True,
        validators=[RegexValidator(
            regex=MAC_ADDRESS_REGEX,
            message="MAC address must be in the format XX:XX:XX:XX:XX:XX (hexadecimal)."
        )]
    )
    device_key = models.CharField(max_length=32)
    organization = models.ForeignKey(
        'openwisp_users.Organization',  # String reference to the related model
        on_delete=models.CASCADE,
        related_name='custom_devices',
        null=True
    )

    def save(self, *args, **kwargs):
        if not self.name:  # If name is empty, set it to mac_address
            self.name = self.mac_address
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or self.mac_address
