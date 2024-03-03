from django.shortcuts import get_object_or_404
from django_unicorn.components import UnicornView

from ..models import Note


class NoteSelectView(UnicornView):
    notebook = None
    note = None
    dialog = False
    query = ''
    notes = []

    class Meta:
        javascript_exclude = (
            'notebook',
            'note',
        )

    def mount(self):
        self.notebook = self.component_kwargs['notebook']
        self.note = self.component_kwargs['note']

    def updated_dialog(self, dialog):
        if dialog:
            self._do_search()
            self.call('focus_search')

    def updated_query(self, query):
        self._do_search()

    def select_note(self, note_id):
        if note_id is None:
            self.note = None
        else:
            self.note = get_object_or_404(
                self._get_queryset(),
                id=note_id,
            )
        self.dialog = False
        self.query = ''
        self.parent._note_selected(self.note)

    def _do_search(self):
        self.notes = list(self._get_queryset().filter(
            title__icontains=self.query,
        )[:10].values('id', 'title'))

    def _get_queryset(self):
        return Note.objects.filter(
            notebook=self.notebook,
        )
