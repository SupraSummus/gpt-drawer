from django_unicorn.components import UnicornView


class NoteView(UnicornView):
    note = None

    class Meta:
        javascript_exclude = ('note',)

    def mount(self):
        self.note = self.component_kwargs['note']

    def _text_updated(self, text):
        self.note.content = text
        self.note.save(update_fields=['content'])
