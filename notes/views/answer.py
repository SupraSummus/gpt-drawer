from django import forms
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from djsfc import Router, get_template_block, parse_template

from ..models import Note, NoteReference


router = Router(__name__)

template_str = '''\
{% extends 'base.html' %}

{% block content %}
  <main class="container">
    <h2>Question</h2>
    <p>{{ note_reference.question }}</p>

    <form method="post" action="{% url ':dont_answer' note_reference.id %}">
      {% csrf_token %}
      <button type="submit" name="action" value="not_relevant">Not relevant</button>
      <button type="submit" name="action" value="ask_later">Ask me later</button>
    </form>

    <h2>Answer</h2>
    <form method="post" action="{% url ':create_answer' note_reference.id %}">
      {% csrf_token %}
      <textarea name="answer" rows="4"
        hx-get="{% url ':get_suggestions' note_reference.id %}"
        hx-trigger="input change delay:500ms"
        hx-target="#suggested_notes"
        hx-swap="outerHTML"
        hx-vals="answer"
      >{{ note_reference.answer }}</textarea>
      <button type="submit">Create note</button>
    </form>

    <h2>Suggested Notes</h2>
    {% block suggested_notes %}
      <div id="suggested_notes">
        {% for note in suggested_notes %}
          <article>
            <form method="post" action="{% url ':select_answer' note_reference.id %}">
              {% csrf_token %}
              <h3>{{ note.title }}</h3>
              <p>{{ note.content }}</p>
              <button type="submit" name="target_note" value="{{ note.id }}">Select</button>
            </form>
          </article>
        {% endfor %}
      </div>
    {% endblock %}

    </form>
  </main>
{% endblock %}
'''
template = parse_template(template_str, router)


@router.route('GET', '<uuid:note_reference_id>/')
def root(request, note_reference_id):
    note_reference = get_note_reference(request, note_reference_id)
    if note_reference.answer:
        suggested_notes = Note.objects.autocomplete_search(note_reference.answer)
    else:
        suggested_notes = Note.objects.autocomplete_search(note_reference.question)
    return TemplateResponse(request, template, {
        'note_reference': note_reference,
        'suggested_notes': suggested_notes,
    })


@router.route('POST', '<uuid:note_reference_id>/dont-answer/')
def dont_answer(request, note_reference_id):
    note_reference = get_note_reference(request, note_reference_id)
    form = DontAnswerForm(request.POST)
    if not form.is_valid():
        return root(request, note_reference_id)
    note = note_reference.note
    if form.cleaned_data['action'] == 'not_relevant':
        note_reference.delete()
    return redirect(note)


class DontAnswerForm(forms.Form):
    action = forms.ChoiceField(
        choices=(
            ('not_relevant', 'Not relevant'),
            ('ask_later', 'Ask me later'),
        ),
    )


@router.route('POST', '<uuid:note_reference_id>/create-answer/')
def create_answer(request, note_reference_id):
    note_reference = get_note_reference(request, note_reference_id)
    form = CreateAnswerForm(request.POST)
    if not form.is_valid():
        return root(request, note_reference_id)
    note = Note.objects.create(
        notebook_id=note_reference.notebook_id,
        content=form.cleaned_data['answer'],
    )
    note_reference.target_note = note
    note_reference.save(update_fields=['target_note'])
    return redirect(note)


class CreateAnswerForm(forms.Form):
    answer = forms.CharField()


@router.route('POST', '<uuid:note_reference_id>/select-answer/')
def select_answer(request, note_reference_id):
    note_reference = get_note_reference(request, note_reference_id)
    form = SelectAnswerForm(request.POST, notebook_id=note_reference.notebook_id)
    if not form.is_valid():
        return root(request, note_reference_id)
    note_reference.target_note = form.cleaned_data['target_note']
    note_reference.save(update_fields=['target_note'])
    return redirect(note_reference)


class SelectAnswerForm(forms.Form):
    target_note = forms.ModelChoiceField(queryset=Note.objects.none())

    def __init__(self, *args, notebook_id, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['target_note'].queryset = Note.objects.filter(notebook_id=notebook_id)


@router.route('GET', '<uuid:note_reference_id>/suggestions/')
def get_suggestions(request, note_reference_id):
    note_reference = get_note_reference(request, note_reference_id)
    text = request.GET.get('answer', '')
    suggested_notes = Note.objects.filter(
      notebook_id=note_reference.notebook_id,
    ).autocomplete_search(text)
    template_block = get_template_block(template, 'suggested_notes')
    return TemplateResponse(request, template_block, {
        'note_reference': note_reference,
        'suggested_notes': suggested_notes,
    })


def get_note_reference(request, note_reference_id):
    user = request.user
    note_reference = get_object_or_404(
        NoteReference.objects.accessible_by_user(user),
        id=note_reference_id,
    )
    return note_reference
