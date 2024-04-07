import pytest
from django.urls import reverse

from .note_select import router


@pytest.mark.django_db
@pytest.mark.urls(router.urls)
def test_select_dialog(user_client, user, note, notebook_user_permission):
    url = reverse(
        'select_dialog',
        kwargs={'field_name': 'field_name', 'note_id': note.id},
    )
    response = user_client.get(url)
    assert response.status_code == 200
