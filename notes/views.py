from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from . import models
from .models import Note


class NotebookListView(LoginRequiredMixin, ListView):
    template_name = 'notebooks.html'
    context_object_name = 'notebooks'
    model = models.Notebook

    def get_queryset(self):
        return super().get_queryset().accessible_by_user(self.request.user)


class NotebookViewMixin:
    def dispatch(self, request, *args, notebook_id, **kwargs):
        self.notebook = get_object_or_404(
            models.Notebook.objects.accessible_by_user(self.request.user),
            id=notebook_id,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notebook'] = self.notebook
        return context


class NotebookDetailView(LoginRequiredMixin, NotebookViewMixin, DetailView):
    template_name = 'notebook.html'

    def get_object(self):
        return self.notebook

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notes'] = self.notebook.notes.all()
        return context


class NoteDetailView(LoginRequiredMixin, DetailView):
    template_name = 'note.html'
    context_object_name = 'note'

    def get_queryset(self):
        return Note.objects.accessible_by_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['references'] = self.object.references.select_related('target_note')
        return context
