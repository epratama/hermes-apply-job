---
name: apply-job
description: Tailor your resume and cover letter for a specific job listing using a multi-agent MoA consortium
version: 1.0.0
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [career, resume, job-search]
    category: career
    requires_toolsets: [terminal, delegation]
---

# Apply Job — Resume & Cover Letter Tailoring

## When to Use

When the user wants to tailor their master resume to a specific job listing.
Triggered via `/apply-job <job-listing-url>`.

The user's base resume is `master-resume.pdf` in the project root.

## MoA Presets

This skill depends on three MoA presets configured in `~/.hermes/config.yaml`:

- `resume-analyzer` — fast extraction (DeepSeek V4 Flash reference, V4 Pro aggregator)
- `resume-writer` — creative drafting (MiniMax M3 + Nemotron 3 Ultra references, V4 Pro aggregator)
- `resume-auditor` — critical scoring (MiniMax M3 + Nemotron 3 Ultra references, V4 Pro aggregator)

If these presets are not configured, stop and tell the user to add them.

## Procedure

You are the orchestrator. Execute each step in order. Switch MoA presets before spawning subagents.

### Step 1 — Job Analyzer

1. Extract the job-listing URL from the `/apply-job` command argument.
2. Verify `master-resume.pdf` exists in the project root. If not, stop and tell the user to place it there.
3. Switch model to MoA preset `resume-analyzer`: `/model resume-analyzer --provider moa`
4. Spawn a subagent with toolsets `[terminal, web]`. Give it this exact prompt:

```
Read the job listing at <URL>. Extract the company name and role title first,
then create the output directory: tailored-resumes/<company>-<role>/

Save the full analysis to tailored-resumes/<company>-<role>/analysis.md with:
- Company name, role title, location, workplace type (remote/hybrid/onsite)
- All required skills, preferred skills, years of experience, tech stack
- Role-specific responsibilities (every one listed in the JD)
- Implied company culture, seniority level, must-mention keywords
- Any hard requirements (citizenship, clearance, location)

The first two lines of the file must be:
# Company: <Company Name>
# Role: <Role Title>

Be thorough. Do not summarize — list everything.

If the URL is inaccessible, report the failure to the parent and do not create any files.
If the JD is partially parseable, extract what you can, clearly note what is missing,
and save the partial analysis. The orchestrator will ask the user to paste the full JD.
```

5. Wait for the subagent to finish. Verify `analysis.md` was created.
6. Extract the company name and role from the first two lines of `analysis.md`.
   These will be used as `<company>-<role>` in all subsequent steps.
7. Read `analysis.md` to confirm it's thorough. If it missed major sections (e.g., no responsibilities listed, no skills), re-spawn the analyzer with a reminder to be thorough.
8. Switch model back to your default: `/model default --provider moa`

### Step 2 — Resume Writer

1. Switch model to MoA preset `resume-writer`: `/model resume-writer --provider moa`
2. Spawn a subagent with toolsets `[terminal]`. Give it this exact prompt:

```
Read the job analysis at tailored-resumes/<company>-<role>/analysis.md.
Read the base resume at master-resume.pdf.

Write a tailored resume saved to tailored-resumes/<company>-<role>/Eky_Pratama_Resume.md.

Rules:
- Reorder bullet points so most relevant experience surfaces first
- Weave JD keywords into descriptions naturally — no keyword stuffing
- De-emphasize or trim experience not relevant to this role
- Keep to 2 pages equivalent in markdown
- Use the JD's language style (enterprise, startup, academic)
- NEVER fabricate experience, degrees, certifications, or dates
- All achievements must be traceable to master-resume.pdf
- If the JD asks for something the candidate genuinely lacks, do not mention it in the resume
- Use real contact info only from master-resume.pdf
```

3. Wait for the subagent to finish. Verify the file was created.
4. Switch model back to default.

### Step 3 — Cover Letter Writer

1. Switch model to MoA preset `resume-writer`: `/model resume-writer --provider moa`
2. Spawn a subagent with toolsets `[terminal]`. Give it this exact prompt:

```
Read the job analysis at tailored-resumes/<company>-<role>/analysis.md.
Read the base resume at master-resume.pdf.

Write a tailored cover letter saved to tailored-resumes/<company>-<role>/Eky_Pratama_CoverLetter.md.

Rules:
- 3-4 paragraphs: opening hook, 2 body paragraphs mapping top candidate matches to the role's stated needs, closing with call to action
- Name the company and role explicitly — no generic templates
- If the JD does not name a hiring manager, use "Hiring Team" as salutation
- Address any obvious gap as a growth area, not an invention
- 1 page equivalent in markdown
- NEVER fabricate experience or credentials
- All achievements must be traceable to master-resume.pdf
```

3. Wait for the subagent to finish. Verify the file was created.
4. Switch model back to default.

### Step 4 — Auditor

1. Switch model to MoA preset `resume-auditor`: `/model resume-auditor --provider moa`
2. Spawn a subagent with toolsets `[terminal]`. Give it this exact prompt:

```
Read:
- tailored-resumes/<company>-<role>/analysis.md (job requirements)
- tailored-resumes/<company>-<role>/Eky_Pratama_Resume.md (tailored resume)
- tailored-resumes/<company>-<role>/Eky_Pratama_CoverLetter.md (tailored cover letter)
- master-resume.pdf (base resume — ground truth)

Audit both documents and save your report to tailored-resumes/<company>-<role>/audit-round-<N>.md
(where N is the round number, starting at 1).

Score each criteria from 0-100 and return an overall score (average of all):

1. Keyword Coverage: What % of JD keywords appear in the resume? (weighted by prominence in the JD)
   Target: ≥85. Deduct for every key skill/responsibility from the JD that is not reflected.

2. ATS Parsability: Standard section headings, no images/tables/icons, plain text.
   Deduct for any non-standard formatting, missing section labels, or complex structures.

3. No Fabrication: Cross-reference every claim in the resume and cover letter against master-resume.pdf.
   Deduct heavily for any claim not in the base resume. Flag exact fabricated lines.

4. Length: Resume ≤2 pages, cover letter ≤1 page (markdown equivalent, ~80 lines per page).
   Deduct proportionally for over-length documents.

5. Tone: Professional, active voice, results-oriented.
   Deduct for passive voice, weak verbs, vague claims without metrics.

6. Personalization: Cover letter references specific JD details, not generic phrases.
   Deduct for templated language, missing company/role name, generic closings.

Output format:

## Audit Report — Round N

### Overall Score: X/100

### 1. Keyword Coverage: X/100
- Missing keywords: [list]
- Suggestions: [list]

### 2. ATS Parsability: X/100
- Issues: [list]
- Fixes: [list]

### 3. No Fabrication: X/100
- Flagged claims: [list exact lines that aren't in master-resume.pdf]
- Verdict: [pass if none, fail with details otherwise]

### 4. Length: X/100
- Current: [lines/pages]
- Actions: [what to cut if overlength]

### 5. Tone: X/100
- Issues: [list weak verbs, passive constructions]
- Fixes: [specific rewrites suggested]

### 6. Personalization: X/100
- Issues: [generic phrases found]
- Fixes: [specific JD details to reference instead]
```

3. Wait for the subagent to finish.
4. Read the audit. If score ≥ 90, skip to Step 6.
5. If fabrication is detected, flag it to the user before proceeding.

### Step 5 — Consortium Loop

For rounds 2 and 3 (max 3 total rounds):

1. Read the previous audit report (`audit-round-<N-1>.md`).
2. Switch model to MoA preset `resume-writer`: `/model resume-writer --provider moa`
3. Spawn the resume writer subagent with this prompt (increment N for each round):

```
Read the latest audit at tailored-resumes/<company>-<role>/audit-round-<N-1>.md.
Read the current resume at tailored-resumes/<company>-<role>/Eky_Pratama_Resume.md.
Read the current cover letter at tailored-resumes/<company>-<role>/Eky_Pratama_CoverLetter.md.

Address every flagged issue from the audit. Apply all suggested fixes unless
they would introduce fabrication. Save updated versions of both files.

If the auditor flagged fabricated claims, REMOVE them — do not try to justify.
```

4. Wait for the subagent to finish.
5. Switch model back to default.
6. Re-run the Auditor (Step 4, incrementing N).
7. If overall score ≥ 90, break out of the loop.
8. If this is round 3, stop and take the best score.

### Step 6 — Present Results

1. Print a summary:

```
Resume and cover letter ready for <Company Name> — <Role Title>.

Files:
  tailored-resumes/<company>-<role>/Eky_Pratama_Resume.md
  tailored-resumes/<company>-<role>/Eky_Pratama_CoverLetter.md

Final Audit Score: X/100 (Round N)

Key changes from base resume:
- [2-3 bullet points summarizing what was emphasized/reordered]

To convert to PDF, reply: "convert to PDF"
```

## Pitfalls

- If MoA presets are not configured, stop early and tell the user: "MoA presets are missing. Add `resume-analyzer`, `resume-writer`, and `resume-auditor` to `~/.hermes/config.yaml`. See IDEA.md for the snippet."
- If `master-resume.pdf` is not found in the project root, stop and ask the user to place it there.
- Subagents timeout after 50 iterations by default. Complex audits may need more. If a subagent times out, re-spawn it with a narrower scope.
- Fabrication is the hardest failure mode. Auditor must cross-reference every major claim against `master-resume.pdf`. If uncertain, flag it.
- The `<company>-<role>` slug is derived from the analysis. If the Analyzer fails to extract these, use a fallback like `job-<timestamp>`.

## Verification

To test the pipeline:

1. Run `/apply-job <url>` with a known job listing
2. Verify all files are created in `tailored-resumes/`
3. Check the audit score
4. Review the tailored resume for accuracy (cross-reference against master-resume.pdf)
5. Run `/apply-job` with a different role/company to verify consistent behavior
