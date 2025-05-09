import os

from django.db import models

def upload_to(_instance, filename):
    return os.path.join('scripts', filename)

class FileRecord(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "File record"
        verbose_name_plural = "File records"