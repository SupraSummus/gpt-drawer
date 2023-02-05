from rest_framework import serializers

from .models import Alias, Note, Notebook, Reference


class NotebookSerializer(serializers.ModelSerializer):
    _detail_url = serializers.HyperlinkedIdentityField(
        view_name='api:notebook-detail',
        lookup_field='pk',
    )

    class Meta:
        model = Notebook
        fields = (
            '_detail_url',
            'id',
            'title',
        )


class PrimaryKeyRelatedAccessibleByUserField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        return super().get_queryset().accessible_by_user(self.context['request'].user)


class NoteShortSerializer(serializers.ModelSerializer):
    _detail_url = serializers.HyperlinkedIdentityField(
        view_name='api:note-detail',
        lookup_field='pk',
    )

    class Meta:
        model = Note
        fields = (
            '_detail_url',
            'id',
            'title',
        )


class AliasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alias
        fields = (
            'id',
            'title',
        )


class ReferenceSerializer(serializers.ModelSerializer):
    target_note = NoteShortSerializer(read_only=True)
    target_note_id = PrimaryKeyRelatedAccessibleByUserField(
        queryset=Note.objects.all(),
        source='target_note',
        write_only=True,
    )

    class Meta:
        model = Reference
        fields = (
            'id',
            'target_note',
            'target_note_id',
        )


class NoteSerializer(NoteShortSerializer):
    notebook_id = PrimaryKeyRelatedAccessibleByUserField(
        queryset=Notebook.objects.all(),
        source='notebook',
    )
    aliases = AliasSerializer(many=True)
    references = ReferenceSerializer(many=True)

    class Meta:
        model = Note
        fields = (
            *NoteShortSerializer.Meta.fields,
            'notebook_id',
            'content',
            'aliases',
            'references',
        )

    def create(self, validated_data):
        aliases_data = validated_data.pop('aliases')
        references_data = validated_data.pop('references')
        note = super().create(validated_data)
        note.set_aliases([Alias(**alias_data, note=note) for alias_data in aliases_data])
        note.set_references([Reference(**reference_data, note=note) for reference_data in references_data])
        return note

    def update(self, instance, validated_data):
        aliases_data = validated_data.pop('aliases', None)
        references_data = validated_data.pop('references', None)
        note = super().update(instance, validated_data)
        if aliases_data is not None:
            note.set_aliases([Alias(**alias_data, note=note) for alias_data in aliases_data])
        if references_data is not None:
            note.set_references([Reference(**reference_data, note=note) for reference_data in references_data])
        return note

    def validate(self, data):
        # we check if references are in the same notebook
        notebook = data.get('notebook') or self.instance.notebook
        for reference_data in data.get('references', []):
            if reference_data['target_note'].notebook != notebook:
                raise serializers.ValidationError({
                    'references': 'References must be in the same notebook',
                })

        return data
