from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from . import models


class NoteBookListView(LoginRequiredMixin, ListView):
    template_name = 'notebooks.html'
    context_object_name = 'notebooks'
    model = models.NoteBook

    def get_queryset(self):
        return super().get_queryset().filter(user_permissions__user=self.request.user)


class NoteBookViewMixin:
    def __init__(self, *args, notebook_id, **kwargs):
        super().__init__(*args, **kwargs)
        self.notebook = get_object_or_404(
            models.NoteBook,
            id=notebook_id,
            user_permissions__user=self.request.user,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notebook'] = self.notebook
        return context


class NoteBookDetailView(LoginRequiredMixin, NoteBookViewMixin, DetailView):
    template_name = 'notebook.html'


class NoteDetailView(LoginRequiredMixin, NoteBookViewMixin, DetailView):
    template_name = 'note.html'
    context_object_name = 'note'

    def get_queryset(self):
        return self.notebook.notes.all()
