from dataclasses import dataclass


@dataclass
class Citation:
    number: int
    document_id: str
    filename: str
    content: str
    page_number: int | None
    section: str | None
    chunk_id: str

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "document_id": self.document_id,
            "filename": self.filename,
            "content": self.content,
            "page_number": self.page_number,
            "section": self.section,
            "chunk_id": self.chunk_id,
        }

    def format_for_llm(self) -> str:
        """Format citation for inclusion in LLM context."""
        location = self.filename
        if self.section:
            location += f", {self.section}"
        if self.page_number:
            location += f", page {self.page_number}"
        return f"[{self.number}] ({location}):\n{self.content}"


def build_citations(retrieved_chunks: list[dict]) -> list[Citation]:
    """Convert retrieved chunks into numbered citations."""
    citations = []
    for i, chunk in enumerate(retrieved_chunks, start=1):
        citations.append(Citation(
            number=i,
            document_id=chunk["document_id"],
            filename=chunk["filename"],
            content=chunk["content"],
            page_number=chunk.get("page_number"),
            section=chunk.get("section"),
            chunk_id=chunk["chunk_id"],
        ))
    return citations


def format_context_for_llm(citations: list[Citation]) -> str:
    """Format all citations as context for the LLM prompt."""
    if not citations:
        return "No relevant documents found."
    parts = ["Here are the relevant excerpts from the uploaded documents:\n"]
    for citation in citations:
        parts.append(citation.format_for_llm())
    return "\n\n".join(parts)
