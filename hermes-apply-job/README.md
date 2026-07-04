# Hermes Apply Job

Tailor your resume and cover letter for any job listing using Hermes Agent's
Mixture of Agents (MoA) and a multi-agent consortium pipeline.

## Quick Start

```bash
git clone <repo-url> && cd hermes-apply-job
python3 scripts/setup.py --resume ~/my-resume.pdf --format pdf
hermes
/apply-job https://example.com/jobs/12345
```

## Prerequisites

- **[Hermes Agent](https://hermes-agent.nousresearch.com/)** v0.18+
- **A model provider** configured in `~/.hermes/config.yaml`
  (default presets use OpenRouter; edit `config/moa-presets.yaml` to use your own)
- **pandoc** (for docx/pdf output) — install with your system package manager:
  ```bash
  brew install pandoc       # macOS
  apt install pandoc        # Linux
  choco install pandoc      # Windows
  ```
- **wkhtmltopdf** (for pdf output):
  ```bash
  brew install wkhtmltopdf       # macOS
  apt install wkhtmltopdf        # Linux
  choco install wkhtmltopdf      # Windows
  ```

The setup script checks all prerequisites and asks before installing anything.

## What the Setup Script Does

`python3 scripts/setup.py` walks you through:

1. Checks Hermes is installed and toolsets (terminal, delegation, web)
   are enabled
2. Optional: installs pandoc and wkhtmltopdf if you picked docx/pdf output
3. Copies your resume to the project as `resume.pdf`
4. Installs the `apply-job` skill to `~/.hermes/skills/career/apply-job/`
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
detection, length, tone, and personalization. Two independent critiques
feed into one verdict.

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
| `--format pdf` | `Resume.pdf`, `CoverLetter.pdf` | pandoc + wkhtmltopdf |

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
│ Extract      │ resume with  │ letter       │ 6 criteria      │
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
              ┌─────────────────────┐
              │ Convert (md/docx/pdf)│
              │ Present final output │
              └─────────────────────┘
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
  skills/
    apply-job/
      SKILL.md                ← The skill source
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
