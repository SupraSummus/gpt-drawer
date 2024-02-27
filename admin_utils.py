from urllib.parse import urlparse

from django.urls import resolve


def get_autocomplete_object_id(request, model_class, field_name):
    """
    Determine if a request is an autocomplete request and retrieve a model instance id that is being edited.

    Parameters:
    request (django.http.HttpRequest): The current HTTP request.
    model_class + field_name: The model field that is being autocompleted.

    Returns an instance id of the specified Django model if this is indeed and autocomplete request.
    Otherwise, None.
    """
    model_name = model_class._meta.model_name
    app_label = model_class._meta.app_label

    if (
        is_autocomplete_request(request) and
        request.GET.get('app_label') == app_label and
        request.GET.get('model_name') == model_name and
        request.GET.get('field_name') == field_name
    ):
        referer = request.META.get('HTTP_REFERER')
        referer_path = urlparse(referer).path
        referer_match = resolve(referer_path)
        object_id = referer_match.kwargs.get('object_id')
        return object_id

    return None


def is_autocomplete_request(request):
    """
    Determine if a request is an autocomplete request.

    Parameters:
    request (django.http.HttpRequest): The current HTTP request.

    Returns True if this is indeed and autocomplete request. Otherwise, False.
    """
    return request.resolver_match.view_name == 'admin:autocomplete'
