"""Tests for extractive answer generation."""

from vaultchat.answer import answer_question, split_sentences
from vaultchat.ingest import Chunk
from vaultchat.retrieval import Hit


def _hit(doc, idx, text, score=0.9):
    return Hit(chunk=Chunk(doc, idx, text), score=score)


def test_split_sentences():
    sents = split_sentences("First sentence. Second one! And a third?")
    assert sents == ["First sentence.", "Second one!", "And a third?"]


def test_answer_extracts_relevant_sentence_with_citation():
    hits = [
        _hit("git.md", 0, "To undo your last commit but keep changes, run git reset --soft HEAD~1. This is unrelated filler text."),
    ]
    ans = answer_question("how do I undo a commit", hits)
    assert "git reset --soft" in ans.text
    assert "[1]" in ans.text
    assert ans.citations[0].doc_name == "git.md"
    assert ans.citations[0].chunk_index == 0
    assert "git.md (chunk 0)" in ans.render()


def test_answer_cites_multiple_chunks():
    hits = [
        _hit("a.md", 0, "Emergency funds cover three to six months of expenses.", score=0.9),
        _hit("b.md", 1, "Automate transfers to savings on payday for consistent saving.", score=0.8),
    ]
    ans = answer_question("how much emergency fund and savings automation", hits, max_sentences=2)
    assert "[1]" in ans.text and "[2]" in ans.text
    assert len(ans.citations) == 2


def test_answer_dedupes_repeated_sentences():
    hits = [_hit("a.md", 0, "Save twenty percent. Save twenty percent."), _hit("a.md", 1, "Save twenty percent.")]
    ans = answer_question("how much should I save", hits, max_sentences=5)
    assert ans.text.count("Save twenty percent.") == 1


def test_answer_handles_no_relevant_hits():
    ans = answer_question("quantum physics", [])
    assert ans.citations == []
    assert "couldn't find" in ans.text.lower()


def test_render_lists_sources():
    hits = [_hit("git.md", 2, "Use git stash to shelve uncommitted changes.")]
    ans = answer_question("stash changes", hits)
    rendered = ans.render()
    assert rendered.startswith(ans.text.strip())
    assert "Sources:" in rendered
    assert "[1] git.md (chunk 2)" in rendered


def test_answer_citation_numbers_follow_best_sentences_order():
    hits = [
        _hit("a.md", 0, "Emergency funds cover three to six months of expenses.", score=0.9),
        _hit("b.md", 1, "Automate transfers to savings on payday.", score=0.8),
        _hit("c.md", 2, "Track subscriptions monthly to cut waste.", score=0.7),
    ]
    ans = answer_question(
        "emergency funds savings subscriptions", hits, max_sentences=3
    )
    assert ans.citations[0].doc_name == "a.md"
    assert ans.citations[1].doc_name == "b.md"
    assert ans.citations[2].doc_name == "c.md"
