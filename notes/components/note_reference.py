from django_unicorn.components import UnicornView


class NoteReferenceView(UnicornView):
    notebook = None
    note_reference = None

    class Meta:
        javascript_exclude = (
            'notebook',
            'note_reference',
        )

    def mount(self):
        self.notebook = self.component_kwargs['notebook']
        self.note_reference = self.component_kwargs['note_reference']

    def _note_selected(self, note):
        self.note_reference.target_note = note
        self.note_reference.save(update_fields=['target_note'])

    def _text_updated(self, text):
        self.note_reference.question = text
        self.note_reference.save(update_fields=['question'])
