import django_filters
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from rest_framework.viewsets import ModelViewSet

from .models import Note, Notebook
from .serializers import AliasSerializer, NotebookSerializer, NoteSerializer, ReferenceSerializer


class NotebookViewSet(ModelViewSet):
    queryset = Notebook.objects.all()
    serializer_class = NotebookSerializer

    def get_queryset(self):
        return self.queryset.accessible_by_user(self.request.user)


class ModelChoiceAccessibleByUserFilter(django_filters.ModelChoiceFilter):
    def get_queryset(self, request):
        return super().get_queryset(request).accessible_by_user(request.user)


class NoteFiterSet(django_filters.FilterSet):
    notebook_id = ModelChoiceAccessibleByUserFilter(
        queryset=Notebook.objects.all()
    )
    search = django_filters.CharFilter(
        method='search_filter',
        label=_('Search'),
    )

    class Meta:
        model = Note
        fields = ()

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(title__istartswith=value) |
            Q(aliases__title__istartswith=value)
        )


class NoteViewSet(ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    filterset_class = NoteFiterSet

    def get_queryset(self):
        return self.queryset.accessible_by_user(self.request.user)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        queryset = queryset.distinct()
        return queryset


class InNoteViewSetMixin:
    def dispatch(self, request, *args, note_pk, **kwargs):
        self.note = get_object_or_404(
            Note.objects.accessible_by_user(self.request.user),
            id=note_pk,
        )
        return super().dispatch(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(note=self.note)


class AliasViewSet(InNoteViewSetMixin, ModelViewSet):
    serializer_class = AliasSerializer

    def get_queryset(self):
        return self.note.aliases


class ReferenceViewSet(InNoteViewSetMixin, ModelViewSet):
    serializer_class = ReferenceSerializer

    def get_queryset(self):
        return self.note.references
