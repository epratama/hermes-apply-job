#!/usr/bin/env python
"""Tests for scripts/preview.py — TDD self-check.

Run: python tests/test_preview.py
"""

import inspect
import io
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import preview


def test_styles_only_three():
    """STYLES has exactly 3 entries, no keep-mine."""
    assert len(preview.STYLES) == 3
    assert "keep-mine" not in preview.STYLES
    assert set(preview.STYLES) == {"classic", "modern", "minimal"}


def test_keep_mine_shows_error():
    """generate_preview('keep-mine') prints error and exits."""
    out = io.StringIO()
    try:
        with patch("sys.stdout", out):
            preview.generate_preview("keep-mine")
    except SystemExit:
        pass
    assert "requires a real resume.docx" in out.getvalue()


def test_generate_preview_single_param():
    """generate_preview takes exactly 1 parameter (no --format param)."""
    sig = inspect.signature(preview.generate_preview)
    assert len(sig.parameters) == 1


def test_classic_preview_generates_valid_html():
    """classic style generates HTML files without template leakage."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        with patch.object(preview, "LOREM_RESUME", tmp / "lorem-resume.md"), \
             patch.object(preview, "LOREM_COVER", tmp / "lorem-coverletter.md"), \
             patch.object(preview, "PREVIEWS_DIR", tmp):
            (tmp / "lorem-resume.md").write_text("## Jane Doe\n\nSenior Engineer")
            (tmp / "lorem-coverletter.md").write_text("Dear Hiring Team,\n\nI am writing to apply...")
            preview.generate_preview("classic")
            resume_html = (tmp / "classic-resume.html").read_text()
            assert "{BODY_FONT}" not in resume_html
            assert "Jane Doe" in resume_html
            cover_html = (tmp / "classic-coverletter.html").read_text()
            assert "{BODY_FONT}" not in cover_html
            assert "Hiring Team" in cover_html


if __name__ == "__main__":
    import traceback
    passed = 0
    failed = []
    for name in sorted(globals()):
        if not name.startswith("test_"):
            continue
        fn = globals()[name]
        try:
            fn()
            passed += 1
            print(f"  ✓ {name}")
        except Exception:
            failed.append(name)
            print(f"  ✗ {name}")
            traceback.print_exc()
    print(f"\n{'─' * 40}\n{passed} passed, {len(failed)} failed")
    sys.exit(1 if failed else 0)
