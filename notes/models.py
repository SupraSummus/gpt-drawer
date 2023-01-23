from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model


User = get_user_model()


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

    class Meta:
        verbose_name = _('notebook')
        verbose_name_plural = _('notebooks')


class NoteBookAccess(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('identifier'),
    )
    notebook = models.ForeignKey(
        to=NoteBook,
        on_delete=models.CASCADE,
        related_name='accesses',
        verbose_name=_('notebook'),
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='notebook_accesses',
        verbose_name=_('user'),
    )

    class Meta:
        verbose_name = _('notebook access')
        verbose_name_plural = _('notebook accesses')
        unique_together = (
            ('notebook', 'user'),
        )
        ordering = ('notebook', 'user')


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
