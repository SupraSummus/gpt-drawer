from rest_framework import serializers

from . import models


class NoteBookSerializer(serializers.ModelSerializer):
    _detail_url = serializers.HyperlinkedIdentityField(
        view_name='api:notebook-detail',
        lookup_field='pk',
    )

    class Meta:
        model = models.NoteBook
        fields = (
            '_detail_url',
            'id',
            'title',
        )
