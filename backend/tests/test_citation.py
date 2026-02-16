from services.citation import Citation, build_citations, format_context_for_llm


class TestCitation:
    def test_to_dict(self):
        c = Citation(
            number=1,
            document_id="doc-123",
            filename="contract.pdf",
            content="The parties agree to the following terms.",
            page_number=5,
            section="Section 2.1",
            chunk_id="chunk-456",
        )
        d = c.to_dict()
        assert d["number"] == 1
        assert d["filename"] == "contract.pdf"
        assert d["page_number"] == 5
        assert d["section"] == "Section 2.1"

    def test_format_for_llm_full(self):
        c = Citation(
            number=1,
            document_id="doc-123",
            filename="contract.pdf",
            content="Some legal text here.",
            page_number=3,
            section="Article IV",
            chunk_id="chunk-456",
        )
        formatted = c.format_for_llm()
        assert "[1]" in formatted
        assert "contract.pdf" in formatted
        assert "Article IV" in formatted
        assert "page 3" in formatted
        assert "Some legal text here." in formatted

    def test_format_for_llm_no_section_or_page(self):
        c = Citation(
            number=2,
            document_id="doc-789",
            filename="memo.docx",
            content="Text content.",
            page_number=None,
            section=None,
            chunk_id="chunk-abc",
        )
        formatted = c.format_for_llm()
        assert "[2]" in formatted
        assert "memo.docx" in formatted
        assert "Text content." in formatted


class TestBuildCitations:
    def test_builds_numbered_citations(self):
        chunks = [
            {
                "chunk_id": "c1",
                "document_id": "d1",
                "filename": "file1.pdf",
                "content": "Content 1",
                "page_number": 1,
                "section": None,
            },
            {
                "chunk_id": "c2",
                "document_id": "d1",
                "filename": "file1.pdf",
                "content": "Content 2",
                "page_number": 2,
                "section": "Section 3",
            },
        ]
        citations = build_citations(chunks)
        assert len(citations) == 2
        assert citations[0].number == 1
        assert citations[1].number == 2
        assert citations[1].section == "Section 3"

    def test_empty_chunks(self):
        citations = build_citations([])
        assert citations == []


class TestFormatContextForLLM:
    def test_with_citations(self):
        citations = [
            Citation(1, "d1", "file.pdf", "Legal text.", 1, None, "c1"),
            Citation(2, "d1", "file.pdf", "More text.", 2, "Section 5", "c2"),
        ]
        context = format_context_for_llm(citations)
        assert "relevant excerpts" in context
        assert "[1]" in context
        assert "[2]" in context

    def test_no_citations(self):
        context = format_context_for_llm([])
        assert "No relevant documents found" in context
