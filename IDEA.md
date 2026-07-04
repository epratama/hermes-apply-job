# Resume Optimization Agent Consortium

A multi-agent pipeline orchestrated by Hermes Agent that uses Mixture of
Agents (MoA) presets and subagents to tailor your resume and cover letter
for a specific job listing, maximizing interview conversion.

## Setup

Run the setup script to install the skill and configure MoA presets:

```bash
python3 scripts/setup.py --resume <path-to-your-resume.pdf> [--format md|docx|pdf]
```

The script handles: installs the `apply-job` and `stop-slop` skills, MoA preset configuration, toolsets,
resume copying, and output format. Re-run anytime to update configuration.

See README.md for prerequisites and troubleshooting.

## Trigger

`/apply-job <job-listing-url>`

Implemented as a skill named `apply-job`. Once installed (via setup script),
invoke via `/apply-job https://example.com/jobs/12345`. Hermes reads the
skill and executes the pipeline.

## MoA Presets

Merge `config/moa-presets.yaml` into `~/.hermes/config.yaml` (the setup script
does this automatically). Each preset uses a different set of models optimized
for its role in the pipeline:

```yaml
moa:
  default_preset: default
  presets:
    resume-analyzer:
      reference_models:
        - provider: openrouter
          model: deepseek/deepseek-v4-flash
      aggregator:
        provider: openrouter
        model: deepseek/deepseek-v4-pro
      reference_max_tokens: 600

    resume-writer:
      reference_models:
        - provider: openrouter
          model: minimax/MiniMax-M3
        - provider: openrouter
          model: nvidia/nemotron-3-ultra
      aggregator:
        provider: openrouter
        model: deepseek/deepseek-v4-pro
      reference_max_tokens: 800

    resume-auditor:
      reference_models:
        - provider: openrouter
          model: minimax/MiniMax-M3
        - provider: openrouter
          model: nvidia/nemotron-3-ultra
      aggregator:
        provider: openrouter
        model: deepseek/deepseek-v4-pro
      reference_max_tokens: 600
```

| Role | Preset | References | Aggregator | Why |
|------|--------|-----------|------------|-----|
| Analyzer | `resume-analyzer` | V4 Flash | V4 Pro | Flash = fast cheap scanning; Pro = clean extraction |
| Writer | `resume-writer` | MiniMax M3 + Nemotron 3 Ultra | V4 Pro | MiniMax strong at narrative; Nemotron balances; Pro edits |
| Auditor | `resume-auditor` | MiniMax M3 + Nemotron 3 Ultra | V4 Pro | Two independent critical perspectives; Pro consolidates |

The `resume-writer` preset handles both resume drafting and cover letter
writing — same models, different prompts.

## Pipeline

Each step spawns a subagent. Per Hermes MoA behavior, subagents inherit the
parent session's model — the orchestrator explicitly switches to the target
MoA preset before spawning each subagent, then restores afterward.

All intermediate artifacts are saved for auditability: job analysis, auditor
reports per round, and draft versions.

### Step 1 — Job Analyzer (MoA: `resume-analyzer`)

Orchestrator switches to `resume-analyzer`, spawns subagent. Fetches the job
listing URL and extracts:
- Required and preferred skills, years of experience, tech stack
- Implied company culture, seniority level, must-mention keywords
- Role-specific responsibilities to map against your experience
- Any hard requirements (citizenship, clearance, location)

Saves structured analysis to `tailored-resumes/<company>-<role>/analysis.md`.
If the URL is inaccessible or contains no parseable job description, reports
the failure immediately and stops the pipeline.

### Step 2 — Resume Writer (MoA: `resume-writer`)

Orchestrator switches to `resume-writer`, spawns subagent. Takes the Job
Analyzer output + your base resume (`resume.pdf`). Produces a tailored
resume (`tailored-resumes/<company>-<role>/Resume.md`):
- Reorders bullet points so most relevant experience surfaces first
- Weaves JD keywords into descriptions naturally — no keyword stuffing
- De-emphasizes or trims experience not relevant to this role
- Keeps to 2 pages equivalent in markdown
- Uses the JD's language style (enterprise, startup, academic)

### Step 3 — Cover Letter Writer (MoA: `resume-writer`)

Orchestrator switches to `resume-writer`, spawns subagent (same MoA preset,
different prompt). Takes the same analysis + your resume. Produces a tailored
cover letter (`tailored-resumes/<company>-<role>/CoverLetter.md`):
- 3-4 paragraphs: opening hook, 2 body paragraphs mapping your top matches
  to their stated needs, closing with call to action
- Names the company and role explicitly — no generic templates
- If the JD does not name a hiring manager, use "Hiring Team" as salutation
- Addresses any obvious gap as a growth area, not an invention
- 1 page equivalent in markdown

### Step 4 — Auditor (MoA: `resume-auditor`)

Orchestrator switches to `resume-auditor`, spawns subagent. Scores both
documents on:
- **Keyword coverage** — ≥85% of JD keywords present (weighted by prominence)
- **ATS parsability** — standard section headings, no images/tables/icons,
  minimal formatting
- **No fabrication** — all claims traceable to `resume.pdf`
- **Length** — resume ≤2 pages, cover letter ≤1 page (markdown equivalent)
- **Tone** — professional, active voice, results-oriented
- **Personalization** — cover letter references specific JD details,
  not generic phrases
- **No AI slop** — scored on Directness, Rhythm, Trust, Authenticity,
  Density (1-10 per dimension, target ≥35/50). Flags filler phrases,
  adverbs, passive voice, em dashes, and formulaic structures

Saves the audit to `tailored-resumes/<company>-<role>/audit-round-<N>.md`.
Returns numeric score and line-item fixes.

### Step 5 — Consortium Loop

Writer(s) and Auditor iterate. Each round the Writer subagent addresses
flagged issues, the Auditor re-scores. Loop stops when:
- Overall score ≥90/100, or
- 3 rounds completed (take best score)

Hermes presents the final output with a summary of what changed and why.

### Step 6 — Convert & Present Results

Hermes reads the configured `output_format` from the skill config and converts:
- **md**: no conversion — `.md` files are the final output
- **docx**: pandoc converts `.md` to `.docx`
- **pdf**: pandoc + wkhtmltopdf converts `.md` to `.pdf`

If conversion tools are missing, Hermes reports the error and keeps the
`.md` output.

## Output

```
tailored-resumes/
  <company>-<role>/
    analysis.md                  # Job Analyzer output
    Resume.md / .docx / .pdf     # Final tailored resume
    CoverLetter.md / .docx / .pdf  # Final tailored cover letter
    audit-round-1.md             # Auditor reports per round
    audit-round-2.md             # (up to 3 rounds)
    audit-round-3.md
```

Only the format selected via `--format` is produced (not all three).

## Guardrails (Non-Negotiable)

- **Never fabricate** experience, degrees, certifications, or dates
- All achievements must be traceable to `resume.pdf`
- If a JD asks for something you genuinely lack:
  - Resume: do not mention it
  - Cover letter: acknowledge honestly as a growth area, not a skill you claim
- Use real contact info only — name, email, phone, LinkedIn from the base resume

## Error Handling

- **Inaccessible URL** — Job Analyzer reports failure, pipeline stops
- **Non-parseable JD** — Job Analyzer surfaces what it could extract, asks
  user to paste the JD manually
- **resume.pdf not found** — Pipeline stops with clear error
- **Auditor detects fabrication** — Flagged explicitly, Writer must remove
  before next round

## Base Resume

`resume.pdf` in the project root. This is your full work history — the source
of truth for all claims. Provided via `scripts/setup.py --resume <path>` and
gitignored to keep your personal data out of version control.
