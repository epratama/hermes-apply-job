# Hermes Apply Job

Tailor your resume and cover letter for any job listing using Hermes Agent's
Mixture of Agents (MoA) and a multi-agent consortium pipeline.

## Quick Start

You'll need Python 3, git, and Hermes Agent.

### 1. Install Hermes Agent — skip if already installed

```bash
hermes --version   # verify it's on your PATH
```
If not installed: [hermes-agent.nousresearch.com](https://hermes-agent.nousresearch.com/)

### 2. Configure a model provider — skip if already configured

```bash
hermes setup                 # first time only
hermes model                 # verify: shows your current provider/model
```
Default presets use OpenRouter. See [Customizing Models](#customizing-models)
to use a different provider.

### 3. Prepare your resume in DOCX format. See [Preparing Your Resume](#preparing-your-resume)

### 4. Clone and set up

```bash
git clone https://github.com/epratama/hermes-apply-job && cd hermes-apply-job
python3 scripts/setup.py --resume ~/your-resume.docx
```

Style and output format are chosen at runtime during `/apply-job`. No flags needed.

For an AI agent to run setup unattended, add `--yes`:

```bash
python3 scripts/setup.py --resume ~/your-resume.docx --yes
```

### 5. Verify setup

```bash
hermes skills list | grep apply-job   # should show apply-job
hermes moa list                       # should show 3 presets
ls resume.docx                        # should exist
```

If any check fails, re-run `python3 scripts/setup.py --resume <path>`.
If the skill doesn't appear, restart Hermes.

### 6. Open Hermes in this directory

```bash
cd hermes-apply-job && hermes
```
Hermes must run from this directory — it loads `AGENTS.md` which tells
the agent how this project works.

### 7. Tailor your first application

```
/apply-job https://example.com/jobs/12345
```

Replace the URL with an actual job listing. You'll be asked to choose a style
and format **before** the pipeline runs — four styles are available
(classic, modern, minimal, keep mine) in DOCX or PDF output.

You can also browse templates online and paste a Typst Universe URL for
inspiration: https://typst.app/universe/search?q=resume

## Preparing Your Resume

The `--resume` flag copies your file into the project as `resume.docx` — this
is your source of truth for all tailored output. The file is gitignored and
never committed.

- **Already have a DOCX?** Point `--resume` to it:
  `python3 scripts/setup.py --resume ~/Documents/my-resume.docx`
- **PDF or other formats?** The setup script copies whatever file you provide
  and saves it as `resume.docx`. Pandoc is used at runtime to extract text.
  **Note:** "keep mine" style (style 4) requires an actual DOCX file — it
  reads your document's fonts and colors with python-docx.
- **No resume yet?** Write one first. The pipeline tailors existing content
  to job descriptions — it doesn't create a resume from scratch.

If `resume.docx` is missing when you run `/apply-job`, the pipeline stops
and asks you to place it there.

## What the Setup Script Does

`python3 scripts/setup.py` walks you through:

1. Checks Hermes is installed and toolsets (terminal, delegation, web)
   are enabled
2. Copies your resume to the project as `resume.docx`
3. Installs the `apply-job`, `stop-slop`, and `ui-ux-pro-max` skills to
   `~/.hermes/skills/`
4. Checks your MoA presets, shows what's missing, asks to merge defaults
5. Validates everything with Hermes

Re-run it any time to update your configuration.

## Mixture of Agents Presets

The pipeline uses three named [MoA presets](https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents),
each tuned for a specific role:

### `resume-analyzer` — Job Analysis

Parses the job listing. Uses a fast model to scan and an accurate model to
structure the output.

| Role | Model |
|------|-------|
| Reference | `deepseek/deepseek-v4-flash` |
| Aggregator | `deepseek/deepseek-v4-pro` |

### `resume-writer` — Resume & Cover Letter

Drafts tailored documents. Two reference models provide balanced creative
perspectives; the aggregator produces the final unified output.

| Role | Model |
|------|-------|
| Reference | `minimax/MiniMax-M3` |
| Reference | `nvidia/nemotron-3-ultra` |
| Aggregator | `deepseek/deepseek-v4-pro` |

### `resume-auditor` — Quality Scoring

Scores both documents on keyword coverage, ATS parsability, fabrication
detection, length, tone, personalization, and AI writing pattern detection.
Two independent critiques feed into one verdict.

| Role | Model |
|------|-------|
| Reference | `minimax/MiniMax-M3` |
| Reference | `nvidia/nemotron-3-ultra` |
| Aggregator | `deepseek/deepseek-v4-pro` |

### Customizing Models

All defaults use OpenRouter. To use different models or providers:

1. Edit `config/moa-presets.yaml`
2. Replace the `model:` values with models accessible on your account
3. Run `python3 scripts/setup.py` again

Example — switch everything to OpenAI (paste under `moa.presets:` in
`~/.hermes/config.yaml`):

```yaml
resume-analyzer:
  reference_models:
    - provider: openai
      model: gpt-4o-mini
  aggregator:
    provider: openai
    model: gpt-4o
```

All other preset options (`reference_max_tokens`, etc.) remain unchanged.

See [MoA documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents)
for all configuration options (temperature, max tokens, multi-provider mixing).

## Output Formats

Style and format are chosen at the start of each `/apply-job` run — not at setup time.
You can change styles between job applications without re-running setup.

| Format | Description |
|--------|-------------|
| **DOCX** (default) | Editable in Word, Pages, LibreOffice. Make final tweaks before sending. |
| **PDF** | Print-ready, locked layout. Best for direct submission. |

4 styles available (classic, modern, minimal, keep mine) + browse custom templates at
https://typst.app/universe/search?q=resume for design inspiration. "keep mine"
preserves your master document's formatting.

## How the Pipeline Works

```
┌────────────────────────────────────────────────────────────────┐
│ /apply-job <url>                                               │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│ Step 0       │ Step 1       │ Job Analyzer │ Resume Writer     │
│ Style+Format │ Pre-Flight   │ (analyzer)   │ (writer)          │
│ Selection    │              │              │                   │
│              │ Verify       │ Fetch JD     │ Tailor resume     │
│ 4 styles     │ resume.docx  │ Extract      │ with JD keywords  │
│ docx/pdf     │ pandoc conv  │ keywords     │                   │
└──────────────┴──────────────┴──────────────┴───────────────────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
   Cover Letter      Auditor       Consortium
   Writer            Score 7 crit  Writer↔Auditor
   (writer)          (auditor)     (up to 3 rounds)
   Draft cover                     Stop when ≥90
            │             │             │
            └─────────────┼─────────────┘
                          ▼
              ┌─────────────────────────────┐
              │ Step 7: Generate Output     │
              │ UI-UX-Pro-Max design system │
              │ HTML/CSS + pandoc/weasyprint│
              └─────────────────────────────┘
```

## Files

```
hermes-apply-job/
  README.md                   ← You are here
  IDEA.md                     ← Full project spec
  AGENTS.md                   ← Hermes auto-loaded context
  LICENSE                     ← MIT license
  .gitignore                  ← Ignores resume.docx, previews, __pycache__, and output
  resume.docx                 ← Your resume (gitignored)
  config/
    moa-presets.yaml          ← MoA model configuration
  docs/
                              ← Historical planning artifacts
  scripts/
    setup.py                  ← One-command setup
  tests/
    test_setup.py             ← Setup script self-check
  previews/                   ← Generated lorem ipsum previews (gitignored)
  templates/
    resume/
      base.html               ← ATS-friendly resume template
      cover-base.html         ← ATS-friendly cover letter template
  skills/
    apply-job/
      SKILL.md                ← The orchestrator skill
      lorem-resume.md         ← Preview placeholder content
      lorem-coverletter.md    ← Preview placeholder content
    stop-slop/
      SKILL.md                ← AI slop detection
      LICENSE                 ← MIT license (Hardik Pandya)
      references/
        phrases.md
        structures.md
        examples.md
    ui-ux-pro-max/
      SKILL.md                ← Design intelligence
      scripts/
        search.py             ← Design system generator
        core.py               ← CSV search engine
        design_system.py      ← Design system formatter
      data/                   ← Styles, colors, fonts, UX guidelines
  tailored-resumes/           ← Output directory
    .gitkeep
    <company>-<role>/
      analysis.md
      Resume.md
      CoverLetter.md
      Resume.<docx|pdf>
      CoverLetter.<docx|pdf>
      audit-round-1.md
      ...
```

## Guardrails

All claims in the output are traceable to your `resume.docx`. The auditor
deducts heavily for fabricated experience and flags every suspect line.
If the JD asks for a skill you don't have, the cover letter acknowledges
it honestly instead of inventing it.

## FAQ

### "hermes skills list" doesn't show apply-job
Restart Hermes. The skill is installed but Hermes scans skills at startup.
Re-run `python3 scripts/setup.py` if it still doesn't appear.

### MoA presets show "model not found"
The default models require OpenRouter access. Edit `config/moa-presets.yaml`
to use models available on your account, then re-run `python3 scripts/setup.py`.

### Pandoc not found during conversion
Pandoc is required. The pipeline stops and asks you to install it.
Install with your package manager and re-run the pipeline.

### The auditor score stays below 90 after 3 rounds
The JD might be behind a login wall. The pipeline will prompt you to paste
the full job description when asked — provide the complete text.

### Can I use my own API keys instead of OpenRouter?
Yes. Edit `config/moa-presets.yaml` — change `provider` and `model` values.
Re-run `python3 scripts/setup.py`. See Customizing Models section above.

### Does this work on Windows?
Yes. Hermes Agent supports Windows natively.

### How do I update the skill?
`git pull && python3 scripts/setup.py --resume <path>`

### My resume is in Word/Pages format
DOCX is the recommended format. The setup script accepts any file and saves
it as `resume.docx`. Pandoc reads DOCX natively at runtime — no conversion
needed.

### I already have MoA presets. Will setup overwrite them?
No. For fresh configurations, setup merges the defaults and creates a
backup (`~/.hermes/config.yaml.bak`). For existing MoA sections, setup
prints the presets for manual addition to avoid YAML merge issues.

### How do I change models after setup?
Edit `config/moa-presets.yaml` and run `python3 scripts/setup.py --resume <path>`
again.

### How do I change the resume template?
Re-run `/apply-job <url>`. The pipeline regenerates all templates — pick a
different one. No need to re-run setup.

### How do I use a custom resume template for design inspiration?
Browse https://typst.app/universe/search?q=resume. When the pipeline
asks for style selection, paste the package URL. Hermes extracts the
design system and applies it to your content via HTML/CSS.

## License

MIT — see [LICENSE](LICENSE).

## Credits

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) by [Nous Research](https://nousresearch.com) — MIT License
- [stop-slop](https://github.com/hardikpandya/stop-slop) by [Hardik Pandya](https://hvpandya.com) — MIT License
- [Superpowers](https://github.com/obra/superpowers) by [obra](https://github.com/obra) — Apache 2.0 License
- [Ponytail](https://github.com/DietrichGebert/ponytail) by [Dietrich Gebert](https://github.com/DietrichGebert) — MIT License
- [OpenCode](https://github.com/opencode-ai/opencode) — MIT License
