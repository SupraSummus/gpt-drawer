import openai
from django.conf import settings


openai_client = openai.Client(
    api_key=settings.OPENAI_API_KEY,
)
