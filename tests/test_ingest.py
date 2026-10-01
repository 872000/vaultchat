"""Tests for document ingestion and chunking."""

import os
import tempfile

import pytest

from vaultchat.ingest import Chunk, chunk_text, clean_markdown, ingest, load_documents


def test_clean_markdown_headings_become_sentences():
    assert clean_markdown("## Undoing Things\nDo this.") == "Undoing Things.\nDo this."
    assert clean_markdown("# FAQ?\ntext") == "FAQ?\ntext"


def test_split_sentences_ignores_code_spans():
    from vaultchat.answer import split_sentences
    sents = split_sentences("Use `git restore filename` or `git checkout -- filename`. Then commit.")
    assert sents == ["Use `git restore filename` or `git checkout -- filename`.", "Then commit."]


def test_chunk_text_basic():
    words = " ".join(f"w{i}" for i in range(250))
    chunks = chunk_text("doc.md", words, chunk_size=100, overlap=20)
    assert len(chunks) == 3
    assert all(isinstance(c, Chunk) for c in chunks)
    assert chunks[0].index == 0
    assert chunks[1].index == 1
    # overlap: chunk 1 starts 20 words before chunk 0 ends
    assert chunks[1].text.split()[:20] == chunks[0].text.split()[-20:]


def test_chunk_text_short_document_is_single_chunk():
    chunks = chunk_text("doc.md", "hello world", chunk_size=100, overlap=20)
    assert len(chunks) == 1
    assert chunks[0].text == "hello world"


def test_chunk_text_invalid_args():
    with pytest.raises(ValueError):
        chunk_text("doc.md", "text", chunk_size=0)
    with pytest.raises(ValueError):
        chunk_text("doc.md", "text", chunk_size=100, overlap=100)


def test_chunk_id_format():
    c = Chunk(doc_name="notes.md", index=2, text="x")
    assert c.chunk_id == "notes.md#c2"


def test_load_documents_reads_supported_extensions(tmp_path):
    (tmp_path / "a.md").write_text("hello markdown")
    (tmp_path / "b.txt").write_text("hello text")
    (tmp_path / "c.pdf").write_text("ignored")
    docs = load_documents(str(tmp_path))
    assert [name for name, _ in docs] == ["a.md", "b.txt"]


def test_load_documents_missing_dir():
    with pytest.raises(FileNotFoundError):
        load_documents("/does/not/exist")


def test_ingest_bundled_docs():
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "docs")
    chunks = ingest(docs_dir)
    doc_names = {c.doc_name for c in chunks}
    assert len(doc_names) == 5
    assert len(chunks) > len(doc_names)  # chunking actually split documents
    assert all(c.text.strip() for c in chunks)
