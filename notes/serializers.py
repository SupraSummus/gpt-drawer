from rest_framework import serializers
from rest_framework_nested.relations import NestedHyperlinkedIdentityField

from .models import Alias, Note, Notebook, NoteVersion, Reference


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
    title = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = Note
        fields = (
            '_detail_url',
            'id',
            'title',
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['title'] = instance.title
        return ret


class AliasSerializer(serializers.ModelSerializer):
    _detail_url = NestedHyperlinkedIdentityField(
        view_name='api:note-alias-detail',
        lookup_field='pk',
        parent_lookup_kwargs={
            'note_pk': 'note__pk',
        },
    )

    class Meta:
        model = Alias
        fields = (
            '_detail_url',
            'id',
            'title',
        )


class NoteVersionSerializer(serializers.ModelSerializer):
    note_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = NoteVersion
        fields = (
            'note_id',
            'created_at',
            'is_active',
            'title',
            'content',
        )
        read_only_fields = fields


class ReferenceSerializer(serializers.ModelSerializer):
    _detail_url = NestedHyperlinkedIdentityField(
        view_name='api:note-reference-detail',
        lookup_field='pk',
        parent_lookup_kwargs={
            'note_pk': 'note__pk',
        },
    )
    target_note = NoteShortSerializer(read_only=True)
    target_note_id = PrimaryKeyRelatedAccessibleByUserField(
        queryset=Note.objects.all(),
        source='target_note',
        write_only=True,
    )

    class Meta:
        model = Reference
        fields = (
            '_detail_url',
            'id',
            'target_note',
            'target_note_id',
        )


class NoteSerializer(NoteShortSerializer):
    _versions_url = serializers.HyperlinkedIdentityField(
        view_name='api:note-version-list',
        lookup_field='pk',
        lookup_url_kwarg='note_pk',
    )
    _aliases_url = serializers.HyperlinkedIdentityField(
        view_name='api:note-alias-list',
        lookup_field='pk',
        lookup_url_kwarg='note_pk',
    )
    _references_url = serializers.HyperlinkedIdentityField(
        view_name='api:note-reference-list',
        lookup_field='pk',
        lookup_url_kwarg='note_pk',
    )
    notebook_id = PrimaryKeyRelatedAccessibleByUserField(
        queryset=Notebook.objects.all(),
        source='notebook',
    )
    content = serializers.CharField(required=False, allow_blank=True, default='')
    aliases = AliasSerializer(many=True)
    references = ReferenceSerializer(many=True)

    class Meta:
        model = Note
        fields = (
            *NoteShortSerializer.Meta.fields,
            '_versions_url',
            '_aliases_url',
            '_references_url',
            'notebook_id',
            'content',
            'aliases',
            'references',
        )

    def create(self, validated_data):
        aliases_data = validated_data.pop('aliases')
        references_data = validated_data.pop('references')
        title = validated_data.pop('title', '')
        content = validated_data.pop('content', '')
        note = Note.objects.create(**validated_data)
        note.create_version(title=title, content=content)
        note.set_aliases([Alias(**alias_data, note=note) for alias_data in aliases_data])
        note.set_references([Reference(**reference_data, note=note) for reference_data in references_data])
        return note

    def update(self, instance, validated_data):
        aliases_data = validated_data.pop('aliases', None)
        references_data = validated_data.pop('references', None)
        title = validated_data.pop('title', None)
        content = validated_data.pop('content', None)

        # Update note fields (like notebook)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Create new version if title or content changed
        if title is not None or content is not None:
            new_title = title if title is not None else instance.title
            new_content = content if content is not None else instance.content
            instance.create_version(title=new_title, content=new_content)

        if aliases_data is not None:
            instance.set_aliases([Alias(**alias_data, note=instance) for alias_data in aliases_data])
        if references_data is not None:
            instance.set_references([Reference(**reference_data, note=instance) for reference_data in references_data])
        return instance

    def validate(self, data):
        # we check if references are in the same notebook
        notebook = data.get('notebook') or self.instance.notebook
        for reference_data in data.get('references', []):
            if reference_data['target_note'].notebook != notebook:
                raise serializers.ValidationError({
                    'references': 'References must be in the same notebook',
                })

        return data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['content'] = instance.content
        return ret
