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
