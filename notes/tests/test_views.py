import pytest
from django.urls import reverse

from ..models import NoteReference


@pytest.mark.django_db
def test_note_detail(user_client, note, notebook_user_permission):
    response = user_client.get(reverse('notes:note:root', kwargs={'note_id': note.id}))
    assert response.status_code == 200
    assert response.context['note'] == note


@pytest.mark.django_db
def test_note_get_edit_form(user_client, note, notebook_user_permission):
    response = user_client.get(reverse('notes:note:edit', kwargs={'note_id': note.id}))
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


@pytest.mark.django_db
def test_note_reference_answer(user_client, note_reference, notebook_user_permission):
    response = user_client.get(reverse(
        'notes:answer:root',
        kwargs={'note_reference_id': note_reference.id},
    ))
    assert response.status_code == 200


@pytest.mark.django_db
def test_answer_get_suggestions(user_client, note_reference, notebook_user_permission):
    response = user_client.get(reverse(
        'notes:answer:get_suggestions',
        kwargs={'note_reference_id': note_reference.id},
    ))
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize('other_note', [{'title': 'Another note'}], indirect=True)
def test_answer_suggestions_some(user_client, note_reference, other_note, notebook_user_permission):
    response = user_client.get(reverse(
        'notes:answer:get_suggestions',
        kwargs={'note_reference_id': note_reference.id},
    ), {'answer': other_note.title})
    assert response.status_code == 200
    assert other_note.title in response.content.decode()
