from django import forms

from .models import Note


class NoteChoiceWidget(forms.widgets.ChoiceWidget):
    template_name = 'widgets/note_select.html'

    def __init__(self, *args, notebook_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.notebook_id = notebook_id

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['notebook_id'] = self.notebook_id
        return context

    def format_value(self, value):
        if value is None:
            return None
        return Note.objects.filter(id=value).first()
