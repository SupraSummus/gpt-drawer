import pytest

from .factories import NotebookFactory, NoteFactory


@pytest.fixture
def notebook(request):
    return NotebookFactory(
        **getattr(request, 'param', {}),
    )


@pytest.fixture
def note(request, notebook):
    return NoteFactory(
        notebook=notebook,
        **getattr(request, 'param', {}),
    )


@pytest.fixture
def other_note(request, notebook):
    return NoteFactory(
        notebook=notebook,
        **getattr(request, 'param', {}),
    )


@pytest.fixture
def other_notebook(request):
    return NotebookFactory(
        **getattr(request, 'param', {}),
    )


@pytest.fixture
def other_notebook_note(request, other_notebook):
    return NoteFactory(
        notebook=other_notebook,
        **getattr(request, 'param', {}),
    )
