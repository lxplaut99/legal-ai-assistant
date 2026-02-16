import os
import tempfile

import pytest

from services.document_processor import (
    TextChunk,
    _detect_section_header,
    _get_overlap,
    chunk_text,
    parse_and_chunk,
    parse_pdf,
)


class TestSectionHeaderDetection:
    def test_section_numbered(self):
        assert _detect_section_header("Section 1.2 Definitions") == "Section 1.2 Definitions"

    def test_article_roman(self):
        assert _detect_section_header("ARTICLE III REPRESENTATIONS") == "ARTICLE III REPRESENTATIONS"

    def test_numbered_heading(self):
        result = _detect_section_header("1.2 Governing Law")
        assert result is not None
        assert "Governing Law" in result

    def test_no_header(self):
        assert _detect_section_header("This is a regular paragraph of text.") is None

    def test_empty_string(self):
        assert _detect_section_header("") is None


class TestGetOverlap:
    def test_short_text(self):
        result = _get_overlap("hello world", 100)
        assert result == "hello world"

    def test_overlap_extraction(self):
        text = " ".join(f"word{i}" for i in range(100))
        result = _get_overlap(text, 50)
        words = result.split()
        # Should get ~37 words (50 * 0.75)
        assert len(words) == 37

    def test_zero_overlap(self):
        result = _get_overlap("hello world", 0)
        assert result == ""


class TestChunkText:
    def test_single_page_small(self):
        pages = [{"text": "Hello world. This is a test.", "page_number": 1}]
        chunks = chunk_text(pages, target_tokens=1000, overlap_tokens=10)
        assert len(chunks) == 1
        assert "Hello world" in chunks[0].content

    def test_multiple_chunks(self):
        # Create text that will span multiple chunks
        long_text = "\n\n".join([f"Paragraph {i}. " + "word " * 100 for i in range(20)])
        pages = [{"text": long_text, "page_number": 1}]
        chunks = chunk_text(pages, target_tokens=100, overlap_tokens=10)
        assert len(chunks) > 1
        # All chunks should have content
        for chunk in chunks:
            assert len(chunk.content) > 0
            assert chunk.token_count > 0

    def test_preserves_page_numbers(self):
        pages = [
            {"text": "Page one content", "page_number": 1},
            {"text": "Page two content", "page_number": 2},
        ]
        chunks = chunk_text(pages, target_tokens=1000, overlap_tokens=10)
        assert len(chunks) >= 1
        assert chunks[0].page_number is not None

    def test_detects_sections(self):
        pages = [{"text": "Section 1.2 Indemnification\n\nThe parties agree to indemnify each other.", "page_number": 5}]
        chunks = chunk_text(pages, target_tokens=1000, overlap_tokens=10)
        assert chunks[0].section is not None
        assert "Indemnification" in chunks[0].section


class TestParseAndChunk:
    def test_unsupported_type(self):
        with pytest.raises(ValueError, match="Unsupported file type"):
            parse_and_chunk("/tmp/test.txt", "txt")

    def test_pdf_nonexistent_file(self):
        with pytest.raises(Exception):
            parse_and_chunk("/tmp/nonexistent.pdf", "pdf")
