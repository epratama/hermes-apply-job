---
name: apply-job
description: Tailor your resume and cover letter for a specific job listing using a multi-agent MoA consortium
version: 1.0.0
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [career, resume, job-search]
    category: career
    requires_toolsets: [terminal, delegation, web]
    config:
      - key: output_format
        description: "Output format for tailored documents"
        default: "md"
        prompt: "Output format (md, docx, or pdf)?"
---

# Apply Job — Resume & Cover Letter Tailoring

## When to Use

When the user wants to tailor their resume to a specific job listing.
Triggered via `/apply-job <job-listing-url>`.

The user's base resume is `resume.pdf` in the project root.

## MoA Presets

This skill depends on three MoA presets configured in `~/.hermes/config.yaml`:

- `resume-analyzer` — fast extraction (DeepSeek V4 Flash reference, V4 Pro aggregator)
- `resume-writer` — creative drafting (MiniMax M3 + Nemotron 3 Ultra references, V4 Pro aggregator)
- `resume-auditor` — critical scoring (MiniMax M3 + Nemotron 3 Ultra references, V4 Pro aggregator)

If these presets are not configured, stop and tell the user to add them.

## Procedure

You are the orchestrator. Execute each step in order. Switch MoA presets before spawning subagents.

### Step 0 — Pre-Flight Checks

1. Verify `resume.pdf` exists in the project root. If not, stop and tell the user to place it there.
2. Convert `resume.pdf` to text once (all subagents will use this file):
   Try `pdfplumber` first (Python library, always available):
   `python3 -c "
   import pdfplumber
   with pdfplumber.open('resume.pdf') as pdf:
       text = '\n'.join(p.extract_text() or '' for p in pdf.pages)
   open('/tmp/resume-base.txt', 'w').write(text)"`
   If `pdfplumber` fails, try `pdftotext`:
   `pdftotext resume.pdf /tmp/resume-base.txt`
   If neither tool is available, stop and tell the user: "Install pdfplumber
   (pip install pdfplumber) or pdftotext to extract text from your resume."

### Step 1 — Job Analyzer (max 2 retries)

1. Extract the job-listing URL from the `/apply-job` command argument.
2. Switch model to MoA preset `resume-analyzer`: `/model resume-analyzer --provider moa`
3. Spawn a subagent with toolsets `[terminal, web]`. Give it this exact prompt:

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

4. Wait for the subagent to finish. Verify `analysis.md` was created.
5. Extract the company name and role from the first two lines of `analysis.md`.
   These will be used as `<company>-<role>` in all subsequent steps.
6. Read `analysis.md` to confirm it's thorough. If it missed major sections (e.g., no
   responsibilities listed, no skills), re-spawn the analyzer with a reminder (max 2 attempts total).
   If the 2nd attempt also misses sections, continue with what's available.
7. Switch model back to your default: `/model default --provider moa`

### Step 2 — Resume Writer (max 1 retry)

1. Switch model to MoA preset `resume-writer`: `/model resume-writer --provider moa`
2. Spawn a subagent with toolsets `[terminal]`. Give it this exact prompt:

```
Read the job analysis at tailored-resumes/<company>-<role>/analysis.md.
Read the base resume text from /tmp/resume-base.txt.

Write a tailored resume saved to tailored-resumes/<company>-<role>/Resume.md.

Rules:
- Reorder bullet points so most relevant experience surfaces first
- Weave JD keywords into descriptions naturally — no keyword stuffing
- De-emphasize or trim experience not relevant to this role
- Keep to 2 pages equivalent in markdown
- Use the JD's language style (enterprise, startup, academic)
- NEVER fabricate experience, degrees, certifications, or dates
- All achievements must be traceable to /tmp/resume-base.txt
- Avoid AI writing patterns: no filler phrases, no adverbs, no passive voice, no em dashes, no vague declaratives
- If the JD asks for something the candidate genuinely lacks, do not mention it in the resume
- Use real contact info only from /tmp/resume-base.txt
- DO NOT add "targeting", "seeking", or "applying for" in the resume
  header. The tailoring should show through content, not a label.
- Each bullet is one achievement, not a paragraph. Split bullets that wrap
  beyond 2 lines. If splitting creates extra page space, trim the least
  relevant bullets rather than keeping dense text.
- Vary bullet length: some 1-line, some 2-line. Monotone rhythm = AI tell.
- Vary sentence openers — don't start every bullet with the same verb
  pattern (e.g., "Led...", "Designed...", "Built..."). Sound like a senior
  professional describing real work, not a template.
- Grammar must be flawless: proper articles (a/an/the), consistent tense
  (past for completed work, present for current role), no fragments.
```

3. Wait for the subagent to finish (max 1 retry if file not created). Verify the file was created.
4. Switch model back to default.

### Step 3 — Cover Letter Writer (max 1 retry)

1. Switch model to MoA preset `resume-writer`: `/model resume-writer --provider moa`
2. Spawn a subagent with toolsets `[terminal]`. Give it this exact prompt:

```
Read the job analysis at tailored-resumes/<company>-<role>/analysis.md.
Read the base resume text from /tmp/resume-base.txt.

Write a tailored cover letter saved to tailored-resumes/<company>-<role>/CoverLetter.md.

Rules:
- Keep it tight: 3 short paragraphs, 250-300 words total (~2/3 page in
  standard format). A letter that fills the page looks desperate — white
  space signals confidence. Do not pad to fill space.
- Paragraph 1: why this role caught your eye (2-3 sentences). No "I am
  writing to apply" — start mid-sentence if it sounds more human.
  Paragraph 2: your best match — one specific achievement tied to their
  stated need (3-4 sentences). Paragraph 3: call to action (2 sentences).
- Format: single-spaced paragraphs, blank line between each. No bullet
  points. No walls of text. Maximum 1 page — shorter is better.
- Name the company and role explicitly — no generic templates.
- If the JD does not name a hiring manager, use "Hiring Team" as salutation.
- Address any obvious gap as a growth area, not an invention.
- Grammar must be flawless. Read each sentence aloud — if it sounds like
  a template, rewrite it.
- NEVER fabricate experience or credentials
- All achievements must be traceable to /tmp/resume-base.txt
- Avoid AI writing patterns: no filler phrases, no adverbs, no passive voice, no em dashes, no vague declaratives
```

3. Wait for the subagent to finish (max 1 retry if file not created). Verify the file was created.
4. Switch model back to default.

### Step 4 — Auditor (max 1 retry)

1. Switch model to MoA preset `resume-auditor`: `/model resume-auditor --provider moa`
2. Spawn a subagent with toolsets `[terminal]`. Give it this exact prompt:

```
Read:
- tailored-resumes/<company>-<role>/analysis.md (job requirements)
- tailored-resumes/<company>-<role>/Resume.md (tailored resume)
- tailored-resumes/<company>-<role>/CoverLetter.md (tailored cover letter)
- /tmp/resume-base.txt (base resume — ground truth)

Audit both documents and save your report to tailored-resumes/<company>-<role>/audit-round-<N>.md
(where N is the round number, starting at 1).

Score each criteria from 0-100 and return an overall score (average of all):

1. Keyword Coverage: What % of JD keywords appear in the resume? (weighted by prominence in the JD)
   Target: ≥85. Deduct for every key skill/responsibility from the JD that is not reflected.

2. ATS Parsability: Standard section headings, no images/tables/icons, plain text.
   Deduct for any non-standard formatting, missing section labels, or complex structures.

3. No Fabrication: Cross-reference every claim in the resume and cover letter against /tmp/resume-base.txt.
   Deduct heavily for any claim not in the base resume. Flag exact fabricated lines.

4. Length: Resume ≤2 pages, cover letter ≤1 page (markdown equivalent, ~80 lines per page).
   Deduct proportionally for over-length documents.

5. Tone: Professional, reads like a human wrote it. Deduct for:
   - Passive voice, weak verbs, vague claims without metrics
   - Template language ("results-driven professional," "utilized cutting-edge")
   - Robotic formulaic phrasing (every bullet starts the same way)
   - Grammar errors, inconsistent tense, awkward constructions

6. Personalization: Cover letter references specific JD details, not generic phrases.
   Deduct for templated language, missing company/role name, generic closings.

7. No AI Slop (stop-slop): Score on five dimensions (1-10 each):
   - Directness: Statements or announcements?
   - Rhythm: Varied or metronomic sentence lengths?
   - Trust: Respects reader intelligence?
   - Authenticity: Sounds human?
   - Density: Anything cuttable?
   Convert: (total/50)*100. Target: ≥70 (35/50).
   Deduct for: filler phrases, passive voice, adverbs, formulaic structures,
   meta-commentary, business jargon, Wh- sentence starters, em dashes, vague
   declaratives, binary contrasts, dramatic fragmentation.

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
- Flagged claims: [list exact lines that aren't in /tmp/resume-base.txt]
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

### 7. No AI Slop: X/100
- Directness: [score/10]
- Rhythm: [score/10]
- Trust: [score/10]
- Authenticity: [score/10]
- Density: [score/10]
- Issues: [flagged AI patterns with line references]
- Fixes: [rewrite suggestions to sound more human]
```

3. Wait for the subagent to finish (max 1 retry if report not created).
4. Read the audit. If fabrication is detected, flag it to the user and
   proceed to the consortium loop (Step 5) regardless of score — do not
   skip to Step 6 until fabrication is resolved.
   If score ≥ 90 and no fabrication was detected, skip to Step 6.

### Step 5 — Consortium Loop

For rounds 2 and 3 (max 3 total rounds):

1. Read the previous audit report (`audit-round-<N-1>.md`).
2. Switch model to MoA preset `resume-writer`: `/model resume-writer --provider moa`
3. Spawn the resume writer subagent with this prompt (increment N for each round):

```
Read the latest audit at tailored-resumes/<company>-<role>/audit-round-<N-1>.md.
Read the current resume at tailored-resumes/<company>-<role>/Resume.md.
Read the current cover letter at tailored-resumes/<company>-<role>/CoverLetter.md.

Address every flagged issue from the audit. Apply all suggested fixes unless
they would introduce fabrication. Save updated versions of both files.

If the auditor flagged fabricated claims, REMOVE them — do not try to justify.
Also fix any AI writing patterns flagged by the auditor (filler phrases, adverbs, passive voice, em dashes).
```

4. Wait for the subagent to finish.
5. Switch model back to default.
6. Re-run the Auditor (Step 4, incrementing N).
7. If overall score ≥ 90, break out of the loop.
8. If this is round 3, stop and take the best score.

### Step 6 — Template Selection & PDF Generation

1. Read the configured `output_format` from the skill's config (default: `md`).

2. Convert based on the format:

   - **md**: no conversion. Present `.md` files as final output.
    - **docx**: `pandoc tailored-resumes/<company>-<role>/Resume.md -o tailored-resumes/<company>-<role>/Resume.docx` and same for CoverLetter. Done.
   - **pdf**: Generate with Typst templates (see sub-steps below).
       If `typst` is not installed, fall back to pandoc + wkhtmltopdf
       (single basic PDF, no template selection). Print install hint.

3. **PDF — Template generation** (when format is pdf and typst is available):

    a. Read `tailored-resumes/<company>-<role>/Resume.md`.
       The first `# ` heading is the candidate's name. The text between
       that heading and the first `## ` section header is the candidate's
       contact info (email, phone, location). Use these as `{{NAME}}` and
       `{{CONTACT}}`.

    b. Convert markdown to raw Typst:
       `pandoc tailored-resumes/<company>-<role>/Resume.md -t typst -o /tmp/resume-body.typ`
       `pandoc tailored-resumes/<company>-<role>/CoverLetter.md -t typst -o /tmp/cover-body.typ`

    c. For each template name: classic, modern, and minimal:
       - Read the template: `templates/resume/<name>.typ` and
         `templates/coverletter/<name>.typ`
       - Use string replacement: swap `{{NAME}}` with the candidate name,
         `{{CONTACT}}` with the contact info, `{{CONTENT}}` with the
         Typst body. Write the result to `/tmp/<name>-resume.typ` and
         `/tmp/<name>-cover.typ`.
        - Compile: `typst compile /tmp/<name>-resume.typ tailored-resumes/<company>-<role>/<name>-resume.pdf`
        - Same for cover: `typst compile /tmp/<name>-cover.typ tailored-resumes/<company>-<role>/<name>-coverletter.pdf`

       If `typst compile` fails for any template:
       - Print the error and skip that template
       - Delete the failed PDF file if it was partially created
       - Continue with the remaining templates
       - If ALL three templates fail, fall back to pandoc + wkhtmltopdf
         for a single basic PDF, keeping the markdown as backup

   d. Print selection prompt:

```
═══ Template Selection ═══

Pick a resume style. Open a link to preview:

1. classic  — Serif, traditional, horizontal rules
   Ref: https://typst.app/universe/package/moderner-cv

2. modern   — Sans-serif (Inter), blue accent, sidebar
   Ref: https://typst.app/universe/package/brilliant-cv

3. minimal  — Monochrome, hairline rules, ATS-friendly
   Ref: https://typst.app/universe/package/simple-technical-resume

PDFs ready at tailored-resumes/<company>-<role>/:
  classic-resume.pdf   classic-coverletter.pdf
  modern-resume.pdf    modern-coverletter.pdf
  minimal-resume.pdf   minimal-coverletter.pdf

Reply with the template name or number (1/2/3).
```

   e. Wait for user response. Match to template name.

   f. On selection:
      - Rename `<chosen>-resume.pdf` → `Resume.pdf`
      - Rename `<chosen>-coverletter.pdf` → `CoverLetter.pdf`
      - Delete the 4 PDFs for the two templates NOT chosen
      - If format is docx or pdf: delete the intermediate Resume.md and
        CoverLetter.md (final output is in the chosen format).
        Keep: analysis.md and all audit-round-*.md.

4. Print final summary:

```
<Company Name> — <Role Title>
Template: <chosen>
Final Audit Score: X/100 (Round N)
Files: tailored-resumes/<company>-<role>/Resume.pdf, CoverLetter.pdf
```

### Step 6g — Clean Temporary Files

Remove all temporary files (no prompt — automatic):

```
python3 -c "
import os, glob
files = ['/tmp/resume-base.txt', '/tmp/resume-body.typ', '/tmp/cover-body.typ']
for name in ['classic', 'modern', 'minimal']:
    files.append(f'/tmp/{name}-resume.typ')
    files.append(f'/tmp/{name}-cover.typ')
for f in files:
    try: os.remove(f)
    except FileNotFoundError: pass
"
print('Cleanup: removed temporary files')
```

## Pitfalls

- If MoA presets are not configured, stop early and tell the user: "MoA presets are missing. Run `python3 scripts/setup.py` to configure them."
- If `resume.pdf` is not found in the project root, stop and ask the user to place it there.
- Subagents timeout after 50 iterations by default. If a subagent times out, re-spawn it
  (respecting the max retry limit for that step) with a narrower scope.
- Fabrication is the hardest failure mode. Auditor must cross-reference every major claim
  against `/tmp/resume-base.txt`. If uncertain, flag it.
- The `<company>-<role>` slug is derived from the analysis. If the Analyzer fails to
  extract these, use a fallback like `job-<timestamp>`.
- If `typst` or `pandoc` is not installed when generating PDFs, fall back to markdown
  output and print the install command.
- If a template compile fails (`typst compile` error), the pipeline skips that template
  and continues with the remaining ones. If all fail, falls back to wkhtmltopdf.

## Verification

To test the pipeline:

1. Run `/apply-job <url>` with a known job listing
2. Verify all files are created in `tailored-resumes/`
3. Check the audit score
4. Review the tailored resume for accuracy (cross-reference against resume.pdf)
5. Run `/apply-job` with a different role/company to verify consistent behavior
