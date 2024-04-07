from django import forms
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe

from djsfc import Router, get_template_block, parse_template

from ..models import Note
from .common import get_note, get_notebook


router = Router(__name__)
template_str = '''\
<div class="note-select" hx-target="this" hx-swap="innerHTML">
  {% with field_name=widget.name note=widget.value %}

    {% block form_field %}
      <div
        role="group"
        {% if note %}
          hx-get="{% url ':select_dialog' field_name note.id %}"
        {% else %}
          hx-get="{% url ':select_dialog_empty' field_name notebook_id %}"
        {% endif %}
        hx-trigger="click"
        hx-target="next .select-dialog"
      >
        <input type="hidden" name="{{ field_name }}"{% if note %} value="{{ note.id }}"{% endif %}>
        <input type="text" value="{% if note %}{{ note }}{% endif %}" readonly>
        <input type="button" value="Change">
      </div>
    {% endblock %}

    <div class="select-dialog">
      {% if dialog_open %}
        {% block select_dialog %}
          <dialog open style="align-items: stretch;">
            <article>
              <header>
                <button aria-label="Close" rel="prev"
                  {% if note %}
                    hx-get="{% url ':note_selected' field_name note.id %}"
                  {% else %}
                    hx-get="{% url ':note_selected_clear' field_name notebook_id %}"
                  {% endif %}
                ></button>
                <p>
                  <strong>Select a note</strong>
                  &mdash;
                  <a href="#"
                    hx-get="{% url ':note_selected_clear' field_name notebook_id %}"
                  >Clear</a>
                </p>
              </header>
              <form
                hx-trigger="submit"
                hx-get="{% url ':note_search' field_name notebook_id %}"
                hx-target="next .note-search-results"
                hx-swap="innerHTML"
              >
                <input
                  type="search"
                  placeholder="Search"
                  aria-label="Search"
                  name="q"
                  hx-trigger="input changed delay:500ms"
                  onsubmit="return false"
                />
              </form>
              <ul class="note-search-results">
                {% block search_results %}
                  {% for note in notes %}
                    <li>
                      <a
                        href="#"
                        hx-get="{% url ':note_selected' field_name note.id %}"
                      >{{ note }}</a>
                    </li>
                  {% endfor %}
                {% endblock %}
              </ul>
            </article>
          </dialog>
        {% endblock %}
      {% endif %}
    </div>

  {% endwith %}
</div>
'''
template = parse_template(template_str, router)
form_field_template = get_template_block(template, 'form_field')
select_dialog_template = get_template_block(template, 'select_dialog')
search_results_template = get_template_block(template, 'search_results')


@router.route('GET', 'selected/<slug:field_name>/<uuid:note_id>')
def note_selected(request, field_name, note_id):
    note = get_note(request, note_id)
    return TemplateResponse(request, form_field_template, {
        'field_name': field_name,
        'notebook_id': note.notebook_id,
        'note': note,
    })


@router.route('GET', 'selected-clear/<slug:field_name>/<uuid:notebook_id>')
def note_selected_clear(request, field_name, notebook_id):
    notebook = get_notebook(request, notebook_id)
    return TemplateResponse(request, form_field_template, {
        'field_name': field_name,
        'notebook_id': notebook.id,
    })


@router.route('GET', 'dialog/<slug:field_name>/<uuid:note_id>')
def select_dialog(request, field_name, note_id):
    note = get_note(request, note_id)
    return TemplateResponse(request, select_dialog_template, {
        'field_name': field_name,
        'notebook_id': note.notebook_id,
        'note': note,
        'dialog_open': True,
        'notes': note.notebook.notes.all()[:10],
    })


@router.route('GET', 'dialog-empty/<slug:field_name>/<uuid:notebook_id>')
def select_dialog_empty(request, field_name, notebook_id):
    notebook = get_notebook(request, notebook_id)
    return TemplateResponse(request, select_dialog_template, {
        'field_name': field_name,
        'notebook_id': notebook.id,
        'note': None,
        'dialog_open': True,
        'notes': notebook.notes.all()[:10],
    })


@router.route('GET', 'search/<slug:field_name>/<uuid:notebook_id>')
def note_search(request, field_name, notebook_id):
    notebook = get_notebook(request, notebook_id)
    query = request.GET.get('q')
    notes = notebook.notes.autocomplete_search(query)[:10]
    return TemplateResponse(request, search_results_template, {
        'field_name': field_name,
        'notebook_id': notebook.id,
        'notes': notes,
    })


class NoteChoiceWidget(forms.widgets.ChoiceWidget):
    template_name = 'notes/views/note_select.html'

    def __init__(self, *args, request, notebook_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.notebook_id = notebook_id

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['notebook_id'] = self.notebook_id
        return context

    def format_value(self, value):
        if value is None:
            return None
        return Note.objects.filter(id=value).first()

    def _render(self, template_name, context, renderer=None):
        if renderer is None:
            renderer = forms.get_default_renderer()
        return mark_safe(renderer.render(template_name, context, request=self.request))
