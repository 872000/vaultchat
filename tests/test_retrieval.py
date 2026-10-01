"""Tests for the pure-Python TF-IDF retriever."""

import math

import pytest

from vaultchat.ingest import Chunk
from vaultchat.retrieval import build_index, search, tokenize


def _chunks():
    return [
        Chunk("git.md", 0, "git reset soft undo last commit keep changes"),
        Chunk("git.md", 1, "git stash shelves uncommitted changes temporarily"),
        Chunk("finance.md", 0, "emergency fund three to six months expenses savings account"),
    ]


def test_tokenize_lowercases_and_drops_stopwords():
    assert tokenize("The CAT sat") == ["cat", "sat"]
    assert tokenize("hello, world! 123") == ["hello", "world", "123"]


def test_build_index_rejects_empty():
    with pytest.raises(ValueError):
        build_index([])


def test_search_finds_relevant_chunk():
    index = build_index(_chunks())
    hits = search("how do I undo a commit", index, top_k=2)
    assert hits
    assert hits[0].chunk.doc_name == "git.md"
    assert hits[0].chunk.index == 0
    assert hits[0].score > 0


def test_search_ranks_more_relevant_chunk_first():
    index = build_index(_chunks())
    hits = search("stash my changes", index, top_k=3)
    assert hits[0].chunk.index == 1


def test_search_scores_are_cosine_bounded():
    index = build_index(_chunks())
    hits = search("emergency fund savings", index, top_k=3)
    assert all(0 < h.score <= 1.0 for h in hits)


def test_search_no_match_returns_empty():
    index = build_index(_chunks())
    assert search("quantum entanglement zebras", index) == []


def test_search_empty_query_returns_empty():
    index = build_index(_chunks())
    assert search("the and of", index) == []
    assert search("", index) == []


def test_search_top_k_limit():
    index = build_index(_chunks())
    hits = search("git", index, top_k=1)
    assert len(hits) == 1
