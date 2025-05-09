from django.contrib import admin
from django.utils.html import format_html

from file_manager.models import FileRecord


# Register your models here.
@admin.register(FileRecord)
class FileRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'uploaded_at', 'file_button')
    search_fields = ('name', 'description')


    def file_button(self, obj):
        if obj.file:
            return format_html(
                '<a class="button" href="{}" download style="padding: 4px 8px; background-color: #5cb85c; color: white; text-decoration: none; border-radius: 4px;">Download</a>',
                obj.file.url
            )
        return 'No file'
    file_button.short_description = 'File'
