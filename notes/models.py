import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from pgvector.django import VectorField

from .openai import openai_client


User = get_user_model()


def schedulable(func):
    return func


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
        ordering = ('title', 'id')

    def __str__(self):
        return self.title


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

    referenced_notes = models.ManyToManyField(
        to='self',
        through='Reference',
        symmetrical=False,
        through_fields=('note', 'target_note'),
        related_name='referencing_notes',
        verbose_name=_('referenced notes'),
    )

    objects = NoteQuerySet.as_manager()

    class Meta:
        verbose_name = _('note')
        verbose_name_plural = _('notes')
        unique_together = (
            ('notebook', 'title'),
        )
        ordering = ('notebook', 'title')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('note-detail', kwargs={'pk': self.id})

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


class ReferenceState(models.TextChoices):
    # Question was automatically genenerated but we are waiting for the uniqueness check
    CHECKING_UNIQUENESS = 'checking_uniqueness', _('Checking uniqueness')
    # Question was automatically genenerated and uniqueness check passed
    # or the question was manually added or modified
    ACTIVE = 'active', _('Active')


class ReferenceQuerySet(models.QuerySet):
    def accessible_by_user(self, user):
        return self.filter(note__notebook__user_permissions__user=user)


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
    state = models.CharField(
        max_length=20,
        choices=ReferenceState.choices,
        default=ReferenceState.ACTIVE,
        verbose_name=_('state'),
    )
    question = models.TextField(
        verbose_name=_('question'),
        blank=True,
    )
    embedding = VectorField(
        dimensions=3072,
        verbose_name=_('embedding'),
        null=True,
        blank=True,
    )
    target_note = models.ForeignKey(
        to=Note,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='references_to',
        verbose_name=_('target note'),
    )

    objects = ReferenceQuerySet.as_manager()

    class Meta:
        verbose_name = _('reference')
        verbose_name_plural = _('references')
        unique_together = (
            ('note', 'target_note'),
        )
        ordering = ('note', 'target_note')

    def get_absolute_url(self):
        return reverse('note-reference', kwargs={'pk': self.id})

    def clean_fields(self, exclude=()):
        super().clean_fields(exclude=exclude)

        if (
            'note' not in exclude and
            'target_note' not in exclude and
            self.target_note is not None and
            self.target_note.notebook_id != self.note.notebook_id
        ):
            raise models.ValidationError({
                'target_note': _(
                    'The target note must be in the same notebook as the source note.'
                ),
            }, code='notebook_mismatch')

    def generate_embedding(self):
        response = openai_client.embeddings.create(
            input=self.question,
            model='text-embedding-3-large',
        )
        embedding = response.data[0].embedding
        assert len(embedding) == 3072
        self.embedding = embedding


NoteReference = Reference
