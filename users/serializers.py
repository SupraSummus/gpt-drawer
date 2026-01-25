from rest_framework import serializers

from .models import User


class SessionSerializer(serializers.ModelSerializer):
    """Serializer for /users/me/ endpoint with auth method info."""

    auth_method = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'auth_method')
        read_only_fields = ('id', 'username', 'email', 'auth_method')

    def get_auth_method(self, obj):
        request = self.context.get('request')
        if not request or not request.successful_authenticator:
            return None
        return type(request.successful_authenticator).__name__
