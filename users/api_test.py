import base64

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from .models import AuthToken
from .models_test import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


def _get_basic_auth_header(username, password):
    credentials = f'{username}:{password}'
    return base64.b64encode(credentials.encode()).decode()


@pytest.mark.django_db
def test_login_returns_token(api_client):
    password = 'testpassword123'
    user = UserFactory(username='testuser')
    user.set_password(password)
    user.save()

    url = reverse('knox_login')
    api_client.credentials(HTTP_AUTHORIZATION=f'Basic {_get_basic_auth_header(user.username, password)}')
    response = api_client.post(url)

    assert response.status_code == 200
    assert 'token' in response.data
    assert 'expiry' in response.data

    token_obj = AuthToken.objects.get()
    assert token_obj.user == user
    assert token_obj.token_key == response.data['token'][:15]


@pytest.mark.django_db
def test_login_invalid_credentials_returns_401(api_client):
    url = reverse('knox_login')
    auth_header = _get_basic_auth_header("nonexistent", "wrongpassword")
    api_client.credentials(HTTP_AUTHORIZATION=f'Basic {auth_header}')
    response = api_client.post(url)

    assert response.status_code in [401, 403]


@pytest.mark.django_db
def test_login_with_incorrect_credentials_www_authenticate_header(api_client):
    url = reverse('knox_login')

    headers = {'HTTP_AUTHORIZATION': f'Basic {_get_basic_auth_header("wrong@example.com", "wrongpassword")}'}

    response = api_client.post(url, **headers)

    www_authenticate = response.headers.get('WWW-Authenticate', '')
    expected_component = 'Basic realm="api"'
    assert expected_component not in www_authenticate
