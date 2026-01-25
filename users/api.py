from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.utils import extend_schema
from knox import views as knox_views
from knox.views import LoginView as KnoxLoginView
from rest_framework import serializers
from rest_framework.authentication import BasicAuthentication


class NoDialogBasicAuthentication(BasicAuthentication):
    """
    BasicAuthentication that suppresses browser auth dialog.

    See: https://stackoverflow.com/a/20221330
    """

    def authenticate_header(self, request):
        return None


class NoDialogBasicAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = NoDialogBasicAuthentication
    name = 'basicAuth'

    def get_security_definition(self, auto_schema):
        return {'type': 'http', 'scheme': 'basic'}


class LoginResponseSerializer(serializers.Serializer):
    expiry = serializers.DateTimeField()
    token = serializers.CharField()


class EmptySerializer(serializers.Serializer):
    pass


@extend_schema(request=None, responses=LoginResponseSerializer)
class LoginView(KnoxLoginView):
    """
    Custom login view that uses Basic Authentication.

    Accepts HTTP Basic Authentication credentials to generate
    a Knox token for subsequent API requests.
    """

    authentication_classes = [NoDialogBasicAuthentication]


@extend_schema(request=None, responses=None)
class LogoutView(knox_views.LogoutView):
    pass


@extend_schema(request=None, responses=None)
class LogoutAllView(knox_views.LogoutAllView):
    pass
