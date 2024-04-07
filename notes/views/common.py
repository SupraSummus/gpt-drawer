from django.shortcuts import get_object_or_404

from ..models import Note, Notebook


def get_notebook(request, notebook_id):
    return get_object_or_404(
        Notebook.objects.accessible_by_user(request.user),
        id=notebook_id,
    )


def get_note(request, note_id):
    return get_object_or_404(
        Note.objects.accessible_by_user(request.user),
        id=note_id,
    )
