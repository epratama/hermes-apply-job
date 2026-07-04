#!/usr/bin/env python3
"""Hermes Apply-Job Setup — one-command configuration.

Author: Eky Pratama
Repo:   https://github.com/epratama/hermes-apply-job

Usage:
    python3 scripts/setup.py --resume ~/my-resume.pdf [--format md|docx|pdf]
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


def _check_tool(name, hint, url, output_format):
    """Check one tool. Print OS-specific install instructions if missing.
    Returns True if found, False otherwise."""
    if shutil.which(name):
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


def check_pandoc_needed(output_format):
    if output_format == "md":
        return True
    if not _check_tool("pandoc", "pandoc", PANDOC_URL, output_format):
        ok("Output will stay as markdown. Use --format md to avoid this warning.")
        return False
    if output_format == "pdf":
        _check_tool("wkhtmltopdf", "wkhtmltopdf", WKHTML_URL, output_format)
    return True


def copy_resume(resume_path):
    header("Resume")
    src = Path(resume_path).expanduser().resolve()
    dst = Path(__file__).parent.parent / "resume.pdf"
    if not src.exists():
        err(f"Resume not found: {src}")
        sys.exit(1)
    shutil.copy2(src, dst)
    ok(f"Copied {src.name} to resume.pdf")


def install_skills():
    header("Skills")
    hermes_dir = _hermes_home()
    src_dir = Path(__file__).parent.parent / "skills"

    # ponytail: two skills, unrolled. Loop overhead for N=2 is silly.
    for name, cat in [("apply-job", "career"), ("stop-slop", "writing")]:
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


def _validate_moa():
    rc, out = run(f"hermes moa list 2>{DEVNULL}")
    if rc == 0 and out:
        ok("hermes moa list succeeded")
        for line in out.split("\n"):
            print(f"    {line.strip()}")
        return
    warn("Could not validate with hermes moa list")


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
            header("Validation")
            _validate_moa()
    else:
        warn("Skipped MoA config. Run setup again or edit config manually.")
        print("  Edit config/moa-presets.yaml and re-run: python3 scripts/setup.py")


def set_output_format(output_format):
    header("Output Format")
    rc, _ = run(f"hermes config set skills.config.apply-job.output_format {output_format} 2>{DEVNULL}")
    if rc == 0:
        ok(f"Output format set to: {output_format}")
    else:
        warn(f"Could not set output format. Run manually: hermes config set skills.config.apply-job.output_format {output_format}")


def print_summary(output_format):
    print(f"\n{C_GREEN}{C_BOLD}Done.{C_RESET}  Output format: {output_format}")
    print(f"  {C_CYAN}/apply-job{C_RESET} <job-listing-url>\n")


def main():
    parser = argparse.ArgumentParser(description="Hermes Apply-Job Setup")
    parser.add_argument("--resume", required=True, help="Path to your resume PDF")
    parser.add_argument("--format", default="md", choices=["md", "docx", "pdf"],
                        help="Output format (default: md)")
    args = parser.parse_args()

    url = "github.com/epratama/hermes-apply-job"
    w = len(url) + 4
    h_bar = "\u2550"
    h_title = "Hermes Apply-Job \u2014 Setup"
    h_author = "by Eky Pratama"
    print(f"{C_BOLD}\u2554{h_bar * w}\u2557{C_RESET}")
    print(f"{C_BOLD}\u2551{h_title:^{w}}\u2551{C_RESET}")
    print(f"{C_BOLD}\u2551  {url}  \u2551{C_RESET}")
    print(f"{C_BOLD}\u2551{h_author:^{w}}\u2551{C_RESET}")
    print(f"{C_BOLD}\u255a{h_bar * w}\u255d{C_RESET}")
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
