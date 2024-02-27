import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_note_autocomplete(admin_client, note, other_note):
    response = admin_client.get(
        reverse('admin:autocomplete'),
        {
            'app_label': 'notes',
            'model_name': 'reference',
            'field_name': 'target_note',
            'term': other_note.title,
        },
        HTTP_REFERER=reverse('admin:notes_note_change', args=(note.id,)),
    )
    assert response.status_code == 200
    assert str(other_note.id) in (r['id'] for r in response.json()['results'])


@pytest.mark.django_db
def test_note_autocomplete_when_adding(admin_client, other_note):
    response = admin_client.get(
        reverse('admin:autocomplete'),
        {
            'app_label': 'notes',
            'model_name': 'reference',
            'field_name': 'target_note',
            'term': other_note.title,
        },
        HTTP_REFERER=reverse('admin:notes_note_add'),
    )
    assert response.status_code == 200
    assert str(other_note.id) in (r['id'] for r in response.json()['results'])


@pytest.mark.django_db
def test_note_autocomplete_outside_notebook(admin_client, note, other_notebook_note):
    response = admin_client.get(
        reverse('admin:autocomplete'),
        {
            'app_label': 'notes',
            'model_name': 'reference',
            'field_name': 'target_note',
            'term': other_notebook_note.title,
        },
        HTTP_REFERER=reverse('admin:notes_note_change', args=(note.id,)),
    )
    assert response.status_code == 200
    print(response.json())
    assert str(other_notebook_note.id) not in (r['id'] for r in response.json()['results'])
