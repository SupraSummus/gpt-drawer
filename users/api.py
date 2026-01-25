from knox import views as knox_views
from knox.views import LoginView as KnoxLoginView
from rest_framework.authentication import BasicAuthentication


class LoginView(KnoxLoginView):
    """
    Custom login view that uses Basic Authentication.

    Accepts HTTP Basic Authentication credentials to generate
    a Knox token for subsequent API requests.
    """

    authentication_classes = [BasicAuthentication]


LogoutView = knox_views.LogoutView
LogoutAllView = knox_views.LogoutAllView
