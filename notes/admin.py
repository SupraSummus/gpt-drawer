from django.contrib import admin

from . import models


class NoteBookUserPermissionInline(admin.TabularInline):
    model = models.NotebookUserPermission
    extra = 0


@admin.register(models.Notebook)
class NoteBookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)
    inlines = (NoteBookUserPermissionInline,)
