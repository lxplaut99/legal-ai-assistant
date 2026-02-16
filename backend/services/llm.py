import anthropic

from config import settings

_client: anthropic.AsyncAnthropic | None = None

SYSTEM_PROMPT = """You are a legal AI assistant that helps lawyers with document analysis, drafting, research, and general legal tasks. Follow these rules:

1. When document excerpts are provided, ground your answers in them and cite sources using [N] notation (e.g., [1], [2]). Use exact text when quoting.

2. When NO document excerpts are provided, or the user's request is a general task (drafting, explaining concepts, brainstorming), respond helpfully using your legal knowledge. You do NOT need citations for general tasks.

3. Be precise and use legal terminology appropriately. Lawyers are your audience.

4. Structure your response clearly with paragraphs. For complex answers, use headings or bullet points.

5. For drafting tasks (contracts, letters, memos, clauses), produce complete, professional, ready-to-use text. Include standard legal provisions appropriate for the document type. Use placeholders like [PARTY NAME], [DATE], [JURISDICTION] where specific details are unknown.

6. If multiple sources provide conflicting information, note the discrepancy and cite both sources.

7. You are an AI assistant, not a lawyer. Your responses assist licensed attorneys and do not constitute legal advice."""


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


def _build_augmented_message(user_message: str, context: str, has_documents: bool) -> str:
    if has_documents:
        return f"""{context}

---

User request: {user_message}

If the request is about the documents above, ground your answer in the excerpts and cite sources using [N] notation. If the request is a general task (drafting, explanation, etc.), respond helpfully and reference the documents where relevant."""
    else:
        return user_message


async def chat_with_context(
    user_message: str,
    context: str,
    conversation_history: list[dict] | None = None,
    has_documents: bool = False,
) -> str:
    """Send a message to Claude with optional document context."""
    client = _get_client()

    messages = []

    if conversation_history:
        for msg in conversation_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": _build_augmented_message(user_message, context, has_documents)})

    response = await client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    return response.content[0].text


async def stream_chat_with_context(
    user_message: str,
    context: str,
    conversation_history: list[dict] | None = None,
    has_documents: bool = False,
):
    """Stream a response from Claude with optional document context."""
    client = _get_client()

    messages = []

    if conversation_history:
        for msg in conversation_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": _build_augmented_message(user_message, context, has_documents)})

    async with client.messages.stream(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            yield text
