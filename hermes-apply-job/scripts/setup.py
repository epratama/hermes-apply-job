#!/usr/bin/env python3
"""Hermes Apply-Job Setup — one-command configuration.

Usage:
    python3 scripts/setup.py --resume ~/my-resume.pdf [--format md|docx|pdf]

Checks prerequisites, copies your resume, installs the apply-job skill,
merges MoA presets into ~/.hermes/config.yaml, and validates with Hermes.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd, capture=True):
    """Run a shell command, return (returncode, stdout)."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
        return result.returncode, result.stdout.strip() if capture else ""
    except FileNotFoundError:
        return -1, ""


def header(text):
    print(f"\n━━━ {text} ━━━")


def ok(msg):
    print(f"  ✓ {msg}")


def warn(msg):
    print(f"  ⚠ {msg}")


def err(msg):
    print(f"  ✗ {msg}")


def ask(msg):
    answer = input(f"  {msg} [Y/n]: ").strip().lower()
    return answer in ("", "y", "yes")


def check_hermes():
    """Check Hermes Agent is installed."""
    header("Prerequisites")
    rc, _ = run("which hermes")
    if rc != 0:
        err("Hermes Agent not found.")
        print("  Install: https://hermes-agent.nousresearch.com/")
        sys.exit(1)
    ok("Hermes Agent detected")


def _enable_toolset(toolset):
    """Prompt to enable a disabled toolset."""
    if ask(f"Enable {toolset} toolset?"):
        rc, _ = run(f"hermes tools enable {toolset} 2>/dev/null")
        if rc == 0:
            ok(f"{toolset} enabled")
            return
        warn(f"Could not enable {toolset}. Run 'hermes tools enable {toolset}' manually.")
    warn(f"{toolset} must be enabled for the pipeline. Enable it manually.")


def check_toolsets():
    """Verify required toolsets are enabled."""
    rc, out = run("hermes tools list 2>/dev/null | grep -E 'terminal|delegation|web' | grep enabled")
    if rc != 0 or not out:
        warn("Could not verify toolsets. Ensure terminal, delegation, and web are enabled.")
        return
    enabled = set()
    for line in out.split("\n"):
        if "terminal" in line:
            enabled.add("terminal")
        if "delegation" in line:
            enabled.add("delegation")
        if "web" in line:
            enabled.add("web")

    for t in ["terminal", "delegation", "web"]:
        if t in enabled:
            ok(f"{t} toolset enabled")
        else:
            err(f"{t} toolset not enabled")
            _enable_toolset(t)


def _check_pandoc_installed():
    """Return True if pandoc is available, prompt install if not."""
    rc, _ = run("which pandoc")
    if rc == 0:
        ok("pandoc installed")
        return True
    err("pandoc not found")
    if ask("Install pandoc?"):
        install_cmd = "brew install pandoc 2>/dev/null || apt install -y pandoc 2>/dev/null || choco install pandoc 2>/dev/null"
        rc, _ = run(install_cmd)
        if rc == 0:
            ok("pandoc installed")
            return True
    warn("Install manually: brew install pandoc (or your system's package manager)")
    return False


def _check_wkhtmltopdf_installed():
    """Return True if wkhtmltopdf is available, prompt install if not.
    Returns True even if not available (non-blocking for PDF setup)."""
    rc, _ = run("which wkhtmltopdf")
    if rc == 0:
        ok("wkhtmltopdf installed")
        return True
    err("wkhtmltopdf not found (needed for PDF output)")
    if ask("Install wkhtmltopdf?"):
        install_cmd = "brew install wkhtmltopdf 2>/dev/null || apt install -y wkhtmltopdf 2>/dev/null || choco install wkhtmltopdf 2>/dev/null"
        rc, _ = run(install_cmd)
        if rc == 0:
            ok("wkhtmltopdf installed")
            return True
    warn("Install manually: brew install wkhtmltopdf")
    return True  # let setup continue even without wkhtmltopdf


def check_pandoc_needed(output_format):
    """Check pandoc and wkhtmltopdf availability for docx/pdf output."""
    if output_format == "md":
        return True
    if not _check_pandoc_installed():
        ok("Output will stay as markdown. Use --format md to avoid this warning.")
        return False
    if output_format == "pdf":
        _check_wkhtmltopdf_installed()
    return True


def copy_resume(resume_path):
    """Copy the user's resume to the project root."""
    header("Resume")
    src = Path(resume_path).expanduser().resolve()
    dst = Path(__file__).parent.parent / "resume.pdf"

    if not src.exists():
        err(f"Resume not found: {src}")
        sys.exit(1)

    shutil.copy2(src, dst)
    ok(f"Copied {src.name} to resume.pdf")


def install_skill():
    """Install the apply-job skill to Hermes."""
    header("Skill")
    src = Path(__file__).parent.parent / "skills" / "apply-job"
    dst = Path.home() / ".hermes" / "skills" / "career" / "apply-job"

    if dst.exists():
        shutil.rmtree(dst)

    shutil.copytree(src, dst)
    ok(f"Installed to ~/.hermes/skills/career/apply-job/")

    # Verify registration
    rc, out = run("hermes skills list 2>/dev/null | grep apply-job")
    if rc == 0:
        ok("Skill registered with Hermes")
    else:
        warn("Skill installed but not detected. Restart Hermes if it was running.")


def load_config():
    """Load ~/.hermes/config.yaml if it exists."""
    config_path = Path.home() / ".hermes" / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            return f.read()
    return ""


def load_moa_defaults():
    """Load the MoA presets from config/moa-presets.yaml."""
    moa_path = Path(__file__).parent.parent / "config" / "moa-presets.yaml"
    if not moa_path.exists():
        err("config/moa-presets.yaml not found")
        return None
    with open(moa_path) as f:
        return f.read()


def merge_moa_config(config_content, moa_content):
    """
    Merge MoA presets into config content.
    If config has no moa section, append the moa content directly.
    If config already has a moa section, show the presets for manual merge
    (safe — avoids YAML nesting errors from string-based insertion).
    Returns True if file was modified, False if only instructions were printed.
    """
    config_path = Path.home() / ".hermes" / "config.yaml"

    if "moa:" not in config_content or config_content.strip() == "":
        if config_content.strip():
            merged = config_content.rstrip() + "\n\n" + moa_content
        else:
            merged = moa_content

        if config_content.strip():
            backup_path = config_path.with_suffix(".yaml.bak")
            with open(backup_path, "w") as f:
                f.write(config_content)

        with open(config_path, "w") as f:
            f.write(merged)
        return True

    # moa: section exists — show presets for manual merge
    warn("MoA section already exists in config. Add these presets manually.")
    print()
    moa_lines = moa_content.strip().split("\n")
    in_presets = False
    for line in moa_lines:
        if line.startswith("  presets:"):
            in_presets = True
            print("  Under moa.presets: in ~/.hermes/config.yaml, add:")
            continue
        if in_presets and line.strip():
            print(f"  {line}")
    print()
    print("  Then run: hermes moa list")
    print()
    return False


def _detect_moa_presets():
    """Return set of preset names already configured in Hermes."""
    rc, out = run("hermes moa list 2>/dev/null")
    if rc != 0 or not out:
        return set()
    existing = set()
    for line in out.split("\n"):
        for preset in ["resume-analyzer", "resume-writer", "resume-auditor"]:
            if preset in line:
                existing.add(preset)
    return existing


def _print_missing_presets(missing, existing):
    """Print what presets are missing and what's already configured."""
    print(f"  Required presets: resume-analyzer, resume-writer, resume-auditor")
    print(f"  Missing: {', '.join(sorted(missing))}")
    if existing:
        print(f"  Already configured: {', '.join(sorted(existing))}")
    print()
    print("  Default presets from config/moa-presets.yaml:")
    print("    • resume-analyzer  — Fast extraction (deepseek-v4-flash + v4-pro)")
    print("    • resume-writer    — Creative writing (MiniMax-M3 + Nemotron 3 Ultra + v4-pro)")
    print("    • resume-auditor   — Detail scoring (MiniMax-M3 + Nemotron 3 Ultra + v4-pro)")
    print()


def _validate_moa():
    """Run hermes moa list and print results. Return True if successful."""
    rc, out = run("hermes moa list 2>/dev/null")
    if rc == 0 and out:
        ok("hermes moa list succeeded")
        for line in out.split("\n"):
            print(f"    {line.strip()}")
        return True
    warn("Could not validate with hermes moa list")
    return False


def setup_moa():
    """Detect, report, and merge MoA presets."""
    header("MoA Presets")

    moa_content = load_moa_defaults()
    if moa_content is None:
        return

    existing = _detect_moa_presets()
    needed = {"resume-analyzer", "resume-writer", "resume-auditor"}
    missing = needed - existing

    if not missing:
        ok("All MoA presets already configured")
        return

    _print_missing_presets(missing, existing)

    if ask("Merge defaults into ~/.hermes/config.yaml?"):
        did_merge = merge_moa_config(load_config(), moa_content)
        if did_merge:
            ok("MoA presets merged")
            header("Validation")
            _validate_moa()
    else:
        warn("Skipped MoA config. Run setup again or edit config manually.")
        print("  Edit config/moa-presets.yaml and re-run: python3 scripts/setup.py")


def set_output_format(output_format):
    """Set the output_format in Hermes skill config."""
    header("Output Format")
    rc, _ = run(f"hermes config set skills.config.apply-job.output_format {output_format} 2>/dev/null")
    if rc == 0:
        ok(f"Output format set to: {output_format}")
    else:
        warn(f"Could not set output format. Run manually: hermes config set skills.config.apply-job.output_format {output_format}")


def print_summary(output_format):
    """Print next steps."""
    header("Done")
    print()
    print(f"  Output format: {output_format}")
    print()
    print("  Ready! Run:")
    print("    cd hermes-apply-job && hermes")
    print("    /apply-job <job-listing-url>")
    print()


def main():
    parser = argparse.ArgumentParser(description="Hermes Apply-Job Setup")
    parser.add_argument("--resume", required=True, help="Path to your resume PDF")
    parser.add_argument("--format", default="md", choices=["md", "docx", "pdf"],
                        help="Output format (default: md)")
    args = parser.parse_args()

    print("Hermes Apply-Job — Setup")
    print("=========================")

    check_hermes()
    check_toolsets()
    check_pandoc_needed(args.format)
    copy_resume(args.resume)
    install_skill()
    setup_moa()
    set_output_format(args.format)
    print_summary(args.format)


if __name__ == "__main__":
    main()
