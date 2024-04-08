import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_note_reference_read(user_client, note_reference, notebook_user_permission):
    response = user_client.get(reverse(
        'notes:note:note_reference_read',
        kwargs={'note_reference_id': note_reference.id},
    ))
    assert response.status_code == 200
    assert response.context['note_reference'] == note_reference


@pytest.mark.django_db
def test_note_reference_edit(user_client, note_reference, notebook_user_permission):
    response = user_client.get(reverse(
        'notes:note:note_reference_edit',
        kwargs={'note_reference_id': note_reference.id},
    ))
    assert response.status_code == 200
    assert response.context['note_reference'] == note_reference


@pytest.mark.django_db
def test_new_note_form(user_client, note, notebook_user_permission):
    response = user_client.get(reverse('notes:note:new_note_form', kwargs={'note_id': note.id}))
    assert response.status_code == 200
    assert response.context_data['note'] == note
    assert 'form' in response.context_data


@pytest.mark.django_db
def test_new_note_save(user_client, note, notebook_user_permission):
    response = user_client.post(
        reverse('notes:note:new_note_save', kwargs={'note_id': note.id}),
        data={},
    )
    assert response.status_code == 200

    # reference is in DB
    note.refresh_from_db()
    assert note.references.count() == 1


@pytest.mark.django_db
def test_trigger_auto_qa_generation(user_client, note, notebook_user_permission):
    response = user_client.post(reverse(
        'notes:note:trigger_auto_qa_generation',
        kwargs={'note_id': note.id},
    ))
    assert response.status_code == 200
