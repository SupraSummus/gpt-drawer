
import json

import django_q
from django_q.tasks import async_chain
from pgvector.django import CosineDistance

from .models import Note, Reference, ReferenceState
from .openai import generate_embedding, openai_client


def generate_references(note_id):
    """
    We are making LLM call to generate questions for this note.
    We give it examples of other notes nearby.
    """
    note = Note.objects.get(id=note_id)

    messages = [{
        'role': 'system',
        'content': (
            'If you were to continue expanding on this topic, '
            'what are the next logical questions you would explore? '
            'Phrase them concisely. '
            'Respond in JSON, in the schema `{"questions": ["first question", "second question", ...]}`.'
        ),
    }]

    example_notes = get_example_notes(note, 3).prefetch_related('references')
    for example_note in example_notes:
        messages.append({
            "role": "user",
            "content": example_note.content,
        })
        questions_json = json.dumps([
            reference.question
            for reference in example_note.references.all()
        ])
        messages.append({
            "role": "assistant",
            "content": questions_json,
        })

    messages.append({
        "role": "user",
        "content": note.content,
    })
    response = openai_client.chat.completions.create(
        messages=messages,
        response_format={'type': 'json_object'},
        model='gpt-3.5-turbo',
        temperature=0,
        max_tokens=1000,
    )
    response_parsed = json.loads(response.choices[0].message.content)
    questions = response_parsed.get('questions', [])
    references = [
        Reference(
            note=note,
            question=question,
            state=ReferenceState.CHECKING_UNIQUENESS,
        )
        for question in questions
    ]
    Reference.objects.bulk_create(references)
    for reference in references:
        async_chain([
            ('notes.tasks.generate_reference_embedding', (reference.id,)),
            ('notes.tasks.check_reference_uniqueness', (reference.id,)),
        ], sync=django_q.conf.Conf.SYNC)


def check_reference_uniqueness(reference_id):
    reference = Reference.objects.get(id=reference_id)
    similar_references = Reference.objects.annotate(
        distance=CosineDistance('embedding', reference.embedding),
    ).filter(
        note_id=reference.note_id,
        state=ReferenceState.ACTIVE,
        distance__lt=0.1,
    ).exclude(id=reference.id)
    if similar_references.exists():
        reference.delete()
    else:
        reference.state = ReferenceState.ACTIVE
        reference.save(update_fields=['state'])


def generate_note_title(note_id):
    note = Note.objects.get(id=note_id)

    messages = [
        {
            "role": "system",
            "content": "Generate a title for note you are given.",
        },
    ]

    example_notes = get_example_notes(note, 3)
    for example_note in example_notes:
        messages.append({
            "role": "user",
            "content": example_note.content,
        })
        messages.append({
            "role": "assistant",
            "content": example_note.title,
        })

    messages.append({
        "role": "user",
        "content": note.content,
    })
    response = openai_client.chat.completions.create(
        messages=messages,
        model='gpt-3.5-turbo',
        temperature=0,
        max_tokens=100,
    )
    note.title = response.choices[0].message.content[:64]
    note.save(update_fields=['title'])


def get_example_notes(note, count=3):
    return Note.objects.filter(
        referenced_notes=note,
    ).order_by('?')[:count]


def generate_note_embedding(note_id):
    note = Note.objects.get(id=note_id)
    note.embedding = generate_embedding(note.content)
    note.save(update_fields=['embedding'])


def generate_reference_embedding(reference_id):
    reference = Reference.objects.get(id=reference_id)
    reference.embedding = generate_embedding(reference.question)
    reference.save(update_fields=['embedding'])
