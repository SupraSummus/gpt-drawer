from django.urls import include, path
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

from notes import api_views as notes_api_views


router = DefaultRouter()
router.register('notebooks', notes_api_views.NotebookViewSet, basename='notebook')
router.register('notes', notes_api_views.NoteViewSet, basename='note')

notes_router = NestedDefaultRouter(router, 'notes', lookup='note')
notes_router.register('aliases', notes_api_views.AliasViewSet, basename='note-alias')
notes_router.register('references', notes_api_views.ReferenceViewSet, basename='note-reference')

urlpatterns = ([
    path(r'', include(router.urls)),
    path(r'', include(notes_router.urls)),
], 'api')
