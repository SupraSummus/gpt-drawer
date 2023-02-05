import pytest
from django.urls import reverse

from ..models import Alias, Note, Reference
from .factories import AliasFactory, NotebookFactory, NotebookUserPermissionFactory, NoteFactory, ReferenceFactory


@pytest.fixture
def user_notebook(user):
    notebook = NotebookFactory()
    NotebookUserPermissionFactory(notebook=notebook, user=user)
    return notebook


@pytest.mark.django_db
def test_note_create(user_client, user_notebook):
    other_note_a = NoteFactory(notebook=user_notebook)
    other_note_b = NoteFactory(notebook=user_notebook)
    response = user_client.post(
        reverse('api:note-list'),
        data={
            'title': 'Test note',
            'content': 'Test content',
            'notebook_id': user_notebook.id,
            'aliases': [
                {'title': 'Test alias 1'},
                {'title': 'Test alias 2'},
                {'title': 'Test alias 1'},  # Duplicate should be ignored
            ],
            'references': [
                {'target_note_id': other_note_a.id},
                {'target_note_id': other_note_b.id},
                {'target_note_id': other_note_a.id},  # Duplicate should be ignored
            ],
        },
        content_type='application/json',
    )
    assert response.status_code == 201, response.content

    note = Note.objects.get(id=response.data['id'])
    assert note.title == 'Test note'
    assert note.content == 'Test content'
    assert note.notebook.id == user_notebook.id
    assert note.aliases.count() == 2
    assert set(note.aliases.values_list('title', flat=True)) == {'Test alias 1', 'Test alias 2'}
    assert note.references.count() == 2
    assert set(note.references.values_list('target_note__id', flat=True)) == {other_note_a.id, other_note_b.id}


@pytest.mark.django_db
def test_note_create_reference_to_other_notebook(user, user_client, user_notebook):
    other_notebook = NotebookFactory()
    NotebookUserPermissionFactory(notebook=other_notebook, user=user)
    other_note = NoteFactory(notebook=other_notebook)

    response = user_client.post(
        reverse('api:note-list'),
        data={
            'title': 'Test note',
            'content': 'Test content',
            'notebook_id': user_notebook.id,
            'aliases': [],
            'references': [
                {'target_note_id': other_note.id},
            ],
        },
        content_type='application/json',
    )
    assert response.status_code == 400, response.content
    assert 'same notebook' in response.data['references'][0].lower()


@pytest.mark.django_db
def test_note_update(user_client, user_notebook):
    note = NoteFactory(notebook=user_notebook)
    alias_a = AliasFactory(note=note)
    alias_b = AliasFactory(note=note)
    reference_a = ReferenceFactory(note=note, target_note__notebook=user_notebook)
    reference_b = ReferenceFactory(note=note, target_note__notebook=user_notebook)
    other_note_c = NoteFactory(notebook=user_notebook)
    response = user_client.patch(
        reverse('api:note-detail', args=[note.id]),
        data={
            'aliases': [
                {'title': alias_a.title},
                {'title': 'Test alias 2'},
                {'title': alias_a.title},
                {'title': 'Test alias 2'},
            ],
            'references': [
                {'target_note_id': reference_a.target_note.id},
                {'target_note_id': other_note_c.id},
                {'target_note_id': reference_a.target_note.id},
                {'target_note_id': other_note_c.id},
            ],
        },
        content_type='application/json',
    )
    assert response.status_code == 200, response.content

    assert note.aliases.count() == 2
    assert set(note.aliases.values_list('title', flat=True)) == {alias_a.title, 'Test alias 2'}
    assert Alias.objects.filter(id=alias_a.id).exists()
    assert not Alias.objects.filter(id=alias_b.id).exists()

    assert note.references.count() == 2
    assert set(note.references.values_list('target_note__id', flat=True)) == {
        reference_a.target_note.id,
        other_note_c.id,
    }
    assert Reference.objects.filter(id=reference_a.id).exists()
    assert not Reference.objects.filter(id=reference_b.id).exists()


@pytest.mark.django_db
def test_note_update_reference_to_other_notebook(user, user_client, user_notebook):
    note = NoteFactory(notebook=user_notebook)

    other_notebook = NotebookFactory()
    NotebookUserPermissionFactory(notebook=other_notebook, user=user)
    other_note = NoteFactory(notebook=other_notebook)

    response = user_client.patch(
        reverse('api:note-detail', args=[note.id]),
        data={
            'references': [
                {'target_note_id': other_note.id},
            ],
        },
        content_type='application/json',
    )
    assert response.status_code == 400, response.content
    assert 'same notebook' in response.data['references'][0].lower()
