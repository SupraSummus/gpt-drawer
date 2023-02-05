from django.urls import path

from . import views


urlpatterns = [
    path('notebooks/', views.NotebookListView.as_view(), name='notebook-list'),
    path('notebooks/<uuid:notebook_id>/', views.NotebookDetailView.as_view(), name='notebook-detail'),
    path('notebooks/<uuid:notebook_id>/notes/<uuid:note_id>/', views.NoteDetailView.as_view(), name='note-detail'),
]
