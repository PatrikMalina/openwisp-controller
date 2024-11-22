from django.db import models


# Create your models here.

class Device(models.Model):
    mac_address = models.CharField(max_length=17, unique=True)
    device_key = models.CharField(max_length=32)
    organization = models.ForeignKey(
        'openwisp_users.Organization',  # String reference to the related model
        on_delete=models.CASCADE,
        related_name='custom_devices',
        null=True
    )
