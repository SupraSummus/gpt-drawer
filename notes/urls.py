from django.urls import path

from . import views


urlpatterns = [
    path('notebooks/', views.NotebookListView.as_view(), name='notebook-list'),
    path('notebook/<uuid:notebook_id>/', views.NotebookDetailView.as_view(), name='notebook-detail'),
    path('note/<uuid:pk>/', views.NoteDetailView.as_view(), name='note-detail'),
    path('note/<uuid:pk>/edit/', views.NoteEditView.as_view(), name='note-edit'),
    path('note-reference/<uuid:pk>/', views.NoteReferenceView.as_view(), name='note-reference'),
    path('note-reference/<uuid:pk>/edit/', views.NoteReferenceEditView.as_view(), name='note-reference-edit'),
]
