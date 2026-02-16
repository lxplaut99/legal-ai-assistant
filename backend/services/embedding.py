from openai import AsyncOpenAI

from config import settings

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts using OpenAI API."""
    if not texts:
        return []

    client = _get_client()
    response = await client.embeddings.create(
        model=settings.embedding_model,
        input=texts,
        dimensions=settings.embedding_dimensions,
    )
    return [item.embedding for item in response.data]


async def generate_embedding(text: str) -> list[float]:
    """Generate embedding for a single text."""
    result = await generate_embeddings([text])
    return result[0]
