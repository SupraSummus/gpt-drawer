from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.edit import CreateView, FormView, UpdateView

from .. import models
from ..models import Note, NoteReference
from ..widgets import NoteChoiceWidget


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
    def get_template_names(self):
        if self.request.htmx:
            template_name = 'components/note_reference.html'
        else:
            template_name = 'note_reference.html'
        return [template_name]

    def delete(self, request, *args, **kwargs):
        self.note_reference.delete()
        return HttpResponse(status=200, content='')


class NoteReferenceForm(forms.ModelForm):
    target_note = forms.ModelChoiceField(
        queryset=Note.objects.none(),
        required=False,
    )

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
        self.fields['target_note'].widget = NoteChoiceWidget(
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


class NoteReferenceAnswerForm(forms.Form):
    answer = Note._meta.get_field('content').formfield(
        required=True,
        label=_('Answer'),
    )


class NoteReferenceAnswerView(NoteReferenceViewMixin, FormView):
    template_name = 'components/note_reference_answer.html'
    form_class = NoteReferenceAnswerForm

    def form_valid(self, form):
        note = Note.objects.create(
            notebook=self.note_reference.note.notebook,
            content=form.cleaned_data['answer'],
        )
        self.note_reference.target_note = note
        self.note_reference.save(update_fields=('target_note',))
        return redirect(self.note_reference)
