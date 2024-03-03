from django_unicorn.components import UnicornView


class EditableTextView(UnicornView):
    text = ''
    editing = False

    def mount(self):
        self.text = self.component_kwargs.get('text', '')

    def save(self):
        self.editing = False
        self.parent._text_updated(self.text)
