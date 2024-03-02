from unittest import mock

import numpy
import pytest
from django_q.conf import Conf
from openai.types.chat import ChatCompletionMessage
from openai.types.chat.chat_completion import ChatCompletion, Choice
from openai.types.create_embedding_response import CreateEmbeddingResponse, Usage
from openai.types.embedding import Embedding

from notes.models import ReferenceState
from notes.openai import openai_client
from notes.tasks import generate_references


@pytest.mark.django_db
def test_generate_references(note, monkeypatch):
    monkeypatch.setattr(Conf, 'SYNC', True)

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
            ),
        ],
        id='cmpl-123',
        created=1630000000,
        model='gpt-4-turbo-preview',
        object='chat.completion',
    )
    monkeypatch.setattr(openai_client.chat.completions, 'create', completions_mock)

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

    generate_references(note.id)

    note.refresh_from_db()

    reference = note.references.first()
    assert reference.state == ReferenceState.ACTIVE
    assert numpy.allclose(reference.embedding, [0.1] * 3072)
