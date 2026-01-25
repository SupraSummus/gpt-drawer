import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from ..models import AuthToken
from .factories import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestLoginEndpoint:
    def test_login_returns_token(self, api_client):
        password = 'testpassword123'
        user = UserFactory(username='testuser')
        user.set_password(password)
        user.save()

        url = reverse('knox_login')
        api_client.credentials(HTTP_AUTHORIZATION=f'Basic {self._get_basic_auth_header(user.username, password)}')
        response = api_client.post(url)

        assert response.status_code == 200
        assert 'token' in response.data
        assert 'expiry' in response.data

        token_obj = AuthToken.objects.get()
        assert token_obj.user == user
        assert token_obj.token_key == response.data['token'][:15]

    def test_login_invalid_credentials_returns_401(self, api_client):
        url = reverse('knox_login')
        auth_header = self._get_basic_auth_header("nonexistent", "wrongpassword")
        api_client.credentials(HTTP_AUTHORIZATION=f'Basic {auth_header}')
        response = api_client.post(url)

        assert response.status_code == 401

    @staticmethod
    def _get_basic_auth_header(username, password):
        import base64
        credentials = f'{username}:{password}'
        return base64.b64encode(credentials.encode()).decode()
