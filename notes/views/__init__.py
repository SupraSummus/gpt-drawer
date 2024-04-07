from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, TemplateView
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
