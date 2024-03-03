from urllib.parse import urlparse

from django.contrib import admin
from django.urls import resolve

from admin_utils import get_autocomplete_object_id

from .models import Alias, Note, Notebook, NotebookUserPermission, Reference


class NotebookUserPermissionInline(admin.TabularInline):
    model = NotebookUserPermission
    extra = 0


@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    list_display = ('title', 'id')
    search_fields = ('title', 'id')
    inlines = (NotebookUserPermissionInline,)


class ReferenceInline(admin.TabularInline):
    model = Reference
    fk_name = 'note'
    extra = 0
    fields = ('state', 'question', 'target_note')
    readonly_fields = ('state',)
    autocomplete_fields = ('target_note',)


class AliasInline(admin.TabularInline):
    model = Alias
    extra = 0


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'notebook', 'id')
    search_fields = ('title', 'id')
    list_filter = ('notebook',)

    inlines = (AliasInline, ReferenceInline)

    def get_search_results(self, request, queryset, search_term):
        if note_id := get_autocomplete_object_id(request, Reference, 'target_note'):
            queryset = Note.objects.filter(notebook__notes__id=note_id)
        return super().get_search_results(request, queryset, search_term)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)

        referer = request.META.get('HTTP_REFERER')
        referer_path = urlparse(referer).path
        referer_match = resolve(referer_path)

        # get the note id this was created from
        if referer_match.view_name == 'admin:notes_note_change':
            object_id = referer_match.kwargs.get('object_id')
            note = Note.objects.get(id=object_id)
            initial['notebook'] = note.notebook_id

        return initial
