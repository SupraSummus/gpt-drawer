import pytest
from django.urls import reverse

from notes.models import Note


@pytest.mark.django_db
def test_create_note_get_form(user_client, notebook, notebook_user_permission):
    response = user_client.get(reverse('notes:notebook:create_note_form', kwargs={'notebook_id': notebook.id}))
    assert response.status_code == 200
    assert 'form' in response.context


@pytest.mark.django_db
def test_create_note_valid_form(user_client, notebook, notebook_user_permission):
    form_data = {
        'content': 'This is a test note.',
    }
    response = user_client.post(
        reverse('notes:notebook:create_note', kwargs={'notebook_id': notebook.id}),
        data=form_data,
    )
    assert response.status_code == 200
    assert response.context['note'].content == 'This is a test note.'
    assert response.context['note'].notebook == notebook


@pytest.mark.django_db
def test_note_card(user_client, note, notebook_user_permission):
    response = user_client.get(reverse('notes:notebook:note_card', kwargs={'note_id': note.id}))
    assert response.status_code == 200
    assert response.context['note'] == note


@pytest.mark.django_db
def test_delete_note(user_client, note, notebook_user_permission):
    response = user_client.delete(reverse('notes:notebook:delete_note', kwargs={'note_id': note.id}))
    assert response.status_code == 200
    assert not Note.objects.filter(id=note.id).exists()
