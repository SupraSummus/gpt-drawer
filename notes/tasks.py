
import json

from django.db import transaction
from django_q.tasks import async_task
from pgvector.django import CosineDistance

from .models import Note, NoteReferenceState, NoteState, NoteVersion, Reference
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
            'Respond in JSON format, in the schema `{"next": ["...", "...", ...]}`.'
        ),
    }]

    example_notes = get_example_notes(note, 3).prefetch_related('references')
    for example_note in reversed(example_notes):
        messages.append({
            "role": "user",
            "content": example_note.content,
        })
        response_json = json.dumps({
            'next': [
                reference.target_note.content
                for reference in example_note.references.all()
            ],
        })
        messages.append({
            "role": "assistant",
            "content": response_json,
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
        max_tokens=4096,
    )
    response_parsed = json.loads(response.choices[0].message.content)
    new_notes_content = response_parsed.get('next', [])

    with transaction.atomic():
        new_notes = [
            Note(
                notebook_id=note.notebook_id,
                state=NoteState.SUGGESTED,
            )
            for _ in new_notes_content
        ]
        Note.objects.bulk_create(new_notes)
        new_versions = [
            NoteVersion(
                note=new_note,
                content=content,
                is_active=True,
            )
            for new_note, content in zip(new_notes, new_notes_content)
        ]
        NoteVersion.objects.bulk_create(new_versions)

        references = [
            Reference(
                note=note,
                target_note=new_note,
                state=NoteReferenceState.SUGGESTED,
            )
            for new_note in new_notes
        ]
        Reference.objects.bulk_create(references)

    for version in new_versions:
        async_task(generate_note_version_title, note_id=version.note_id, created_at=version.created_at)
        async_task(generate_note_version_embedding, note_id=version.note_id, created_at=version.created_at)

    note.generating_references = False
    note.save(update_fields=['generating_references'])


generate_note_references = generate_references


def check_reference_uniqueness(reference_id):
    reference = Reference.objects.get(id=reference_id)
    similar_references = Reference.objects.annotate(
        distance=CosineDistance('embedding', reference.embedding),
    ).filter(
        note_id=reference.note_id,
        distance__lt=0.1,
    ).exclude(id=reference.id)
    if similar_references.exists():
        reference.delete()
    else:
        reference.save(update_fields=['state'])


def generate_note_version_title(note_id, created_at):
    version = NoteVersion.objects.select_related('note').get(note_id=note_id, created_at=created_at)
    note = version.note

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
        "content": version.content,
    })
    response = openai_client.chat.completions.create(
        messages=messages,
        model='gpt-3.5-turbo',
        temperature=0,
        max_tokens=100,
    )
    version.title = response.choices[0].message.content[:64]
    version.save(update_fields=['title'])


def get_example_notes(note, count=3):
    return Note.objects.filter(
        referenced_notes=note,
    ).order_by('?')[:count]


def generate_note_version_embedding(note_id, created_at):
    version = NoteVersion.objects.get(note_id=note_id, created_at=created_at)
    version.embedding = generate_embedding(version.content)
    version.save(update_fields=['embedding'])
