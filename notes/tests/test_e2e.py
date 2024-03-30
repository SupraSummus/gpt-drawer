from unittest import mock

import numpy
import pytest
from django.urls import reverse
from django_q.conf import Conf
from openai.types.chat import ChatCompletionMessage
from openai.types.chat.chat_completion import ChatCompletion, Choice
from openai.types.create_embedding_response import CreateEmbeddingResponse, Usage
from openai.types.embedding import Embedding

from notes.models import ReferenceState
from notes.openai import openai_client
from notes.tasks import generate_references


@pytest.fixture
def sync_tasks(monkeypatch):
    monkeypatch.setattr(Conf, 'SYNC', True)


@pytest.fixture
def chat_completion_mock(monkeypatch):
    completions_mock = mock.Mock()
    completions_mock.return_value = ChatCompletion(
        choices=[
            Choice(
                message=ChatCompletionMessage(
                    role='assistant',
                    content='{"questions": ["first question", "second question"]}',
                ),
                finish_reason='stop',
                index=0,
                logprobs=None,
            ),
        ],
        id='cmpl-123',
        created=1630000000,
        model='gpt-4-turbo-preview',
        object='chat.completion',
    )
    monkeypatch.setattr(openai_client.chat.completions, 'create', completions_mock)
    return completions_mock


@pytest.fixture
def embedding_mock(monkeypatch):
    embedding_mock = mock.Mock()
    embedding_mock.return_value = CreateEmbeddingResponse(
        data=[
            Embedding(
                embedding=[0.1] * 3072,
                index=0,
                object='embedding',
            ),
        ],
        model='text-embedding-3-large',
        object='list',
        usage=Usage(
            prompt_tokens=123,
            total_tokens=456,
        ),
    )
    monkeypatch.setattr(openai_client.embeddings, 'create', embedding_mock)
    return embedding_mock


@pytest.mark.django_db
def test_generate_references(note, monkeypatch, sync_tasks, chat_completion_mock, embedding_mock):
    generate_references(note.id)

    note.refresh_from_db()

    reference = note.references.first()
    assert reference.state == ReferenceState.ACTIVE
    assert numpy.allclose(reference.embedding, [0.1] * 3072)


@pytest.mark.django_db
def test_note_reference_answer(
    user_client, note_reference, notebook_user_permission,
    sync_tasks,
    chat_completion_mock,
    embedding_mock,
):
    chat_completion_mock.return_value.choices[0].message.content = 'LLM generated title'
    response = user_client.post(
        reverse('notes:answer:create_answer', kwargs={'note_reference_id': note_reference.id}),
        data={'answer': 'This is an answer'},
    )
    assert response.status_code == 302
    note_reference.refresh_from_db()
    assert note_reference.target_note.content == 'This is an answer'
    assert note_reference.target_note.title == 'LLM generated title'
    assert chat_completion_mock.mock_calls[0].kwargs['messages'][-1] == {
        'role': 'user',
        'content': 'This is an answer',
    }
