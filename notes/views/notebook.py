from django import forms
from django.http import HttpResponse
from django.template.response import TemplateResponse

from djsfc import Router, get_template_block, parse_template

from ..models import Note
from .common import get_note, get_notebook


router = Router(__name__)
template_str = '''\
{% extends 'base_main.html' %}

{% block title %}{{ notebook.title }}{% endblock %}

{% block main %}
  <h1>{{ notebook.title }}</h1>
  <p>
    <a href="{% url 'notebook-ask-me' notebook.id %}" role="button">Ask me something</a>
    <a href="#" role="button"
      hx-get="{% url ':create_note_form' notebook.id %}"
      hx-target="#notes"
      hx-swap="afterbegin"
    >New note</a>
  </p>
  <div id="notes">
    {% if new_note %}
      {% block new_note %}
        <form
          hx-post="{% url ':create_note' notebook.id %}"
          hx-target="this"
          hx-swap="outerHTML"
        >
          {% csrf_token %}
          {{ form.as_div }}
          <div class="grid">
            <button type="submit">Create note</button>
            <button type="reset" hx-on:click="this.closest('form').remove()">Cancel</button>
          </div>
        </form>
      {% endblock %}
    {% endif %}
    {% for note in notes %}
      {% block note_card %}
        <article
          hx-target="this"
          hx-swap="outerHTML"
          {% if not note.title %}
            hx-get="{% url ':note_card' note.id %}"
            hx-trigger="load delay:2s"
            aria-busy="true"
          {% endif %}
        >
          <h2>{{ note }}</h2>
          <p style="white-space: pre-line;">{{ note.content|truncatechars:200 }}</p>
          <p>
            <a href="{% url 'notes:note:root' note.id %}">
              See more
            </a>
            &ndash;
            <button
              hx-delete="{% url ':delete_note' note.id %}"
              hx-confirm="Are you sure?"
              class="outline secondary"
            >Delete</button>
          </p>
        </article>
      {% endblock %}
    {% endfor %}
  </div>
{% endblock %}
'''
template = parse_template(template_str, router)
new_note_template = get_template_block(template, 'new_note')
note_card_template = get_template_block(template, 'note_card')


@router.route('GET', '<uuid:notebook_id>')
def root(request, notebook_id):
    notebook = get_notebook(request, notebook_id)
    return TemplateResponse(request, template, {
        'notebook': notebook,
        'notes': notebook.notes.all(),
        'new_note': False,
    })


@router.route('GET', '<uuid:notebook_id>/create-note')
def create_note_form(request, notebook_id):
    notebook = get_notebook(request, notebook_id)
    return TemplateResponse(request, new_note_template, {
        'notebook': notebook,
        'form': NoteForm(),
    })


@router.route('POST', '<uuid:notebook_id>/create-note')
def create_note(request, notebook_id):
    notebook = get_notebook(request, notebook_id)
    form = NoteForm(request.POST)
    if form.is_valid():
        form.instance.notebook = notebook
        form.save()
        return TemplateResponse(request, note_card_template, {
            'note': form.instance,
        })
    else:
        return TemplateResponse(request, new_note_template, {
            'notebook': notebook,
            'form': form,
        })


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['content']


@router.route('GET', 'note/<uuid:note_id>')
def note_card(request, note_id):
    note = get_note(request, note_id)
    return TemplateResponse(request, note_card_template, {
        'note': note,
    })


@router.route('DELETE', 'note/<uuid:note_id>')
def delete_note(request, note_id):
    note = get_note(request, note_id)
    note.delete()
    return HttpResponse()
