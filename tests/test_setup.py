#!/usr/bin/env python3
"""Tests for scripts/setup.py — TDD self-check.

Run: python3 tests/test_setup.py

Covers 7 pure-logic functions. Integration functions (Hermes runtime)
are tested by running setup.py against a live Hermes installation.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "scripts"))

# Import setup module — globals freeze at import, patch inside tests
import setup


def test_hermes_home_env():
    """HERMES_HOME env var takes priority."""
    with patch.dict(os.environ, {"HERMES_HOME": "/custom/hermes"}, clear=True):
        result = setup._hermes_home()
    assert result == Path("/custom/hermes")


def test_hermes_home_default_unix():
    """Unix default: ~/.hermes."""
    with patch.dict(os.environ, {}, clear=True):
        result = setup._hermes_home()
    assert result == Path.home() / ".hermes"


def test_hermes_home_windows_localappdata():
    """Windows: LOCALAPPDATA\hermes."""
    with patch.dict(os.environ, {"LOCALAPPDATA": "C:\\Users\\test\\AppData\\Local"}, clear=True), \
         patch.object(setup, "IS_WINDOWS", True):
        result = str(setup._hermes_home())
    assert result.endswith("hermes")
    assert "test" in result


def test_hermes_home_windows_fallback():
    """Windows without LOCALAPPDATA falls back to AppData."""
    with patch.dict(os.environ, {}, clear=True), \
         patch.object(setup, "IS_WINDOWS", True), \
         patch.object(Path, "home", return_value=Path("/home/user")):
        result = setup._hermes_home()
    assert result == Path("/home/user/AppData/Local/hermes")


def test_check_tool_found():
    """_check_tool returns True when binary is on PATH."""
    with patch("shutil.which", return_value="/usr/bin/pandoc"):
        result = setup._check_tool("pandoc", "pandoc", "https://url", "pdf")
    assert result is True


def test_check_tool_missing_macos():
    """_check_tool returns False and prints brew instructions on macOS."""
    with patch("shutil.which", return_value=None), \
         patch.object(setup, "IS_MACOS", True):
        result = setup._check_tool("pandoc", "pandoc", "https://url", "pdf")
    assert result is False


def test_check_tool_missing_linux():
    """_check_tool returns False and prints URL on Linux."""
    with patch("shutil.which", return_value=None), \
         patch.object(setup, "IS_LINUX", True), \
         patch.object(setup, "IS_MACOS", False):
        result = setup._check_tool("pandoc", "pandoc", "https://url", "pdf")
    assert result is False


def test_check_tool_missing_windows():
    """_check_tool returns False and prints URL on Windows."""
    with patch("shutil.which", return_value=None), \
         patch.object(setup, "IS_WINDOWS", True), \
         patch.object(setup, "IS_MACOS", False):
        result = setup._check_tool("pandoc", "pandoc", "https://url", "pdf")
    assert result is False


def test_copy_resume_missing():
    """copy_resume aborts when source file doesn't exist."""
    with patch("sys.exit", side_effect=SystemExit):
        try:
            setup.copy_resume("/nonexistent/path/resume.docx")
        except SystemExit:
            pass


def test_copy_resume_success():
    """copy_resume copies file to project root as resume.docx."""
    src = Path(tempfile.mkstemp(suffix=".docx")[1])
    src.write_text("fake resume content")
    dst = src.parent / "resume.docx"
    try:
        with patch.object(setup, "__file__", str(src.parent / "scripts" / "setup.py")):
            setup.copy_resume(str(src))
        assert dst.exists()
        assert dst.read_text() == "fake resume content"
    finally:
        dst.unlink(missing_ok=True)
        src.unlink(missing_ok=True)


def test_load_config_exists():
    """load_config returns file content when config exists."""
    tmp = Path(tempfile.mkdtemp())
    try:
        (tmp / "config.yaml").write_text("key: value")
        with patch.object(setup, "_hermes_home", return_value=tmp):
            assert setup.load_config() == "key: value"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_load_config_missing():
    """load_config returns empty string when no config file."""
    with patch.object(setup, "_hermes_home", return_value=Path("/nonexistent")):
        assert setup.load_config() == ""


def test_load_moa_defaults_exists():
    """Returns MoA config content when file exists."""
    tmp = Path(tempfile.mkdtemp())
    try:
        presets = tmp / "config" / "moa-presets.yaml"
        presets.parent.mkdir(parents=True, exist_ok=True)
        presets.write_text("moa:\n  presets:\n    test:")
        with patch.object(setup, "__file__", str(tmp / "scripts" / "setup.py")):
            result = setup.load_moa_defaults()
        assert result == "moa:\n  presets:\n    test:"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_load_moa_defaults_missing():
    """Returns None when moa-presets.yaml does not exist."""
    with patch.object(setup, "__file__", "/nonexistent/scripts/setup.py"):
        assert setup.load_moa_defaults() is None


def test_merge_no_moa():
    """Writes full moa block when config has no moa: key."""
    tmp = Path(tempfile.mkdtemp())
    try:
        moa_content = "moa:\n  presets:\n    resume-analyzer:\n"
        with patch.object(setup, "_hermes_home", return_value=tmp):
            result = setup.merge_moa_config("", moa_content)
        assert result is True
        written = (tmp / "config.yaml").read_text()
        assert "moa:" in written
        assert "resume-analyzer" in written
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_merge_moa_with_existing_config():
    """Appends moa block to existing config."""
    tmp = Path(tempfile.mkdtemp())
    try:
        existing = "existing_key: value"
        moa = "moa:\n  presets:\n    resume-analyzer:\n"
        with patch.object(setup, "_hermes_home", return_value=tmp):
            result = setup.merge_moa_config(existing, moa)
        assert result is True
        written = (tmp / "config.yaml").read_text()
        assert "existing_key" in written
        assert "moa:" in written
        assert (tmp / "config.yaml.bak").read_text() == "existing_key: value"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_merge_existing_moa_refuses():
    """Returns False when config already has moa: key (manual merge)."""
    tmp = Path(tempfile.mkdtemp())
    try:
        existing = "moa:\n  presets:\n    existing_preset:"
        moa = "moa:\n  presets:\n    new_preset:\n"
        with patch.object(setup, "_hermes_home", return_value=tmp):
            result = setup.merge_moa_config(existing, moa)
        assert result is False
        assert not (tmp / "config.yaml").exists()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_ask_auto_yes():
    """ask() returns True when --yes flag overrides prompts."""
    with patch.object(setup, "_AUTO_YES", True):
        result = setup.ask("Test prompt?")
    assert result is True


def test_main_yes_flag():
    """--yes flag sets _AUTO_YES to True in main()."""
    with patch("sys.argv", ["setup.py", "--resume", "/tmp/fake.pdf", "--yes"]):
        try:
            setup.main()
        except SystemExit:
            pass
    assert setup._AUTO_YES is True


def test_main_no_yes_flag():
    """Without --yes flag, _AUTO_YES remains False in main()."""
    setup._AUTO_YES = False  # reset in case prior test leaked
    with patch("sys.argv", ["setup.py", "--resume", "/tmp/fake.pdf"]):
        try:
            setup.main()
        except SystemExit:
            pass
    assert setup._AUTO_YES is False


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
