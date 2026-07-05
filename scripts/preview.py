#!/usr/bin/env python
"""Generate a styled resume preview from lorem ipsum content.

Usage:
    python scripts/preview.py <style>

Styles: classic, modern, minimal
    classic    — serif, traditional
    modern     — sans-serif, blue accent
    minimal    — clean monochrome

Output: previews/<style>-resume.html, previews/<style>-coverletter.html
"""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PREVIEWS_DIR = PROJECT_ROOT / "previews"
LOREM_RESUME = PROJECT_ROOT / "skills" / "apply-job" / "lorem-resume.md"
LOREM_COVER = PROJECT_ROOT / "skills" / "apply-job" / "lorem-coverletter.md"
TEMPLATE = PROJECT_ROOT / "templates" / "resume" / "base.html"

STYLES = {
    "classic": {
        "body-font": "Georgia, 'Times New Roman', serif",
        "heading-font": "Georgia, 'Times New Roman', serif",
        "accent-color": "#1a1a1a",
        "bg": "#ffffff",
        "name": "Classic Serif",
    },
    "modern": {
        "body-font": "Inter, system-ui, sans-serif",
        "heading-font": "Inter, system-ui, sans-serif",
        "accent-color": "#2563EB",
        "bg": "#ffffff",
        "name": "Modern Sans",
    },
    "minimal": {
        "body-font": "system-ui, sans-serif",
        "heading-font": "system-ui, sans-serif",
        "accent-color": "#374151",
        "bg": "#ffffff",
        "name": "Clean Minimal",
    },
}

RESUME_CSS = """
body { font-family: {{BODY_FONT}}; color: #1a1a1a; background: {{BG}}; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; }
h1 { font-family: {{HEADING_FONT}}; color: {{ACCENT}}; font-size: 1.75rem; margin-bottom: 0.25rem; }
h2 { font-family: {{HEADING_FONT}}; color: {{ACCENT}}; font-size: 1.1rem; border-bottom: 2px solid {{ACCENT}}; padding-bottom: 0.25rem; margin-top: 1.5rem; }
.contact { color: #6b7280; font-size: 0.9rem; margin-bottom: 1rem; }
ul { padding-left: 1.25rem; margin-top: 0.25rem; }
li { margin-bottom: 0.35rem; }
"""


def generate_preview(style_key):
    if style_key == "keep-mine":
        print("Style 4 (keep-mine) requires a real resume.docx. Create one with setup.py and use /apply-job.")
        sys.exit(1)

    if style_key not in STYLES:
        print(f"Unknown style: {style_key}. Choose: {', '.join(STYLES)}")
        sys.exit(1)

    style = STYLES[style_key]

    if not LOREM_RESUME.exists() or not LOREM_COVER.exists():
        print("Lorem content files not found. Run setup first.")
        sys.exit(1)

    css = (RESUME_CSS
           .replace("{{BODY_FONT}}", style["body-font"])
           .replace("{{HEADING_FONT}}", style["heading-font"])
           .replace("{{ACCENT}}", style["accent-color"])
           .replace("{{BG}}", style["bg"]))

    resume_md = LOREM_RESUME.read_text()
    cover_md = LOREM_COVER.read_text()

    resume_html = (
        '<!DOCTYPE html>\n<html lang="en">\n'
        '<head><meta charset="UTF-8">'
        f'<title>Resume Preview — {style["name"]}</title>\n'
        f'<style>{css}</style></head>\n<body>\n'
        f'<pre style="font-family: {style["body-font"]}; line-height: 1.6; white-space: pre-wrap;">\n'
        f'{resume_md}\n</pre>\n</body></html>'
    )

    cover_html = (
        '<!DOCTYPE html>\n<html lang="en">\n'
        '<head><meta charset="UTF-8">'
        f'<title>Cover Letter Preview — {style["name"]}</title>\n'
        f'<style>{css}</style></head>\n<body>\n'
        f'<pre style="font-family: {style["body-font"]}; line-height: 1.6; white-space: pre-wrap;">\n'
        f'{cover_md}\n</pre>\n</body></html>'
    )

    PREVIEWS_DIR.mkdir(exist_ok=True)
    (PREVIEWS_DIR / f"{style_key}-resume.html").write_text(resume_html)
    (PREVIEWS_DIR / f"{style_key}-coverletter.html").write_text(cover_html)

    print(f"Generated {style_key}-resume.html, {style_key}-coverletter.html in previews/")


def main():
    parser = argparse.ArgumentParser(description="Generate styled resume preview")
    parser.add_argument("style", choices=list(STYLES), help="Style name")
    args = parser.parse_args()
    generate_preview(args.style)


if __name__ == "__main__":
    main()
