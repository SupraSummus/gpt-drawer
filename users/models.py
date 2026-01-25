import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from knox.models import AbstractAuthToken


class User(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('identifier'),
    )


class AuthToken(AbstractAuthToken):
    """
    Custom AuthToken model extending knox's AbstractAuthToken.
    Add custom fields here as needed.
    """

    class Meta:
        verbose_name = _('auth token')
        verbose_name_plural = _('auth tokens')
