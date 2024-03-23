from django.shortcuts import redirect
from django.template import engines
from django.template.response import TemplateResponse

from router import Router

from .models import Note, NoteReference


engine = engines['django']
router = Router()

template_str = '''
{% extends 'base.html' %}

{% block content %}
  <main class="container">
    <form method="post" action="{% url ':submit_answer' note_reference.id %}">
      {% csrf_token %}

      <h2>Question</h2>
      <p>{{ note_reference.question }}</p>
      <button type="submit" name="more_context">I need more context</button>
      <button type="submit" name="not_relevant">Not relevant</button>
      <button type="submit" name="ask_later">Ask me later</button>

      <h2>Answer</h2>
      <textarea name="answer" rows="4"
        hx-get="{% url ':get_suggestions' note_reference.id %}"
        hx-trigger="input change"
        hx-target="#suggested_notes"
        hx-swap="outerHTML"
        hx-vals="answer"
      >{{ note_reference.answer }}</textarea>
      <button type="submit" name="create_note">Create note</button>

      <h2>Suggested Notes</h2>
      {% block suggested_notes %}
        <div id="suggested_notes">
          {% for note in suggeted_notes %}
            <article>
              <h3>{{ note.title }}</h3>
              <p>{{ note.question }}</p>
              <button type="submit" name="note_id" value="{{ note.id }}">Select</button>
            </article>
          {% endfor %}
        </div>
      {% endblock %}

    </form>
  </main>
{% endblock %}
'''
template = engine.from_string(template_str)


@router.route('GET', '<uuid:note_reference_id>/')
def root(request, note_reference_id):
    note_reference = NoteReference.objects.get(id=note_reference_id)
    return TemplateResponse(request, template, {
        'note_reference': note_reference,
        'suggested_notes': Note.objects.all(),
    })


@router.route('POST', '<uuid:note_reference_id>/')
def submit_answer(request, note_reference_id):
    note_reference = NoteReference.objects.get(id=note_reference_id)
    if 'more_context' in request.POST:
        note_reference.target_note = None
    elif 'not_relevant' in request.POST:
        note_reference.target_note = Note.objects.none()
    elif 'ask_later' in request.POST:
        note_reference.target_note = Note.objects.none()
    elif 'create_note' in request.POST:
        note = Note.objects.create(
            notebook=note_reference.note.notebook,
            question=note_reference.question,
            answer=request.POST['answer'],
        )
        note_reference.target_note = note
    note_reference.answer = request.POST['answer']
    note_reference.save()
    return redirect(note_reference)


@router.route('GET', '<uuid:note_reference_id>/suggestions/')
def get_suggestions(request, note_reference_id):
    note_reference = NoteReference.objects.get(id=note_reference_id)
    return template.render({
        'note_reference': note_reference,
        'suggested_notes': Note.objects.search(note_reference.answer),
    })
