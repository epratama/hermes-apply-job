#!/usr/bin/env python
"""Tests for skills/apply-job/SKILL.md — structural validation.

Run: python tests/test_skill.py
"""

import os
import re
import sys
from pathlib import Path

SKILL_PATH = Path(__file__).parent.parent / "skills" / "apply-job" / "SKILL.md"


def test_skill_exists():
    """SKILL.md file exists and is readable."""
    assert SKILL_PATH.exists(), f"{SKILL_PATH} not found"
    content = SKILL_PATH.read_text()
    assert len(content) > 100, "SKILL.md is too short"


def test_all_eight_steps():
    """Contains Step 0 through Step 7 headers."""
    content = SKILL_PATH.read_text()
    for n in range(8):
        assert f"Step {n}" in content, f"Missing Step {n} header"


def test_progress_headers_have_etas():
    """All [Step N of 7] headers include timing estimates (~Xs)."""
    content = SKILL_PATH.read_text()
    headers = re.findall(r'\[Step \d of 7\].*', content)
    assert len(headers) >= 7, f"Expected >=7 progress headers, got {len(headers)}"
    for h in headers:
        assert "~" in h, f"Progress header missing ETA: {h}"


def test_no_stale_patterns():
    """SKILL.md contains no removed features or platform-specific cruft."""
    content = SKILL_PATH.read_text()
    stale = [
        ("brew install", "macOS-only instruction, use pandoc.org URL instead"),
        ("/tmp/", "hardcoded Unix path, use <tempdir>/ instead"),
        ("Typst Universe", "Typst URL browsing was removed in 5a4f3a0"),
        ("python3", "use python (cross-platform) instead"),
    ]
    for pattern, reason in stale:
        assert pattern not in content, f"Stale pattern '{pattern}': {reason}"


def test_required_sections_present():
    """Contains Pitfalls, Verification, and MoA Presets sections."""
    content = SKILL_PATH.read_text()
    required = ["## Pitfalls", "## Verification", "## MoA Presets"]
    for section in required:
        assert section in content, f"Missing section: {section}"


def test_step_one_has_placeholder_check():
    """Step 1 includes bracket placeholder detection."""
    content = SKILL_PATH.read_text()
    step1_start = content.find("### Step 1")
    step2_start = content.find("### Step 2")
    step1 = content[step1_start:step2_start]
    assert "placeholder" in step1.lower(), "Step 1 missing placeholder detection"
    assert "[your.email" in step1 or "bracket" in step1.lower(), "Step 1 missing bracket placeholder example"


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
