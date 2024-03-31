from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.base import ContextMixin

from .. import models
from ..models import NoteReference


class NotebookListView(LoginRequiredMixin, ListView):
    template_name = 'notebooks.html'
    context_object_name = 'notebooks'
    model = models.Notebook

    def get_queryset(self):
        return super().get_queryset().accessible_by_user(self.request.user)


class NotebookViewMixin(LoginRequiredMixin, ContextMixin):
    def dispatch(self, request, *args, notebook_id, **kwargs):
        self.notebook = get_object_or_404(
            models.Notebook.objects.accessible_by_user(self.request.user),
            id=notebook_id,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notebook'] = self.notebook
        context['notebook_id'] = self.notebook.id
        return context


class NotebookDetailView(NotebookViewMixin, DetailView):
    template_name = 'notebook.html'

    def get_object(self):
        return self.notebook

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notes'] = self.notebook.notes.all()
        return context


class NotebookAskMeView(NotebookViewMixin, TemplateView):
    template_name = 'components/notebook_ask_me.html'

    def get(self, request, *args, **kwargs):
        unanswered_question = NoteReference.objects.filter(
            note__notebook=self.notebook,
            target_note__isnull=True,
        ).order_by('?').first()
        if unanswered_question:
            return redirect(reverse(
                'notes:answer:root',
                kwargs={'note_reference_id': unanswered_question.id},
            ))
        return super().get(request, *args, **kwargs)


class NoteSelectView(NotebookViewMixin, TemplateView):
    """Return an element where user can select a note to use in a form."""
    template_name = 'components/note_select.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_name'] = self.request.GET.get('field_name')
        context['note_id'] = self.request.GET.get('note_id', '')
        context['notes'] = self.notebook.notes.all()[0:10]
        return context


class NoteSearchView(NotebookViewMixin, TemplateView):
    """Return matching notes. User can select one to use in a form."""
    template_name = 'components/note_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_name'] = self.request.GET.get('field_name')
        context['notes'] = self.notebook.notes.autocomplete_search(self.request.GET.get('q'))[0:10]
        return context


class NoteSelectedView(NotebookViewMixin, TemplateView):
    """Return element representing selected note for use in a form."""
    template_name = 'components/note_selected.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_name'] = self.request.GET.get('field_name')
        note_id_str = self.request.GET.get('note_id', '')
        if not note_id_str:
            context['note'] = None
        else:
            context['note'] = self.notebook.notes.filter(id=note_id_str).first()
        return context
