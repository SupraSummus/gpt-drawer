from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from djsfc import Router, parse_template

from ..models import Notebook


router = Router(__name__)
template_str = '''\
{% extends 'base_main.html' %}

{% block title %}{{ notebook.title }}{% endblock %}

{% block main %}
  <h1>{{ notebook.title }}</h1>
  <p>
    <a href="{% url 'notebook-ask-me' notebook.id %}" role="button">Ask me something</a>
  </p>
  {% for note in notes %}
    <article>
      <h2>{{ note }}</h2>
      <p style="white-space: pre-line;">{{ note.content|truncatechars:200 }}</p>
      <p>
        <a href="{% url 'notes:note:root' note.id %}">
          See more
        </a>
      </p>
    </article>
  {% endfor %}
{% endblock %}
'''
template = parse_template(template_str, router)


@router.route('GET', '/notebooks/<uuid:notebook_id>')
def root(request, notebook_id):
    notebook = get_notebook(request, notebook_id)
    return TemplateResponse(request, template, {
        'notebook': notebook,
        'notes': notebook.notes.all(),
    })


def get_notebook(request, notebook_id):
    return get_object_or_404(
        Notebook.objects.accessible_by_user(request.user),
        id=notebook_id,
    )
