import openai
from django.conf import settings


openai_client = openai.Client(
    api_key=settings.OPENAI_API_KEY,
)


def generate_embedding(text):
    response = openai_client.embeddings.create(
        input=text,
        model='text-embedding-3-large',
    )
    embedding = response.data[0].embedding
    assert len(embedding) == 3072
    return embedding
