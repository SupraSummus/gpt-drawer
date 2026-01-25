import factory
import pytest

from .models import Alias, Note, Notebook, NotebookUserPermission, NoteVersion, Reference


class NotebookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notebook


class NotebookUserPermissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NotebookUserPermission


class NoteVersionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NoteVersion

    title = factory.Sequence(lambda n: f'Test note {n}')
    content = ''
    is_active = True


_note_counter = 0


class NoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Note
        skip_postgeneration_save = True

    notebook = factory.SubFactory(NotebookFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        global _note_counter
        _note_counter += 1
        title = kwargs.pop('title', f'Test note {_note_counter}')
        content = kwargs.pop('content', '')
        note = super()._create(model_class, *args, **kwargs)
        NoteVersion.objects.create(note=note, title=title, content=content, is_active=True)
        return note


class AliasFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Alias

    title = factory.Sequence(lambda n: f'Test alias {n}')


class ReferenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Reference

    note = factory.SubFactory(NoteFactory)
    target_note = factory.SubFactory(NoteFactory, notebook=factory.SelfAttribute('..note.notebook'))


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
