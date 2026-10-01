"""Pure-Python TF-IDF retrieval with cosine similarity (stdlib only)."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field

from .ingest import Chunk

_TOKEN_RE = re.compile(r"[a-z0-9]+")

# A compact English stopword list so common words don't dominate scoring.
STOPWORDS = frozenset(
    """
    a about above after again against all am an and any are as at be because been
    before being below between both but by can cannot could did do does doing down
    during each few for from further had has have having he her here hers herself
    him himself his how i if in into is it its itself me more most my myself no nor
    not of off on once only or other ought our ours ourselves out over own same she
    should so some such than that the their theirs them themselves then there these
    they this those through to too under until up very was we were what when where
    which while who whom why with would you your yours yourself yourselves
    """.split()
)


def tokenize(text: str) -> list[str]:
    """Lowercase, split on non-alphanumerics, drop stopwords."""
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in STOPWORDS]


@dataclass
class Index:
    """TF-IDF index over a set of chunks."""

    chunks: list[Chunk]
    idf: dict[str, float] = field(default_factory=dict)
    doc_vectors: list[dict[str, float]] = field(default_factory=list)
    doc_norms: list[float] = field(default_factory=list)


def build_index(chunks: list[Chunk]) -> Index:
    """Build the TF-IDF index from chunks."""
    if not chunks:
        raise ValueError("Cannot build an index from zero chunks")

    n = len(chunks)
    term_counts: list[Counter] = [Counter(tokenize(c.text)) for c in chunks]

    df: Counter = Counter()
    for counts in term_counts:
        for term in counts:
            df[term] += 1

    idf = {term: math.log((n + 1) / (freq + 1)) + 1.0 for term, freq in df.items()}

    doc_vectors: list[dict[str, float]] = []
    doc_norms: list[float] = []
    for counts in term_counts:
        total = sum(counts.values()) or 1
        vec = {term: (count / total) * idf[term] for term, count in counts.items()}
        doc_vectors.append(vec)
        doc_norms.append(math.sqrt(sum(w * w for w in vec.values())) or 1e-12)

    return Index(chunks=chunks, idf=idf, doc_vectors=doc_vectors, doc_norms=doc_norms)


@dataclass
class Hit:
    chunk: Chunk
    score: float


def search(query: str, index: Index, top_k: int = 3) -> list[Hit]:
    """Rank chunks by cosine similarity between the query and each chunk vector."""
    if top_k <= 0:
        raise ValueError("top_k must be positive")

    q_counts = Counter(tokenize(query))
    total = sum(q_counts.values())
    if total == 0:
        return []

    q_vec = {term: (count / total) * index.idf.get(term, 0.0)
             for term, count in q_counts.items()
             if term in index.idf}
    q_norm = math.sqrt(sum(w * w for w in q_vec.values()))
    if q_norm == 0:
        return []

    scored: list[Hit] = []
    for chunk, d_vec, d_norm in zip(index.chunks, index.doc_vectors, index.doc_norms):
        dot = sum(q_w * d_vec.get(term, 0.0) for term, q_w in q_vec.items())
        score = dot / (q_norm * d_norm)
        if score > 0:
            scored.append(Hit(chunk=chunk, score=score))

    scored.sort(key=lambda h: h.score, reverse=True)
    return scored[:top_k]
