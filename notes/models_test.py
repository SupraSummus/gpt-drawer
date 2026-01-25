import factory
import pytest

from .models import Alias, Note, Notebook, NotebookUserPermission, Reference


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


@pytest.fixture
def notebook(request):
    return NotebookFactory(**getattr(request, 'param', {}))


@pytest.fixture
def notebook_user_permission(request, notebook, user):
    return NotebookUserPermissionFactory(
        notebook=notebook,
        user=user,
        **getattr(request, 'param', {}),
    )


@pytest.fixture
def note(request, notebook):
    return NoteFactory(notebook=notebook, **getattr(request, 'param', {}))


@pytest.fixture
def note_reference(request, note, other_note):
    return NoteReferenceFactory(
        note=note,
        target_note=other_note,
        **getattr(request, 'param', {}),
    )


@pytest.fixture
def other_note(request, notebook):
    return NoteFactory(notebook=notebook, **getattr(request, 'param', {}))


@pytest.fixture
def other_notebook(request):
    return NotebookFactory(**getattr(request, 'param', {}))


@pytest.fixture
def other_notebook_note(request, other_notebook):
    return NoteFactory(notebook=other_notebook, **getattr(request, 'param', {}))
