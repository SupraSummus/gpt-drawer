import pytest
from django.urls import reverse

from ..models import NoteReference


@pytest.mark.django_db
def test_note_detail(user_client, note, notebook_user_permission):
    response = user_client.get(reverse('note-detail', kwargs={'note_id': note.id}))
    assert response.status_code == 200
    assert response.context['note'] == note


@pytest.mark.django_db
def test_note_reference_create_get(user_client, note, notebook_user_permission):
    response = user_client.get(reverse('note-reference-create', kwargs={'note_id': note.id}))
    assert response.status_code == 200
    assert response.context['note'] == note


@pytest.mark.django_db
def test_note_reference_create_post(user_client, note, notebook_user_permission):
    response = user_client.post(
        reverse('note-reference-create', kwargs={'note_id': note.id}),
        data={'question': 'This is a note reference'},
    )
    assert response.status_code == 302
    note_reference_id = response.url.split('/')[-2]
    note_reference = NoteReference.objects.get(id=note_reference_id)
    assert note_reference.note == note
    assert note_reference.question == 'This is a note reference'
