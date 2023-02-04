from rest_framework import serializers

from .models import Note, NoteBook


class NoteBookSerializer(serializers.ModelSerializer):
    _detail_url = serializers.HyperlinkedIdentityField(
        view_name='api:notebook-detail',
        lookup_field='pk',
    )

    class Meta:
        model = NoteBook
        fields = (
            '_detail_url',
            'id',
            'title',
        )


class PrimaryKeyRelatedAccessibleByUserField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        return super().get_queryset().accessible_by_user(self.context['request'].user)


class NoteSerializer(serializers.ModelSerializer):
    _detail_url = serializers.HyperlinkedIdentityField(
        view_name='api:note-detail',
        lookup_field='pk',
    )
    notebook_id = PrimaryKeyRelatedAccessibleByUserField(
        queryset=NoteBook.objects.all(),
        source='notebook',
    )

    class Meta:
        model = Note
        fields = (
            '_detail_url',
            'id',
            'notebook_id',
            'title',
            'content',
        )
