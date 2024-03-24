from django.urls import path

from djsfc import Router

from . import node_reference_answer, views


router = Router()
router.route_all('answer/', node_reference_answer.router, name='answer')


urlpatterns = [
    path('notebooks/', views.NotebookListView.as_view(), name='notebook-list'),
    path('notebook/<uuid:notebook_id>/', views.NotebookDetailView.as_view(), name='notebook-detail'),
    path('notebook/<uuid:notebook_id>/ask-me/', views.NotebookAskMeView.as_view(), name='notebook-ask-me'),
    path('notebook/<uuid:notebook_id>/note-select/', views.NoteSelectView.as_view(), name='note-select'),
    path('notebook/<uuid:notebook_id>/note-search/', views.NoteSearchView.as_view(), name='note-search'),
    path('notebook/<uuid:notebook_id>/note-selected/', views.NoteSelectedView.as_view(), name='note-selected'),
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
    path(
        'note-reference/<uuid:note_reference_id>/answer/',
        views.NoteReferenceAnswerView.as_view(),
        name='note-reference-answer',
    ),
]
