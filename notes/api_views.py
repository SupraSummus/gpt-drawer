import django_filters
from django.db.models import Q
from rest_framework.viewsets import ModelViewSet

from .models import Note, NoteBook
from .serializers import NoteBookSerializer, NoteSerializer


class NoteBookViewSet(ModelViewSet):
    queryset = NoteBook.objects.all()
    serializer_class = NoteBookSerializer

    def get_queryset(self):
        return self.queryset.accessible_by_user(self.request.user)


class ModelChoiceAccessibleByUserFilter(django_filters.ModelChoiceFilter):
    def get_queryset(self, request):
        return super().get_queryset(request).accessible_by_user(request.user)


class NoteFiterSet(django_filters.FilterSet):
    notebook = ModelChoiceAccessibleByUserFilter(queryset=NoteBook.objects.all())
    search = django_filters.CharFilter(method='search_filter')

    class Meta:
        model = Note
        fields = ('notebook',)

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
