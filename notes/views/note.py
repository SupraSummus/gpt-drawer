from django import forms
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import engines
from django.template.response import TemplateResponse

from djsfc import Router, get_template_block

from ..models import Note, NoteReference
from ..widgets import NoteChoiceWidget


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
          {% block note_reference %}
            {% if editing %}
              <form hx-post="{% url ':note_reference_save' note_reference.id %}" hx-target="this" hx-swap="outerHTML">
                {% csrf_token %}
                {{ form.as_div }}
                <div class="grid">
                  <button type="submit">Save</button>
                  <button type="reset" hx-get="{% url ':note_reference_read' note_reference.id %}">Cancel</button>
                </div>
              </form>

            {% else %}
              <div hx-target="this" hx-swap="outerHTML">

                <dt>
                  <p style="white-space: pre-line;">{{ note_reference.question }}</p>
                </dt>

                <dd>
                  {% if note_reference.target_note %}
                    <p>
                      <a href="{% url 'notes:note:root' note_reference.target_note.id %}">
                        {{ note_reference.target_note }}
                      </a>
                    </p>
                    <p>{{ note_reference.target_note.content|truncatechars:200 }}</p>
                  {% else %}
                    <p>
                      No answer yet
                      <a
                        role="button"
                        href="{% url 'notes:answer:root' note_reference.id %}"
                        class="outline"
                      >Answer in new note</a>
                    </p>
                  {% endif %}

                </dd>

                <aside>
                  <button
                    hx-get="{% url ':note_reference_edit' note_reference.id %}"
                    hx-trigger="click"
                    class="outline"
                  >Edit</button>
                  <button
                    hx-delete="{% url ':note_reference_delete' note_reference.id %}"
                    hx-confirm="Are you sure?"
                    class="outline"
                  >Delete</button>
                </aside>

                <hr>
              </div>

            {% endif %}
          {% endblock %}
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
note_reference_block = get_template_block(template, 'note_reference')


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


class NoteReferenceForm(forms.ModelForm):
    target_note = forms.ModelChoiceField(
        queryset=Note.objects.none(),
        required=False,
    )

    class Meta:
        model = NoteReference
        fields = ('question', 'target_note')

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        notebook_id = self.instance.note.notebook_id
        self.fields['target_note'].queryset = Note.objects.accessible_by_user(
            user,
        ).filter(
            notebook_id=notebook_id,
        )
        self.fields['target_note'].widget = NoteChoiceWidget(
            notebook_id=notebook_id,
        )


@router.route('GET', 'note-reference/<uuid:note_reference_id>/')
def note_reference_read(request, note_reference_id):
    note_reference = get_note_reference(request, note_reference_id)
    return TemplateResponse(request, note_reference_block, {
      'note_reference': note_reference,
      'editing': False,
    })


@router.route('GET', 'note-reference/<uuid:note_reference_id>/edit/')
def note_reference_edit(request, note_reference_id):
    note_reference = get_note_reference(request, note_reference_id)
    form = NoteReferenceForm(instance=note_reference, user=request.user)
    return TemplateResponse(request, note_reference_block, {
      'note_reference': note_reference,
      'editing': True,
      'form': form,
    })


@router.route('POST', 'note-reference/<uuid:note_reference_id>/edit/')
def note_reference_save(request, note_reference_id):
    note_reference = get_note_reference(request, note_reference_id)
    form = NoteReferenceForm(
        request.POST,
        instance=note_reference,
        user=request.user,
    )
    if form.is_valid():
        form.save()
        return TemplateResponse(request, note_reference_block, {
          'note_reference': note_reference,
          'editing': False,
        })
    else:
        return TemplateResponse(request, note_reference_block, {
          'note_reference': note_reference,
          'editing': True,
          'form': form,
        })


@router.route('DELETE', 'note-reference/<uuid:note_reference_id>/')
def note_reference_delete(request, note_reference_id):
    note_reference = get_note_reference(request, note_reference_id)
    note_reference.delete()
    return HttpResponse()


def get_note_reference(request, note_reference_id):
    return get_object_or_404(
        NoteReference.objects.accessible_by_user(request.user),
        id=note_reference_id,
    )
