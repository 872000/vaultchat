"""Tests for the CLI: ask (one-shot) and chat (interactive loop)."""

import os
import subprocess
import sys

import pytest

from vaultchat.cli import main

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "docs")


def test_ask_answers_end_to_end(capsys):
    rc = main(["--docs", DOCS_DIR, "ask", "How do I undo a git commit?"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "git reset" in out
    assert "Sources:" in out
    assert "git-notes.md" in out


def test_ask_irrelevant_question_graceful(capsys):
    rc = main(["--docs", DOCS_DIR, "ask", "quantum entanglement zebras"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "couldn't find" in out.lower()


def test_ask_missing_docs_dir_errors(capsys):
    rc = main(["--docs", "/does/not/exist", "ask", "hello"])
    assert rc == 1


def test_chat_loop_quits(capsys, monkeypatch):
    inputs = iter(["What is the 50/30/20 rule?", "quit"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(inputs))
    rc = main(["--docs", DOCS_DIR, "chat"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "50 percent" in out
    assert "Sources:" in out
    assert "Bye!" in out


def test_module_entrypoint_works():
    result = subprocess.run(
        [sys.executable, "-m", "vaultchat", "--docs", DOCS_DIR, "ask", "What is VaultChat's stack?"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )
    assert result.returncode == 0
    assert "Sources:" in result.stdout
