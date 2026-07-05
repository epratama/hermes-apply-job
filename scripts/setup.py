#!/usr/bin/env python3
"""Hermes Apply-Job Setup — one-command configuration.

Author: Eky Pratama
Repo:   https://github.com/epratama/hermes-apply-job

Usage:
    python3 scripts/setup.py --resume ~/my-resume.docx
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
DEVNULL = "NUL" if IS_WINDOWS else "/dev/null"

HERMES_URL = "https://hermes-agent.nousresearch.com/"
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

_AUTO_YES = False  # set by --yes flag for unattended agent setup


def run(cmd, capture=True):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
        return result.returncode, result.stdout.strip() if capture else ""
    except FileNotFoundError:
        return -1, ""


def _hermes_home():
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
    if _AUTO_YES:
        return True
    answer = input(f"  {msg} [Y/n]: ").strip().lower()
    return answer in ("", "y", "yes")


def check_hermes():
    header("Prerequisites")
    if not shutil.which("hermes"):
        err("Hermes Agent not found.")
        print(f"  Install: {HERMES_URL}")
        sys.exit(1)
    ok("Hermes Agent detected")


def _enable_toolset(toolset):
    if ask(f"Enable {toolset} toolset?"):
        rc, _ = run(f"hermes tools enable {toolset} 2>{DEVNULL}")
        if rc == 0:
            ok(f"{toolset} enabled")
            return
        warn(f"Could not enable {toolset}. Run 'hermes tools enable {toolset}' manually.")
    warn(f"{toolset} must be enabled for the pipeline. Enable it manually.")


def check_toolsets():
    rc, out = run(f"hermes tools list 2>{DEVNULL}")
    enabled = set()
    for line in out.split("\n"):
        if "enabled" not in line:
            continue
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


def copy_resume(resume_path):
    header("Resume")
    src = Path(resume_path).expanduser().resolve()
    dst = Path(__file__).parent.parent / "resume.docx"

    if not src.exists():
        err(f"Resume not found: {src}")
        sys.exit(1)

    if src == dst.resolve():
        ok(f"Already in place: resume.docx")
        return

    ext = src.suffix.lower()
    if ext in (".md", ".txt"):
        if not shutil.which("pandoc"):
            err("Markdown/txt input requires pandoc. Install: https://pandoc.org/installing.html")
            sys.exit(1)
        ok(f"Converting {src.name} to resume.docx via pandoc...")
        rc, _ = run(f"pandoc {src} -o {dst}", capture=False)
        if rc != 0:
            err("Pandoc conversion failed. Is your file valid?")
            sys.exit(1)
        ok(f"Converted {src.name} to resume.docx")
    elif ext == ".pdf":
        if not shutil.which("pandoc"):
            err("PDF input requires pandoc. Install: https://pandoc.org/installing.html")
            sys.exit(1)
        ok(f"Converting {src.name} (first page) to resume.docx via pandoc...")
        rc, _ = run(f"pandoc {src} -o {dst}", capture=False)
        if rc != 0:
            err("Pandoc conversion failed. Is your PDF text-selectable?")
            sys.exit(1)
        ok(f"Converted {src.name} to resume.docx")
    else:
        shutil.copy2(src, dst)
        ok(f"Copied {src.name} to resume.docx")


def install_skills():
    header("Skills")
    hermes_dir = _hermes_home()
    src_dir = Path(__file__).parent.parent / "skills"

    # ponytail: three skills, unrolled.
    for name, cat in [("apply-job", "career"), ("stop-slop", "writing"), ("ui-ux-pro-max", "writing")]:
        src = src_dir / name
        dst = hermes_dir / "skills" / cat / name
        if not src.exists():
            err(f"{name} skill not found at {src}")
            continue
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        ok(f"Installed {name} to {dst}")

    rc, out = run(f"hermes skills list 2>{DEVNULL}")
    if any(s in out for s in ("apply-job", "stop-slop", "ui-ux-pro-max")):
        ok("Skills registered with Hermes")
    else:
        warn("Skills installed but not detected. Restart Hermes if it was running.")


def load_config():
    config_path = _hermes_home() / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            return f.read()
    return ""


def load_moa_defaults():
    moa_path = Path(__file__).parent.parent / "config" / "moa-presets.yaml"
    if not moa_path.exists():
        err("config/moa-presets.yaml not found")
        return None
    with open(moa_path) as f:
        return f.read()


def merge_moa_config(config_content, moa_content):
    config_path = _hermes_home() / "config.yaml"

    if "moa:" not in config_content or config_content.strip() == "":
        if config_content.strip():
            merged = config_content.rstrip() + "\n\n" + moa_content
            backup_path = config_path.with_suffix(".yaml.bak")
            with open(backup_path, "w") as f:
                f.write(config_content)
        else:
            merged = moa_content
        with open(config_path, "w") as f:
            f.write(merged)
        return True

    # ponytail: no YAML parser — show presets for manual merge
    warn("MoA section already exists in config. Add these presets manually.")
    print("  Under moa.presets: in ~/.hermes/config.yaml, add:")
    moa_lines = moa_content.strip().split("\n")
    in_presets = False
    for line in moa_lines:
        if line.startswith("  presets:"):
            in_presets = True
            continue
        if in_presets and line.strip():
            print(f"  {line}")
    print("  Then run: hermes moa list\n")
    return False


def _detect_moa_presets():
    rc, out = run(f"hermes moa list 2>{DEVNULL}")
    if rc != 0 or not out:
        return set()
    existing = set()
    for line in out.split("\n"):
        for preset in ["resume-analyzer", "resume-writer", "resume-auditor"]:
            if preset in line:
                existing.add(preset)
    return existing


def setup_moa():
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

    print(f"  Required presets: resume-analyzer, resume-writer, resume-auditor")
    print(f"  Missing: {', '.join(sorted(missing))}")
    if existing:
        print(f"  Already configured: {', '.join(sorted(existing))}")
    print("  Default presets from config/moa-presets.yaml:")
    for preset in sorted(missing):
        print(f"    \u2022 {preset}")
    print()

    if ask("Merge defaults into ~/.hermes/config.yaml?"):
        did_merge = merge_moa_config(load_config(), moa_content)
        if did_merge:
            ok("MoA presets merged")
    else:
        warn("Skipped MoA config. Run setup again or edit config manually.")
        print("  Edit config/moa-presets.yaml and re-run: python3 scripts/setup.py")


def print_summary():
    print(f"\n{C_GREEN}{C_BOLD}Done.{C_RESET}  Style & format chosen at runtime.")
    print(f"  {C_CYAN}/apply-job{C_RESET} <job-listing-url>\n")


def main():
    parser = argparse.ArgumentParser(description="Hermes Apply-Job Setup")
    parser.add_argument("--resume", required=True,
                        help="Path to your resume (docx/md/txt/pdf; pandoc required for non-docx)")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Skip all prompts (for automated/agent-driven setup)")
    args = parser.parse_args()

    global _AUTO_YES
    _AUTO_YES = args.yes

    print(f"\n{C_BOLD}Hermes Apply-Job — Setup — github.com/epratama/hermes-apply-job{C_RESET}\n")

    check_hermes()
    check_toolsets()
    copy_resume(args.resume)
    install_skills()
    setup_moa()
    print_summary()


if __name__ == "__main__":
    main()
