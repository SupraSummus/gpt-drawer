import pytest
from django.test.client import Client


pytest_plugins = [
    'users.models_test',
    'notes.models_test',
]


@pytest.fixture
def user_client(user):
    client = Client()
    client.force_login(user)
    return client
