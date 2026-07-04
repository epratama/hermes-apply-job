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

### 3. Prepare your resume as a PDF — see [Preparing Your Resume](#preparing-your-resume)

### 4. Clone and set up

```bash
git clone https://github.com/epratama/hermes-apply-job && cd hermes-apply-job
python3 scripts/setup.py --resume ~/your-resume.pdf
```

Start with markdown (the default). Add `--format pdf` once you have
pandoc + typst installed.

For an AI agent to run setup unattended, add `--yes`:

```bash
python3 scripts/setup.py --resume ~/your-resume.pdf --yes
```

### 5. Verify setup

```bash
hermes skills list | grep apply-job   # should show apply-job
hermes moa list                       # should show 3 presets
ls resume.pdf                         # should exist
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
Replace the URL with an actual job listing.

## Preparing Your Resume

The `--resume` flag copies your PDF into the project as `resume.pdf` — this
is your source of truth for all tailored output. The file is gitignored and
never committed.

- **Already have a PDF?** Point `--resume` to it:
  `python3 scripts/setup.py --resume ~/Documents/my-resume.pdf`
- **Word or Pages?** Convert first:
  - macOS: File → Export as PDF, or `pandoc resume.docx -o resume.pdf`
  - Linux: `pandoc resume.docx -o resume.pdf`
  - Windows: File → Save As → PDF, or `pandoc resume.docx -o resume.pdf`
- **No resume yet?** Write one first. The pipeline tailors existing content
  to job descriptions — it doesn't create a resume from scratch.

If `resume.pdf` is missing when you run `/apply-job`, the pipeline stops
and asks you to place it there.

## What the Setup Script Does

`python3 scripts/setup.py` walks you through:

1. Checks Hermes is installed and toolsets (terminal, delegation, web)
   are enabled
2. Checks pandoc, typst, and wkhtmltopdf availability and prints OS-specific
   instructions if you picked docx/pdf output
3. Copies your resume to the project as `resume.pdf`
4. Installs the `apply-job` and `stop-slop` skills to `~/.hermes/skills/`
5. Checks your MoA presets, shows what's missing, asks to merge defaults
6. Validates everything with Hermes

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

| Flag | Output | Requirements |
|------|--------|-------------|
| `--format md` (default) | `Resume.md`, `CoverLetter.md` | None |
| `--format docx` | `Resume.docx`, `CoverLetter.docx` | pandoc |
| `--format pdf` | `Resume.pdf`, `CoverLetter.pdf` | pandoc + typst (recommended) or wkhtmltopdf |

Output lands in `tailored-resumes/<company>-<role>/` along with the job
analysis and audit reports. Only the format you selected is produced.

## How the Pipeline Works

```
┌──────────────────────────────────────────────────────────────┐
│ /apply-job <url>                                             │
├──────────────┬──────────────┬──────────────┬─────────────────┤
│ Job Analyzer │ Resume Writer│ Cover Letter │ Auditor         │
│ (analyzer)   │ (writer)     │ Writer       │ (auditor)       │
│              │              │ (writer)     │                 │
│ Fetch JD     │ Tailor       │ Draft cover  │ Score across    │
│ Extract      │ resume with  │ letter       │ 7 criteria      │
│ keywords     │ JD keywords  │              │ (target ≥90)    │
└──────────────┴──────────────┴──────────────┴─────────────────┘
                          │
                          ▼
              ┌─────────────────────┐
              │ Consortium Loop     │
              │ Writer ←→ Auditor   │
              │ (up to 3 rounds)    │
              └─────────────────────┘
                          │
                          ▼
              ┌─────────────────────────────┐
              │ Templates & PDF (3 styles)  │
              │   Present final output      │
              └─────────────────────────────┘
```

## Files

```
hermes-apply-job/
  README.md                   ← You are here
  IDEA.md                     ← Full project spec
  AGENTS.md                   ← Hermes auto-loaded context
  .gitignore                  ← Ignores resume.pdf and output
  resume.pdf                  ← Your resume (gitignored)
  config/
    moa-presets.yaml          ← MoA model configuration
  scripts/
    setup.py                  ← One-command setup
  tests/
    test_setup.py             ← Setup script self-check
  templates/
    resume/
      classic.typ             ← Serif, traditional
      modern.typ              ← Sans-serif, accent
      minimal.typ             ← Monochrome, ATS
    coverletter/              ← Matching cover letter templates
  skills/
    apply-job/
      SKILL.md                ← The skill source
    stop-slop/
      SKILL.md                ← AI slop detection
      references/
        phrases.md
        structures.md
        examples.md
  tailored-resumes/           ← Output directory
    <company>-<role>/
      analysis.md
      Resume.md / .docx / .pdf
      CoverLetter.md / .docx / .pdf
      audit-round-1.md
      ...
```

## Guardrails

All claims in the output are traceable to your `resume.pdf`. The auditor
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
The pipeline falls back to markdown output. Install pandoc with your package
manager and re-run the pipeline.

### The auditor score stays below 90 after 3 rounds
The JD might be behind a login wall. The pipeline will prompt you to paste
the full job description when asked — provide the complete text.

### Can I use my own API keys instead of OpenRouter?
Yes. Edit `config/moa-presets.yaml` — change `provider` and `model` values.
Re-run `python3 scripts/setup.py`. See Customizing Models section above.

### Does this work on Windows?
Yes. Hermes Agent supports Windows natively. Setup prints OS-specific
install instructions for any missing tools.

### How do I update the skill?
`git pull && python3 scripts/setup.py --resume <path>`

### My resume is in Word/Pages format
Convert to PDF first (`pandoc resume.docx -o resume.pdf` or File → Export
as PDF), then provide the PDF to `--resume`.

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

### How do I use a custom Typst resume template?
Browse https://typst.app/universe/search?q=resume. When the pipeline
asks for template selection, paste the package URL. Hermes downloads
and compiles the template for your content.

## License

MIT — see [LICENSE](LICENSE).

## Credits

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) by [Nous Research](https://nousresearch.com) — MIT License
- [stop-slop](https://github.com/hardikpandya/stop-slop) by [Hardik Pandya](https://hvpandya.com) — MIT License
- [Superpowers](https://github.com/obra/superpowers) by [obra](https://github.com/obra) — Apache 2.0 License
- [Ponytail](https://github.com/DietrichGebert/ponytail) by [Dietrich Gebert](https://github.com/DietrichGebert) — MIT License
- [OpenCode](https://github.com/opencode-ai/opencode) — MIT License
- [Typst](https://github.com/typst/typst) — Apache 2.0 License
