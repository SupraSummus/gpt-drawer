from django_unicorn.components import UnicornView
from django.shortcuts import get_object_or_404

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
                Note,
                id=note_id,
                notebook=self.notebook,
            )
        self.dialog = False
        self.query = ''
        self.parent._note_selected(self.note)

    def _do_search(self):
        self.notes = list(Note.objects.filter(
            notebook=self.notebook,
            title__icontains=self.query,
        )[:10].values('id', 'title'))
