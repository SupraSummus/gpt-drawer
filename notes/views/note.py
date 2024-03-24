from django import forms
from django.shortcuts import get_object_or_404
from django.template import engines
from django.template.response import TemplateResponse

from djsfc import Router, get_template_block

from ..models import Note


router = Router()


template_str = '''\
{% extends 'base.html' %}

{% block title %}{{ note }}{% endblock %}

{% block content %}
  <main class="container">

    <section>
      {% block note %}

        {% if editing %}
          <form hx-post="{% url ':edit_save' note.id %}" hx-target="this" hx-swap="outerHTML">
            {% csrf_token %}
            {{ form.as_div }}
            <div class="grid">
              <button type="submit">Save</button>
              <button type="reset" hx-get="{% url ':read' note.id %}">Cancel</button>
            </div>
          </form>

        {% else %}
          <div hx-target="this" hx-swap="outerHTML">
            <h1>{{ note }}</h1>
            <p style="white-space: pre-line;">{{ note.content }}</p>
            <aside>
              <button
                hx-get="{% url ':edit' note.id %}"
                hx-trigger="click"
                class="outline"
              >Edit</button>
            </aside>
          </div>

        {% endif %}
      {% endblock %}
    </section>

    <section>
      <h2>QA</h2>
      <dl>
        {% for note_reference in note.references.all %}
          {% include 'components/note_reference.html' %}
        {% endfor %}
        <p hx-target="this" hx-swap="beforebegin">
          <button class="outline"
            hx-get="{% url 'note-reference-create' note.id %}"
            hx-trigger="click"
          >Add QA entry</button>
        </p>
      </dl>
    </section>

  </main>
{% endblock %}
'''
template = engines['django'].from_string(template_str)
note_block = get_template_block(template, 'note')


@router.route('GET', '<uuid:note_id>/')
def root(request, note_id):
    note = get_note(request, note_id)
    return TemplateResponse(request, template, {
      'note': note,
      'editing': False,
    })


@router.route('GET', '<uuid:note_id>/edit/')
def edit(request, note_id):
    note = get_note(request, note_id)
    form = NoteForm(instance=note)
    return TemplateResponse(request, note_block, {
      'note': note,
      'editing': True,
      'form': form,
    })


@router.route('POST', '<uuid:note_id>/edit/')
def edit_save(request, note_id):
    note = get_note(request, note_id)
    form = NoteForm(request.POST, instance=note)
    if form.is_valid():
        form.save()
        return TemplateResponse(request, note_block, {
          'note': note,
          'editing': False,
        })
    else:
        return TemplateResponse(request, note_block, {
          'note': note,
          'editing': True,
          'form': form,
        })


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ('title', 'content')


@router.route('GET', '<uuid:note_id>/read/')
def read(request, note_id):
    note = get_note(request, note_id)
    return TemplateResponse(request, note_block, {
      'note': note,
      'editing': False,
    })


def get_note(request, note_id):
    return get_object_or_404(
        Note.objects.accessible_by_user(request.user),
        id=note_id,
    )
