# Resume Optimization Project

This project tailors your resume (`resume.docx`) to specific job listings
using a multi-agent MoA consortium orchestrated by Hermes.

## How It Works

1. Run `python3 scripts/setup.py [--resume <path>]` to configure
2. Give Hermes `/apply-job <job-listing-url>`
3. Hermes orchestrates a pipeline: Step 0 (Style+Format) → Step 1 (Pre-Flight) → Job Analyzer → Resume Writer → Cover Letter Writer → Auditor → Consortium Loop → Step 7 (Generate Output)
4. Tailored output lands in `tailored-resumes/<company>-<role>/`

## Key Files

- `resume.docx` — your base resume (gitignored, provided via setup script)
- `IDEA.md` — full project spec with MoA presets and pipeline details
- `scripts/setup.py` — one-command setup (skill install + MoA config + resume copy)
- `config/moa-presets.yaml` — MoA model configuration
- `templates/resume/` — HTML templates (base.html, cover-base.html)
- `tailored-resumes/` — output directory, one subfolder per application
- `tests/test_setup.py` — setup script self-check tests

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
  analysis.md              # Job Analyzer output
  Resume.md                # Final tailored resume (markdown source)
  CoverLetter.md           # Final tailored cover letter (markdown source)
  Resume.<docx|pdf>        # Styled output (format chosen at Step 0)
  CoverLetter.<docx|pdf>   # Styled output (format chosen at Step 0)
  audit-round-1.md         # Auditor reports per round (up to 3)
  audit-round-2.md
  audit-round-3.md
```

Output format is chosen at runtime in Step 0 (docx or pdf), not at setup time.

## Guardrails

- Never fabricate experience. All claims must be traceable to `resume.docx`.
- If you lack a skill, acknowledge it honestly in the cover letter.
- Use real contact info only — name, email, phone, LinkedIn from `resume.docx`.
- Use the JD's language style.
