"""Extractive Q&A: compose answers from retrieved chunks, with cited sources."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

from .ingest import Chunk
from .retrieval import Hit, tokenize

_SENTENCE_RE = re.compile(r"[^.!?]+[.!?]")
_CODE_SPAN_RE = re.compile(r"`[^`]*`")


@dataclass
class Citation:
    number: int  # [1], [2], ...
    doc_name: str
    chunk_index: int

    def label(self) -> str:
        return f"[{self.number}]"

    def reference(self) -> str:
        return f"{self.doc_name} (chunk {self.chunk_index})"


@dataclass
class Answer:
    text: str  # answer body with inline [n] markers
    citations: list[Citation]
    hits: list[Hit]

    def render(self) -> str:
        lines = [self.text.strip(), "", "Sources:"]
        for c in self.citations:
            lines.append(f"  {c.label()} {c.reference()}")
        return "\n".join(lines)


def split_sentences(text: str) -> list[str]:
    """Split text into sentences, cleaning up whitespace.

    Periods inside inline code spans (backticks) don't end sentences.
    """
    placeholders: dict[str, str] = {}

    def _mask(match: re.Match) -> str:
        key = f"\x00CODE{len(placeholders)}\x00"
        placeholders[key] = match.group(0)
        return key

    masked = _CODE_SPAN_RE.sub(_mask, text)
    sentences = [re.sub(r"\s+", " ", s).strip() for s in _SENTENCE_RE.findall(masked)]
    leftover = _SENTENCE_RE.sub("", masked)
    leftover = re.sub(r"\s+", " ", leftover).strip()
    if leftover:
        sentences.append(leftover)

    restored = []
    for s in sentences:
        for key, code in placeholders.items():
            s = s.replace(key, code)
        s = s.strip()
        if s:
            restored.append(s)
    return restored


def score_sentence(sentence: str, query_terms: set[str]) -> float:
    """Score a sentence by query-term overlap (length-normalized)."""
    tokens = set(tokenize(sentence))
    if not tokens:
        return 0.0
    overlap = len(tokens & query_terms)
    if overlap == 0:
        return 0.0
    # Reward term coverage, lightly prefer complete sentences.
    return overlap / math.sqrt(len(tokens))


def answer_question(
    query: str,
    hits: list[Hit],
    max_sentences: int = 4,
    top_k_chunks: int | None = None,
) -> Answer:
    """Build an extractive answer from retrieval hits.

    Picks the most relevant sentences across the top chunks and cites the
    chunk each sentence came from. Every claim is traceable to a source.
    """
    query_terms = set(tokenize(query))
    chosen_hits = hits if top_k_chunks is None else hits[:top_k_chunks]

    citations: list[Citation] = []
    citation_by_chunk: dict[str, Citation] = {}
    hit_by_chunk_id = {hit.chunk.chunk_id: hit for hit in chosen_hits}
    candidates: list[tuple[float, str, str]] = []  # (score, chunk_id, sentence)

    for hit in chosen_hits:
        for sentence in split_sentences(hit.chunk.text):
            s = score_sentence(sentence, query_terms)
            if s > 0:
                candidates.append((s * (0.5 + hit.score), hit.chunk.chunk_id, sentence))

    candidates.sort(key=lambda c: c[0], reverse=True)

    seen: set[str] = set()
    picked: list[tuple[str, str]] = []  # (chunk_id, sentence)
    for _, chunk_id, sentence in candidates:
        normalized = sentence.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        picked.append((chunk_id, sentence))
        if len(picked) >= max_sentences:
            break

    if not picked:
        return Answer(
            text="I couldn't find anything relevant in the indexed documents.",
            citations=[],
            hits=chosen_hits,
        )

    for chunk_id, _ in picked:
        if chunk_id not in citation_by_chunk:
            hit = hit_by_chunk_id[chunk_id]
            citation_by_chunk[chunk_id] = Citation(
                number=len(citation_by_chunk) + 1,
                doc_name=hit.chunk.doc_name,
                chunk_index=hit.chunk.index,
            )
            citations.append(citation_by_chunk[chunk_id])

    lines = []
    for chunk_id, sentence in picked:
        lines.append(f"{sentence} {citation_by_chunk[chunk_id].label()}")
    return Answer(text=" ".join(lines), citations=citations, hits=chosen_hits)
