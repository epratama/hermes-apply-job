# Resume Optimization Project

This project tailors my resume (`master-resume.pdf`) to specific job listings
using a multi-agent MoA consortium orchestrated by Hermes.

## How It Works

1. I give Hermes `/apply-job <job-listing-url>`
2. Hermes orchestrates a pipeline: Job Analyzer → Resume Writer → Cover Letter Writer → Auditor → Consortium Loop
3. Tailored output lands in `tailored-resumes/<company>-<role>/`

## Key Files

- `master-resume.pdf` — my base resume (source of truth, 15+ years SWE)
- `IDEA.md` — full project spec with MoA presets and pipeline details
- `tailored-resumes/` — output directory, one subfolder per application

## Invocation

```
/apply-job https://example.com/jobs/12345
```

The `apply-job` skill must be installed in `~/.hermes/skills/career/apply-job/SKILL.md`.

## MoA Presets

See `IDEA.md` for the YAML config. Add to `~/.hermes/config.yaml` under `moa.presets`.
Three presets: `resume-analyzer`, `resume-writer`, `resume-auditor`.

## Output Structure

```
tailored-resumes/<company>-<role>/
  analysis.md           # Job Analyzer output
  Eky_Pratama_Resume.md
  Eky_Pratama_CoverLetter.md
  audit-round-1.md      # Auditor reports per round (up to 3)
  audit-round-2.md
  audit-round-3.md
```

## Guardrails

- Never fabricate experience. All claims must be traceable to `master-resume.pdf`.
- If I lack a skill, acknowledge it honestly in the cover letter.
- Output is markdown. PDF conversion is manual (ask Hermes when ready).
- Use the JD's language style.

## My Models

All via OpenRouter:
- `deepseek/deepseek-v4-pro` — primary/aggregator
- `deepseek/deepseek-v4-flash` — fast scanning
- `minimax/MiniMax-M3` — creative writing reference
- `nvidia/nemotron-3-ultra` — second opinion reference
