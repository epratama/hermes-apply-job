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
from unittest.mock import patch

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


def test_ask_interactive_yes():
    """ask() returns True for y/yes/Y/YES/empty."""
    with patch.object(setup, "_AUTO_YES", False):
        with patch("builtins.input") as mock_input:
            for answer in ("", "y", "yes", "Y", "yEs"):
                mock_input.return_value = answer
                assert setup.ask("Prompt?") is True


def test_ask_interactive_no():
    """ask() returns False for n/no/N/no thanks/anything else."""
    with patch.object(setup, "_AUTO_YES", False):
        with patch("builtins.input") as mock_input:
            for answer in ("n", "no", "N", "No", "nope"):
                mock_input.return_value = answer
                assert setup.ask("Prompt?") is False


def test_run_success():
    """run() returns (0, stdout) on success."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "hello\n"
        rc, out = setup.run("echo hello")
    assert rc == 0
    assert out == "hello"


def test_run_failure():
    """run() returns (returncode, '') on nonzero exit."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        rc, out = setup.run("false")
    assert rc == 1
    assert out == ""


def test_run_filenotfound():
    """run() returns (-1, '') when binary not found."""
    with patch("subprocess.run", side_effect=FileNotFoundError):
        rc, out = setup.run("nonexistent_binary")
    assert rc == -1
    assert out == ""


def test_setup_moa_all_present():
    """setup_moa skips when all presets already configured."""
    with patch.object(setup, "load_moa_defaults", return_value="moa:\n  presets:\n    test:"), \
         patch.object(setup, "_detect_moa_presets", return_value={"resume-analyzer", "resume-writer", "resume-auditor"}):
        setup.setup_moa()  # should return early without asking


def test_setup_moa_missing_with_merge():
    """setup_moa merges defaults when user accepts."""
    moa_content = "moa:\n  presets:\n    resume-analyzer:\n"
    with patch.object(setup, "load_moa_defaults", return_value=moa_content), \
         patch.object(setup, "_detect_moa_presets", return_value=set()), \
         patch.object(setup, "ask", return_value=True), \
         patch.object(setup, "load_config", return_value=""), \
         patch.object(setup, "merge_moa_config", return_value=True):
        setup.setup_moa()


def test_setup_moa_missing_decline():
    """setup_moa skips merge when user declines."""
    moa_content = "moa:\n  presets:\n    resume-analyzer:\n"
    with patch.object(setup, "load_moa_defaults", return_value=moa_content), \
         patch.object(setup, "_detect_moa_presets", return_value=set()), \
         patch.object(setup, "ask", return_value=False):
        setup.setup_moa()


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
