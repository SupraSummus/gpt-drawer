import factory
import pytest

from .models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User


@pytest.fixture
def user():
    return UserFactory()
