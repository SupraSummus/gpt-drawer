from knox import views as knox_views
from knox.views import LoginView as KnoxLoginView
from rest_framework.authentication import BasicAuthentication


class NoDialogBasicAuthentication(BasicAuthentication):
    """
    BasicAuthentication that suppresses browser auth dialog.

    See: https://stackoverflow.com/a/20221330
    """

    def authenticate_header(self, request):
        return None


class LoginView(KnoxLoginView):
    """
    Custom login view that uses Basic Authentication.

    Accepts HTTP Basic Authentication credentials to generate
    a Knox token for subsequent API requests.
    """

    authentication_classes = [NoDialogBasicAuthentication]


LogoutView = knox_views.LogoutView
LogoutAllView = knox_views.LogoutAllView
