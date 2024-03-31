from django.urls import path

from djsfc import Router

from . import views
from .views import answer, note


router = Router(__name__)
router.route_all('answer/', answer.router, name='answer')
router.route_all('note/', note.router, name='note')


urlpatterns = [
    path('notebooks/', views.NotebookListView.as_view(), name='notebook-list'),
    path('notebook/<uuid:notebook_id>/', views.NotebookDetailView.as_view(), name='notebook-detail'),
    path('notebook/<uuid:notebook_id>/ask-me/', views.NotebookAskMeView.as_view(), name='notebook-ask-me'),
    path('notebook/<uuid:notebook_id>/note-select/', views.NoteSelectView.as_view(), name='note-select'),
    path('notebook/<uuid:notebook_id>/note-search/', views.NoteSearchView.as_view(), name='note-search'),
    path('notebook/<uuid:notebook_id>/note-selected/', views.NoteSelectedView.as_view(), name='note-selected'),
]
