from django.urls import path

from . import views


urlpatterns = [
    path('notebooks/', views.NotebookListView.as_view(), name='notebook-list'),
    path('notebook/<uuid:notebook_id>/', views.NotebookDetailView.as_view(), name='notebook-detail'),
    path('note/<uuid:note_id>/', views.NoteDetailView.as_view(), name='note-detail'),
    path('note/<uuid:note_id>/edit/', views.NoteEditView.as_view(), name='note-edit'),
    path(
        'note/<uuid:note_id>/create-note-reference/',
        views.NoteReferenceCreateView.as_view(),
        name='note-reference-create',
    ),
    path('note-reference/<uuid:note_reference_id>/', views.NoteReferenceView.as_view(), name='note-reference'),
    path(
        'note-reference/<uuid:note_reference_id>/edit/',
        views.NoteReferenceEditView.as_view(),
        name='note-reference-edit',
    ),
]
