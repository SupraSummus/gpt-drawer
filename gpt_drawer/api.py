from rest_framework.routers import DefaultRouter

from notes import api_views as notes_api_views


router = DefaultRouter()
router.register('notebooks', notes_api_views.NoteBookViewSet, basename='notebook')
