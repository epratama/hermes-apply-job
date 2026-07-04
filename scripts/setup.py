#!/usr/bin/env python3
"""Hermes Apply-Job Setup — one-command configuration.

Author: Eky Pratama
Repo:   https://github.com/epratama/hermes-apply-job

Usage:
    python3 scripts/setup.py --resume ~/my-resume.pdf [--format md|docx|pdf]

Checks prerequisites, copies your resume, installs apply-job and stop-slop
skills, merges MoA presets, and validates with Hermes.
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

SYSTEM = platform.system()
IS_WINDOWS = SYSTEM == "Windows"
IS_MACOS = SYSTEM == "Darwin"
IS_LINUX = SYSTEM == "Linux"
DEVNULL = "NUL" if IS_WINDOWS else "/dev/null"

HERMES_URL = "https://hermes-agent.nousresearch.com/"
PANDOC_URL = "https://pandoc.org/installing.html"
WKHTML_URL = "https://wkhtmltopdf.org/downloads.html"

# ANSI colors — disabled when output is piped
IS_TTY = sys.stdout.isatty()
C_RESET  = "\033[0m"  if IS_TTY else ""
C_BOLD   = "\033[1m"  if IS_TTY else ""
C_GREEN  = "\033[32m" if IS_TTY else ""
C_YELLOW = "\033[33m" if IS_TTY else ""
C_RED    = "\033[31m" if IS_TTY else ""
C_CYAN   = "\033[36m" if IS_TTY else ""
GREEN_CHECK  = f"{C_GREEN}\u2713{C_RESET}"
YELLOW_WARN  = f"{C_YELLOW}\u26a0{C_RESET}"
RED_CROSS    = f"{C_RED}\u2717{C_RESET}"

# ponytail: shutil.which() is stdlib since 3.3, covers unix+windows
def _which(cmd):
    return shutil.which(cmd) is not None


def run(cmd, capture=True):
    """Run a shell command, return (returncode, stdout)."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
        return result.returncode, result.stdout.strip() if capture else ""
    except FileNotFoundError:
        return -1, ""


def _hermes_home():
    """Hermes home directory on any OS."""
    env_home = os.environ.get("HERMES_HOME")
    if env_home:
        return Path(env_home)
    if IS_WINDOWS:
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "hermes"
    return Path.home() / ".hermes"


def header(text):
    print(f"\n{C_CYAN}{C_BOLD}==>{C_RESET} {text}")


def ok(msg):
    print(f"  {GREEN_CHECK} {msg}")


def warn(msg):
    print(f"  {YELLOW_WARN} {msg}")


def err(msg):
    print(f"  {RED_CROSS} {msg}")


def ask(msg):
    answer = input(f"  {msg} [Y/n]: ").strip().lower()
    return answer in ("", "y", "yes")


def check_hermes():
    """Check Hermes Agent is installed."""
    header("Prerequisites")
    if not _which("hermes"):
        err("Hermes Agent not found.")
        print(f"  Install: {HERMES_URL}")
        sys.exit(1)
    ok("Hermes Agent detected")


def _enable_toolset(toolset):
    """Prompt to enable a disabled toolset."""
    if ask(f"Enable {toolset} toolset?"):
        rc, _ = run(f"hermes tools enable {toolset} 2>{DEVNULL}")
        if rc == 0:
            ok(f"{toolset} enabled")
            return
        warn(f"Could not enable {toolset}. Run 'hermes tools enable {toolset}' manually.")
    warn(f"{toolset} must be enabled for the pipeline. Enable it manually.")


def check_toolsets():
    """Verify required toolsets are enabled."""
    rc, out = run(f"hermes tools list 2>{DEVNULL} | grep -E 'terminal|delegation|web' | grep enabled")
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


def check_pandoc_needed(output_format):
    """Check pandoc and wkhtmltopdf availability for docx/pdf output.
    Prints install instructions per-OS — user runs them manually."""
    if output_format == "md":
        return True

    def _check(name, hint, url):
        if _which(name):
            ok(f"{name} installed")
            return True
        err(f"{name} not found (needed for {output_format} output)")
        if IS_MACOS:
            warn(f"Install manually: brew install {hint}")
        elif IS_LINUX:
            warn(f"Install from: {url}")
        elif IS_WINDOWS:
            warn(f"Install from: {url}")
        return False

    if not _check("pandoc", "pandoc", PANDOC_URL):
        ok("Output will stay as markdown. Use --format md to avoid this warning.")
        return False
    if output_format == "pdf":
        _check("wkhtmltopdf", "wkhtmltopdf", WKHTML_URL)
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


def install_skills():
    """Install apply-job and stop-slop skills to Hermes."""
    header("Skills")
    src_dir = Path(__file__).parent.parent / "skills"
    hermes_dir = _hermes_home()
    skills_config = [
        {"name": "apply-job", "category": "career"},
        {"name": "stop-slop", "category": "writing"},
    ]
    for skill in skills_config:
        name, cat = skill["name"], skill["category"]
        src = src_dir / name
        dst = hermes_dir / "skills" / cat / name
        if not src.exists():
            err(f"{name} skill not found at {src}")
            continue
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        ok(f"Installed {name} to {dst}")

    rc, out = run(f"hermes skills list 2>{DEVNULL} | grep -E 'apply-job|stop-slop'")
    if rc == 0:
        ok("Skills registered with Hermes")
    else:
        warn("Skills installed but not detected. Restart Hermes if it was running.")


def load_config():
    """Load ~/.hermes/config.yaml if it exists."""
    config_path = _hermes_home() / "config.yaml"
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
    — avoids YAML nesting errors from string-based insertion.
    Returns True if file was modified, False if only instructions were printed.
    """
    config_path = _hermes_home() / "config.yaml"

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
    rc, out = run(f"hermes moa list 2>{DEVNULL}")
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
    print("    \u2022 resume-analyzer  \u2014 Fast extraction (deepseek-v4-flash + v4-pro)")
    print("    \u2022 resume-writer    \u2014 Creative writing (MiniMax-M3 + Nemotron 3 Ultra + v4-pro)")
    print("    \u2022 resume-auditor   \u2014 Detail scoring (MiniMax-M3 + Nemotron 3 Ultra + v4-pro)")
    print()


def _validate_moa():
    """Run hermes moa list and print results."""
    rc, out = run(f"hermes moa list 2>{DEVNULL}")
    if rc == 0 and out:
        ok("hermes moa list succeeded")
        for line in out.split("\n"):
            print(f"    {line.strip()}")
        return
    warn("Could not validate with hermes moa list")


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
    rc, _ = run(f"hermes config set skills.config.apply-job.output_format {output_format} 2>{DEVNULL}")
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

    print(f"{C_BOLD}\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557{C_RESET}")
    print(f"{C_BOLD}\u2551          Hermes Apply-Job \u2014 Setup           \u2551{C_RESET}")
    print(f"{C_BOLD}\u2551   github.com/epratama/hermes-apply-job      \u2551{C_RESET}")
    print(f"{C_BOLD}\u2551               by Eky Pratama                \u2551{C_RESET}")
    print(f"{C_BOLD}\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d{C_RESET}")
    print()

    check_hermes()
    check_toolsets()
    check_pandoc_needed(args.format)
    copy_resume(args.resume)
    install_skills()
    setup_moa()
    set_output_format(args.format)
    print_summary(args.format)


if __name__ == "__main__":
    main()
