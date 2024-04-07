from django.urls import path

from djsfc import Router

from . import views
from .views import answer, note, notebook


router = Router(__name__)
router.route_all('answer/', answer.router, name='answer')
router.route_all('note/', note.router, name='note')
router.route_all('notebook/', notebook.router, name='notebook')


urlpatterns = [
    path('notebooks/', views.NotebookListView.as_view(), name='notebook-list'),
    path('notebook/<uuid:notebook_id>/ask-me/', views.NotebookAskMeView.as_view(), name='notebook-ask-me'),
]
