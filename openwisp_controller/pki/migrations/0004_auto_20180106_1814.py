# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-06 17:14
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pki', '0003_fill_organization_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ca',
            name='serial_number',
            field=models.CharField(blank=True, help_text='leave blank to determine automatically', max_length=39, null=True, verbose_name='serial number'),
        ),
        migrations.AlterField(
            model_name='cert',
            name='serial_number',
            field=models.CharField(blank=True, help_text='leave blank to determine automatically', max_length=39, null=True, verbose_name='serial number'),
        ),
    ]
