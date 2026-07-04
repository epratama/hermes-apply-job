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
        if t not in enabled:
            err(f"{t} toolset not enabled")
            if ask(f"Enable {t} toolset?"):
                rc, _ = run(f"hermes tools enable {t} 2>/dev/null")
                if rc == 0:
                    ok(f"{t} enabled")
                else:
                    warn(f"Could not enable {t}. Run 'hermes tools enable {t}' manually.")
            else:
                warn(f"{t} must be enabled for the pipeline. Enable it manually.")
        else:
            ok(f"{t} toolset enabled")


def check_pandoc_needed(output_format):
    """Check pandoc is available if docx/pdf output."""
    if output_format == "md":
        return True
    rc, _ = run("which pandoc")
    if rc == 0:
        ok("pandoc installed")
        if output_format == "pdf":
            rc, _ = run("which wkhtmltopdf")
            if rc == 0:
                ok("wkhtmltopdf installed")
            else:
                err("wkhtmltopdf not found (needed for PDF output)")
                if ask("Install wkhtmltopdf?"):
                    install_cmd = "brew install wkhtmltopdf 2>/dev/null || apt install -y wkhtmltopdf 2>/dev/null || choco install wkhtmltopdf 2>/dev/null"
                    rc, _ = run(install_cmd)
                    if rc == 0:
                        ok("wkhtmltopdf installed")
                    else:
                        warn("Install manually: brew install wkhtmltopdf")
                        return True
        return True
    else:
        err(f"pandoc not found (needed for {output_format} output)")
        if ask("Install pandoc?"):
            install_cmd = "brew install pandoc 2>/dev/null || apt install -y pandoc 2>/dev/null || choco install pandoc 2>/dev/null"
            rc, _ = run(install_cmd)
            if rc == 0:
                ok("pandoc installed")
                return True
        warn(f"Install manually: brew install pandoc (or your system's package manager)")
        ok(f"Output will stay as markdown. Use --format md to avoid this warning.")
        return False


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
    If config has no moa section, append the moa content.
    If config has existing moa section, append only the new presets under it.
    """
    config_path = Path.home() / ".hermes" / "config.yaml"

    if "moa:" not in config_content or config_content.strip() == "":
        if config_content.strip():
            merged = config_content.rstrip() + "\n\n" + moa_content
        else:
            merged = moa_content
    else:
        # Moa section exists — extract only the presets block from moa_content
        # and indent it under the existing moa: key to avoid duplicate keys
        moa_lines = moa_content.strip().split("\n")
        preset_lines = []
        found_presets = False
        for line in moa_lines:
            if line.startswith("  presets:"):
                found_presets = True
                preset_lines.append(line.strip())
            elif found_presets:
                preset_lines.append(line.rstrip())
        if preset_lines:
            moa_block = "\n".join(preset_lines)
            merged = config_content.rstrip() + "\n\n# Added by hermes-apply-job setup\n" + moa_block
        else:
            merged = config_content

    # Backup original
    backup_path = config_path.with_suffix(".yaml.bak")
    if config_content.strip():
        with open(backup_path, "w") as f:
            f.write(config_content)

    with open(config_path, "w") as f:
        f.write(merged)


def setup_moa():
    """Detect, report, and merge MoA presets."""
    header("MoA Presets")

    moa_content = load_moa_defaults()
    if moa_content is None:
        return

    config_content = load_config()

    # Check what presets already exist
    rc, out = run("hermes moa list 2>/dev/null")
    existing = set()
    if rc == 0 and out:
        for line in out.split("\n"):
            for preset in ["resume-analyzer", "resume-writer", "resume-auditor"]:
                if preset in line:
                    existing.add(preset)

    needed = {"resume-analyzer", "resume-writer", "resume-auditor"}
    missing = needed - existing

    if not missing:
        ok("All MoA presets already configured")
    else:
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

        if ask("Merge defaults into ~/.hermes/config.yaml?"):
            merge_moa_config(config_content, moa_content)
            ok("MoA presets merged")

            # Validate with Hermes
            header("Validation")
            rc, out = run("hermes moa list 2>/dev/null")
            if rc == 0 and out:
                ok("hermes moa list succeeded")
                for line in out.split("\n"):
                    print(f"    {line.strip()}")
            else:
                warn("Could not validate with hermes moa list")
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
