from django.contrib import admin

from .models import ScriptRecord

# Register your models here.
@admin.register(ScriptRecord)
class FileRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'file')
    search_fields = ('name', 'description')