# Generated by Django 4.2.20 on 2025-03-19 07:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("device_manager", "0002_device_organization"),
    ]

    operations = [
        migrations.AddField(
            model_name="device",
            name="name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="device",
            name="mac_address",
            field=models.CharField(
                max_length=17,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="MAC address must be in the format XX:XX:XX:XX:XX:XX (hexadecimal).",
                        regex="^[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}$",
                    )
                ],
            ),
        ),
    ]
