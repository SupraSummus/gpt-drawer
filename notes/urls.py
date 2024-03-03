from django.urls import path

from . import views


urlpatterns = [
    path('notebooks/', views.NotebookListView.as_view(), name='notebook-list'),
    path('notebook/<uuid:notebook_id>/', views.NotebookDetailView.as_view(), name='notebook-detail'),
    path('note/<uuid:pk>/', views.NoteDetailView.as_view(), name='note-detail'),
]
