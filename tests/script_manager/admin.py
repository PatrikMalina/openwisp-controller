from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import ScriptRecord

@admin.register(ScriptRecord)
class FileRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'file_button')
    search_fields = ('name', 'description')
    readonly_fields = ('validation_notice',)

    def validation_notice(self, _obj):
        return mark_safe(
            '<div style="padding: 10px; background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; border-radius: 4px;">'
            '<strong>Note:</strong> We do not validate <b>.sh</b> files. Please upload valid files only.'
            '</div>'
        )

    validation_notice.short_description = "Notice"

    def file_button(self, obj):
        if obj.file:
            return format_html(
                '<a class="button" href="{}" download style="padding: 4px 8px; background-color: #5cb85c; color: white; text-decoration: none; border-radius: 4px;">Download</a>',
                obj.file.url
            )
        return 'No file'
    file_button.short_description = 'File'