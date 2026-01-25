import pytest
from rest_framework.test import APIClient

from .models import AuthToken


@pytest.mark.django_db
def test_session_serializer_with_session_auth(user, client):
    client.force_login(user)
    response = client.get('/api/auth/users/me/')

    assert response.status_code == 200
    assert response.json()['id'] == str(user.id)
    assert response.json()['auth_method'] == 'SessionAuthentication'


@pytest.mark.django_db
def test_session_serializer_with_token_auth(user):
    _, token = AuthToken.objects.create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    response = client.get('/api/auth/users/me/')

    assert response.status_code == 200
    assert response.data['id'] == str(user.id)
    assert response.data['auth_method'] == 'TokenAuthentication'
