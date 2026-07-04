# Resume Optimization Project

This project tailors your resume (`resume.pdf`) to specific job listings
using a multi-agent MoA consortium orchestrated by Hermes.

## How It Works

1. Run `python3 scripts/setup.py --resume <path> [--format md|docx|pdf]` to configure
2. Give Hermes `/apply-job <job-listing-url>`
3. Hermes orchestrates a pipeline: Job Analyzer → Resume Writer → Cover Letter Writer → Auditor → Consortium Loop
4. Tailored output lands in `tailored-resumes/<company>-<role>/`

## Key Files

- `resume.pdf` — your base resume (gitignored, provided via setup script)
- `IDEA.md` — full project spec with MoA presets and pipeline details
- `scripts/setup.py` — one-command setup (skill install + MoA config + resume copy)
- `config/moa-presets.yaml` — MoA model configuration
- `tailored-resumes/` — output directory, one subfolder per application

## Invocation

```
/apply-job https://example.com/jobs/12345
```

The `apply-job` skill is installed automatically by `scripts/setup.py`.

## MoA Presets

Configured via `scripts/setup.py`. Three presets defined in `config/moa-presets.yaml`:
`resume-analyzer`, `resume-writer`, `resume-auditor`.

See README.md for model details and customization instructions.

## Output Structure

```
tailored-resumes/<company>-<role>/
  analysis.md           # Job Analyzer output
  Resume.md             # Final tailored resume
  CoverLetter.md        # Final tailored cover letter
  audit-round-1.md      # Auditor reports per round (up to 3)
  audit-round-2.md
  audit-round-3.md
```

Output format (md, docx, or pdf) is selected at setup time via `--format`.

## Guardrails

- Never fabricate experience. All claims must be traceable to `resume.pdf`.
- If you lack a skill, acknowledge it honestly in the cover letter.
- Use real contact info only — name, email, phone, LinkedIn from `resume.pdf`.
- Output format is configured at setup. Default is markdown.
- Use the JD's language style.
