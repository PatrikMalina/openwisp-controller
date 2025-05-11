import os

from django.db import models


def upload_to(_instance, filename):
    return os.path.join('uploads', filename)


class FileRecord(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "File record"
        verbose_name_plural = "File records"
