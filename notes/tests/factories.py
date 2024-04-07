import factory

from ..models import Alias, Note, Notebook, NotebookUserPermission, Reference


class NotebookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notebook


class NotebookUserPermissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NotebookUserPermission


class NoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Note

    notebook = factory.SubFactory(NotebookFactory)
    title = factory.Sequence(lambda n: f'Test note {n}')


class AliasFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Alias

    title = factory.Sequence(lambda n: f'Test alias {n}')


class ReferenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Reference

    note = factory.SubFactory(NoteFactory)
    target_note = factory.SubFactory(NoteFactory, notebook=factory.SelfAttribute('note.notebook'))


NoteReferenceFactory = ReferenceFactory
