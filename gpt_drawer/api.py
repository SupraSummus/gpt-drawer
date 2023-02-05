from rest_framework.routers import DefaultRouter

from notes import api_views as notes_api_views


router = DefaultRouter()
router.register('notebooks', notes_api_views.NotebookViewSet, basename='notebook')
router.register('notes', notes_api_views.NoteViewSet, basename='note')
