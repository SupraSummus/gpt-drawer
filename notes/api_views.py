from rest_framework.viewsets import ModelViewSet

from . import models, serializers


class NoteBookViewSet(ModelViewSet):
    queryset = models.NoteBook.objects.all()
    serializer_class = serializers.NoteBookSerializer
    search_fields = ('title',)

    def get_queryset(self):
        return self.queryset.filter(user_permissions__user=self.request.user)
