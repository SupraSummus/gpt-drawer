import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class NotebookQuerySet(models.QuerySet):
    def accessible_by_user(self, user):
        return self.filter(user_permissions__user=user)


class Notebook(models.Model):
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

    objects = NotebookQuerySet.as_manager()

    class Meta:
        verbose_name = _('notebook')
        verbose_name_plural = _('notebooks')


class NotebookUserPermission(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('identifier'),
    )
    notebook = models.ForeignKey(
        to=Notebook,
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
        to=Notebook,
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

    def set_aliases(self, aliases):
        to_delete = {
            alias.title: alias
            for alias in self.aliases.all()
        }
        to_create = {}
        to_keep = {}
        for alias in aliases:
            assert alias.note == self
            if alias.title in to_delete:
                del to_delete[alias.title]
                to_keep[alias.title] = alias
            elif alias.title in to_create or alias.title in to_keep:
                pass
            else:
                to_create[alias.title] = alias
        Alias.objects.bulk_create(to_create.values())
        Alias.objects.filter(id__in=[alias.id for alias in to_delete.values()]).delete()

    def set_references(self, references):
        to_delete = {
            reference.target_note: reference
            for reference in self.references.all()
        }
        to_create = {}
        to_keep = {}
        for reference in references:
            assert reference.note == self
            assert reference.target_note.notebook == self.notebook
            if reference.target_note in to_delete:
                del to_delete[reference.target_note]
                to_keep[reference.target_note] = reference
            elif reference.target_note in to_create or reference.target_note in to_keep:
                pass
            else:
                to_create[reference.target_note] = reference
        Reference.objects.bulk_create(to_create.values())
        Reference.objects.filter(id__in=[reference.id for reference in to_delete.values()]).delete()


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
    target_note = models.ForeignKey(
        to=Note,
        on_delete=models.PROTECT,
        related_name='references_to',
        verbose_name=_('target note'),
    )

    class Meta:
        verbose_name = _('reference')
        verbose_name_plural = _('references')
        unique_together = (
            ('note', 'target_note'),
        )
        ordering = ('note', 'target_note')
