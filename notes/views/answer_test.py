import pytest
from django.urls import reverse


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
