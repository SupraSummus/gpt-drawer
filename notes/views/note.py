from django import forms
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils import timezone

from djsfc import Router, get_template_block, parse_template

from ..models import Note, NoteReference
from ..widgets import NoteChoiceWidget


router = Router(__name__)


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

        {% if adding_reference %}
          {% block new_note_reference %}
            <form
              hx-post="{% url ':new_note_reference_save' note.id %}"
              hx-target="this" hx-swap="outerHTML"
            >
              {% csrf_token %}
              {{ form.as_div }}
              <div class="grid">
                <button type="submit">Save</button>
                <button type="reset" hx-on:click="this.closest('form').remove()">Cancel</button>
              </div>
            </form>
          {% endblock %}
        {% endif %}

        <p hx-target="this" hx-swap="beforebegin">
          <button class="outline"
            hx-get="{% url ':new_note_reference_form' note.id %}"
            hx-trigger="click"
          >Add QA entry</button>
          {% block generate_references_button %}
            <button class="outline"
              hx-target="this"
              hx-swap="outerHTML"
              hx-vals='{ "now": "{{ now.isoformat }}" }'
              {% if note.generating_references %}
                disabled
                aria-busy="true"
                hx-get="{% url ':generate_references_button' note.id %}"
                hx-trigger="load delay:2s"
              {% else %}
                hx-post="{% url ':trigger_auto_qa_generation' note.id %}"
              {% endif %}
            >Generate QA</button>
          {% endblock %}
        </p>

      </dl>
    </section>
    {% include 'notes/views/asdf.html' %}
  </main>
{% endblock %}
'''
template = parse_template(template_str, router)
note_block = get_template_block(template, 'note')
note_reference_block = get_template_block(template, 'note_reference')
new_note_reference_block = get_template_block(template, 'new_note_reference')
generate_references_button_template = get_template_block(template, 'generate_references_button')

router.route_all('asdf/', 'notes.views.asdf')


@router.route('GET', '<uuid:note_id>/')
def root(request, note_id):
    note = get_note(request, note_id)
    return TemplateResponse(request, template, {
      'note': note,
      'editing': False,
      'adding_reference': False,
      'now': timezone.now(),
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


@router.route('GET', '<uuid:note_id>/new-reference/')
def new_note_reference_form(request, note_id):
    note = get_note(request, note_id)
    note_reference = NoteReference(note=note)
    form = NoteReferenceForm(instance=note_reference, user=request.user)
    return TemplateResponse(request, new_note_reference_block, {
      'note': note,
      'form': form,
    })


@router.route('POST', '<uuid:note_id>/new-reference/')
def new_note_reference_save(request, note_id):
    note = get_note(request, note_id)
    note_reference = NoteReference(note=note)
    form = NoteReferenceForm(request.POST, instance=note_reference, user=request.user)
    if form.is_valid():
        form.save()
        return TemplateResponse(request, note_reference_block, {
          'note_reference': note_reference,
          'editing': False,
        })
    else:
        return TemplateResponse(request, new_note_reference_block, {
          'note': note,
          'form': form,
        })


@router.route('GET', '<uuid:note_id>/generate-references-button')
def generate_references_button(request, note_id):
    note = get_note(request, note_id)
    return TemplateResponse(request, generate_references_button_template, {
        'note': note,
        'now': timezone.now(),
    })


@router.route('POST', '<uuid:note_id>/trigger-auto-qa-generation')
def trigger_auto_qa_generation(request, note_id):
    note = get_note(request, note_id)
    note.schedule_generate_references()
    return TemplateResponse(request, generate_references_button_template, {
        'note': note,
        'now': timezone.now(),
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
