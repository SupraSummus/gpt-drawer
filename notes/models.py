import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class NoteBookQuerySet(models.QuerySet):
    def accessible_by_user(self, user):
        return self.filter(user_permissions__user=user)


class NoteBook(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('identifier'),
    )
    title = models.CharField(
        max_length=64,
        verbose_name=_('title'),
    )

    objects = NoteBookQuerySet.as_manager()

    class Meta:
        verbose_name = _('notebook')
        verbose_name_plural = _('notebooks')


class NoteBookUserPermission(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('identifier'),
    )
    notebook = models.ForeignKey(
        to=NoteBook,
        on_delete=models.CASCADE,
        related_name='user_permissions',
        verbose_name=_('notebook'),
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='notebook_permissions',
        verbose_name=_('user'),
    )

    class Meta:
        verbose_name = _('notebook user permission')
        verbose_name_plural = _('notebook user permissions')
        unique_together = (
            ('notebook', 'user'),
        )
        ordering = ('notebook', 'user')


class NoteQuerySet(models.QuerySet):
    def accessible_by_user(self, user):
        return self.filter(notebook__user_permissions__user=user)


class Note(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('identifier'),
    )
    notebook = models.ForeignKey(
        to=NoteBook,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('notebook'),
    )
    title = models.CharField(
        max_length=64,
        verbose_name=_('title'),
    )
    content = models.TextField(
        verbose_name=_('content'),
        blank=True,
    )

    objects = NoteQuerySet.as_manager()

    class Meta:
        verbose_name = _('note')
        verbose_name_plural = _('notes')
        unique_together = (
            ('notebook', 'title'),
        )
        ordering = ('notebook', 'title')


class Alias(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('identifier'),
    )
    note = models.ForeignKey(
        to=Note,
        on_delete=models.CASCADE,
        related_name='aliases',
        verbose_name=_('note'),
    )
    title = models.CharField(
        max_length=64,
        verbose_name=_('title'),
    )

    class Meta:
        verbose_name = _('alias')
        verbose_name_plural = _('aliases')
        unique_together = (
            ('note', 'title'),
        )
        ordering = ('note', 'title')


class Reference(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('identifier'),
    )
    note = models.ForeignKey(
        to=Note,
        on_delete=models.CASCADE,
        related_name='references',
        verbose_name=_('source note'),
    )
    offset = models.PositiveIntegerField(
        verbose_name=_('link offset'),
    )
    length = models.PositiveIntegerField(
        verbose_name=_('link length'),
    )
    target_note = models.ForeignKey(
        to=Note,
        on_delete=models.PROTECT,
        related_name='referenced_by',
        verbose_name=_('target note'),
    )

    class Meta:
        verbose_name = _('reference')
        verbose_name_plural = _('references')
        unique_together = (
            ('note', 'target_note'),
        )
        ordering = ('note', 'offset')
