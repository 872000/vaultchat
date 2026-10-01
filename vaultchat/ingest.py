"""Document ingestion: read markdown/text files and split them into passages."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass


SUPPORTED_EXTENSIONS = {".md", ".markdown", ".txt"}


@dataclass
class Chunk:
    """A single passage of a document."""

    doc_name: str  # file name, e.g. "git-notes.md"
    index: int  # chunk number within the document
    text: str

    @property
    def chunk_id(self) -> str:
        return f"{self.doc_name}#c{self.index}"


def clean_markdown(text: str) -> str:
    """Turn markdown headings into plain sentences so chunking stays readable.

    "# Title" -> "Title."  (keeps headings from gluing onto the next sentence)
    """
    def _heading(match: re.Match) -> str:
        heading = match.group(1).strip()
        if heading and heading[-1] not in ".!?:":
            heading += "."
        return heading

    text = re.sub(r"(?m)^#{1,6}\s+(.+?)\s*$", _heading, text)
    # Drop other common markdown noise but keep the words.
    text = re.sub(r"(?m)^\s*[-*]\s+", "", text)  # list bullets
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)  # bold
    text = re.sub(r"\*([^*]+)\*", r"\1", text)  # italics
    return text


def load_documents(docs_dir: str) -> list[tuple[str, str]]:
    """Return (file_name, text) for every supported file in docs_dir, sorted by name."""
    if not os.path.isdir(docs_dir):
        raise FileNotFoundError(f"Docs directory not found: {docs_dir}")
    documents: list[tuple[str, str]] = []
    for name in sorted(os.listdir(docs_dir)):
        ext = os.path.splitext(name)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            continue
        path = os.path.join(docs_dir, name)
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        if text.strip():
            documents.append((name, text))
    return documents


def chunk_text(doc_name: str, text: str, chunk_size: int = 120, overlap: int = 30) -> list[Chunk]:
    """Split text into word-based chunks with overlap.

    chunk_size: words per chunk. overlap: words shared with the previous chunk.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if not (0 <= overlap < chunk_size):
        raise ValueError("overlap must be in [0, chunk_size)")

    words = text.split()
    chunks: list[Chunk] = []
    start = 0
    idx = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunks.append(Chunk(doc_name=doc_name, index=idx, text=" ".join(chunk_words)))
        idx += 1
        if end == len(words):
            break
        start = end - overlap
    return chunks


def ingest(docs_dir: str, chunk_size: int = 120, overlap: int = 30) -> list[Chunk]:
    """Ingest every supported document in docs_dir into a flat list of chunks."""
    documents = load_documents(docs_dir)
    if not documents:
        raise ValueError(f"No readable documents found in {docs_dir}")
    chunks: list[Chunk] = []
    for doc_name, text in documents:
        chunks.extend(chunk_text(doc_name, clean_markdown(text), chunk_size=chunk_size, overlap=overlap))
    return chunks
