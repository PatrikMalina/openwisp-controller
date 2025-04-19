import os

from django.core.exceptions import ValidationError
from django.db import models


# Create your models here.

def upload_to(_instance, filename):
    return os.path.join('scripts', filename)


def validate_sh_file(value):
    ext = os.path.splitext(value.name)[1]
    if ext.lower() != '.sh':
        raise ValidationError('Only .sh files are allowed.')


class ScriptRecord(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=upload_to, validators=[validate_sh_file])

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Script record"
        verbose_name_plural = "Script records"
