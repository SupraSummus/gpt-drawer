from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.edit import CreateView, UpdateView

from . import models
from .models import Note, NoteReference


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


# ### Notes ###

class NoteViewMixin(LoginRequiredMixin, ContextMixin):
    def dispatch(self, request, *args, note_id, **kwargs):
        self.note = get_object_or_404(
            Note.objects.accessible_by_user(self.request.user),
            id=note_id,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['note'] = self.note
        return context


class GETMixin(ContextMixin, TemplateResponseMixin):
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())


class NoteDetailView(NoteViewMixin, GETMixin, View):
    def get_template_names(self):
        if self.request.htmx:
            template_name = 'components/note.html'
        else:
            template_name = 'note.html'
        return [template_name]

    def delete(self, request, *args, **kwargs):
        self.note.delete()
        return HttpResponse(status=200, content='')


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ('title', 'content')


class NoteEditView(NoteViewMixin, UpdateView):
    template_name = 'components/note_edit.html'
    form_class = NoteForm

    def get_object(self):
        return self.note


# ### Note references ###


class NoteReferenceViewMixin(LoginRequiredMixin, TemplateResponseMixin):
    def dispatch(self, request, *args, note_reference_id, **kwargs):
        self.note_reference = get_object_or_404(
            NoteReference.objects.accessible_by_user(self.request.user),
            id=note_reference_id,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['note_reference'] = self.note_reference
        return context


class NoteReferenceView(NoteReferenceViewMixin, GETMixin, View):
    template_name = 'components/note_reference.html'

    def delete(self, request, *args, **kwargs):
        self.note_reference.delete()
        return HttpResponse(status=200, content='')


class NoteReferenceForm(forms.ModelForm):
    class Meta:
        model = NoteReference
        fields = ('question', 'target_note')

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        notebook_id = self.instance.note.notebook_id
        self.fields['target_note'].queryset = Note.objects.accessible_by_user(
            user,
        ).filter(
            notebook_id=notebook_id,
        )


class NoteReferenceEditView(NoteReferenceViewMixin, UpdateView):
    template_name = 'components/note_reference_edit.html'
    form_class = NoteReferenceForm

    def get_object(self):
        return self.note_reference

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class NoteReferenceCreateView(NoteViewMixin, CreateView):
    model = NoteReference
    form_class = NoteReferenceForm
    template_name = 'components/note_reference_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['instance'] = NoteReference(note=self.note)
        return kwargs
