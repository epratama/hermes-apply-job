---
name: apply-job
description: Tailor your resume and cover letter for a specific job listing using a multi-agent MoA consortium
version: 2.0.0
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [career, resume, job-search]
    category: career
    requires_toolsets: [terminal, delegation, web]
---

# Apply Job — Resume & Cover Letter Tailoring

## When to Use

When the user wants to tailor their resume to a specific job listing.
Triggered via `/apply-job <job-listing-url>`.

The user's base resume is `resume.docx` in the project root.
The master document is never modified — templates only affect the tailored output.

## Style Preference

The user's style+format preference is saved after each run.
On subsequent runs, pressing Enter reuses the last saved choice.

## MoA Presets

This skill depends on three MoA presets configured in `~/.hermes/config.yaml`:

- `resume-analyzer` — fast extraction (DeepSeek V4 Flash reference, V4 Pro aggregator)
- `resume-writer` — creative drafting (MiniMax M3 + Nemotron 3 Ultra references, V4 Pro aggregator)
- `resume-auditor` — critical scoring (MiniMax M3 + Nemotron 3 Ultra references, V4 Pro aggregator)

If these presets are not configured, stop and tell the user to add them.

## Procedure

You are the orchestrator. Execute each step in order. Switch MoA presets before spawning subagents.
Do NOT run any pipeline steps until the user has chosen a style and format.

### Step 0 — Style & Format Selection

1. Before anything else, ask the user what style and output format they want.
   Show this prompt exactly:

```
═══════════════════════════════════════════════════════════════════════
               Choose Your Resume Style & Format
═══════════════════════════════════════════════════════════════════════

Styles:
  1. classic      Serif, traditional, horizontal rules
  2. modern       Sans-serif (Inter), subtle blue accent
  3. minimal      Clean monochrome, ATS-friendly, max whitespace
  4. keep mine    Preserve your master resume's existing style

Output format:
  docx           Editable in Word, Pages, LibreOffice
  pdf            Print-ready, locked layout

Which style and format?
  Reply: "2 docx" or "modern pdf" or "4"
```

2. Handle the user's response:

   **Direct pick** ("2 docx", "modern pdf", "4", etc.):
   - If format is missing (just a number or name), ask "DOCX or PDF?"
   - Proceed to Step 1

### Step 1 — Pre-Flight Checks

[Step 1 of 7] Verifying prerequisites (~5s)...
   `python -c "import tempfile; print(tempfile.gettempdir())"` — save the result.
    Use this path everywhere `<tempdir>/` is referenced below.
2. Verify `resume.docx` exists in the project root. If not, stop and tell the user to place it there.
3. Convert to text once (all subagents will use this file):
   `pandoc resume.docx -t plain --wrap=none -o <tempdir>/resume-base.txt`
   If pandoc is not available, stop and tell the user: "Pandoc is required.
   Install: https://pandoc.org/installing.html"
4. Scan `<tempdir>/resume-base.txt` for bracket placeholders like
   `[your.email@example.com]`, `[phone number]`, `[Company Name]`.
   If found, stop and tell the user: "Your resume contains template
   placeholders: <list them>. Replace with real content and re-run setup."

### Step 2 — Job Analyzer (max 2 retries)

[Step 2 of 7] Analyzing the job listing (~15s)...

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

### Step 3 — Resume Writer (max 1 retry)

[Step 3 of 7] Writing tailored resume (~45s)...

1. Switch model to MoA preset `resume-writer`: `/model resume-writer --provider moa`
2. Spawn a subagent with toolsets `[terminal]`. Give it this exact prompt:

```
Read the job analysis at tailored-resumes/<company>-<role>/analysis.md.
Read the base resume text from <tempdir>/resume-base.txt.

Write a tailored resume saved to tailored-resumes/<company>-<role>/Resume.md.

Rules:
- Reorder bullet points so most relevant experience surfaces first
- Weave JD keywords into descriptions naturally — no keyword stuffing
- De-emphasize or trim experience not relevant to this role
- Keep to 2 pages equivalent in markdown
- Use the JD's language style (enterprise, startup, academic)
- NEVER fabricate experience, degrees, certifications, or dates
- All achievements must be traceable to <tempdir>/resume-base.txt
- Avoid AI writing patterns: no filler phrases, no adverbs, no passive voice, no em dashes, no vague declaratives
- If the JD asks for something the candidate genuinely lacks, do not mention it in the resume
- Use real contact info only from <tempdir>/resume-base.txt
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

### Step 4 — Cover Letter Writer (max 1 retry)

[Step 4 of 7] Writing tailored cover letter (~30s)...

1. Switch model to MoA preset `resume-writer`: `/model resume-writer --provider moa`
2. Spawn a subagent with toolsets `[terminal]`. Give it this exact prompt:

```
Read the job analysis at tailored-resumes/<company>-<role>/analysis.md.
Read the base resume text from <tempdir>/resume-base.txt.

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
- All achievements must be traceable to <tempdir>/resume-base.txt
- Avoid AI writing patterns: no filler phrases, no adverbs, no passive voice, no em dashes, no vague declaratives
```

3. Wait for the subagent to finish (max 1 retry if file not created). Verify the file was created.
4. Switch model back to default.

### Step 5 — Auditor (max 1 retry)

[Step 5 of 7] Auditing documents (~30s)...

1. Switch model to MoA preset `resume-auditor`: `/model resume-auditor --provider moa`
2. Spawn a subagent with toolsets `[terminal]`. Give it this exact prompt:

```
Read:
- tailored-resumes/<company>-<role>/analysis.md (job requirements)
- tailored-resumes/<company>-<role>/Resume.md (tailored resume)
- tailored-resumes/<company>-<role>/CoverLetter.md (tailored cover letter)
- <tempdir>/resume-base.txt (base resume — ground truth)

Audit both documents and save your report to tailored-resumes/<company>-<role>/audit-round-<N>.md
(where N is the round number, starting at 1).

Score each criteria from 0-100 and return an overall score (average of all):

1. Keyword Coverage: What % of JD keywords appear in the resume? (weighted by prominence in the JD)
   Target: ≥85. Deduct for every key skill/responsibility from the JD that is not reflected.

2. ATS Parsability: Standard section headings, no images/tables/icons, plain text.
   Deduct for any non-standard formatting, missing section labels, or complex structures.

3. No Fabrication: Cross-reference every claim in the resume and cover letter against <tempdir>/resume-base.txt.
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
- Flagged claims: [list exact lines that aren't in <tempdir>/resume-base.txt]
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
   proceed to the consortium loop (Step 6) regardless of score — do not
   skip to Step 7 until fabrication is resolved.
   If score ≥ 90 and no fabrication was detected, skip to Step 7.

### Step 6 — Consortium Loop

[Step 6 of 7] Consortium loop — iterating on feedback (~2 min/round)...

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
6. Re-run the Auditor (Step 5, incrementing N).
7. If overall score ≥ 90, break out of the loop.
8. If this is round 3, stop and take the best score.

### Step 7 — Generate Styled Output

[Step 7 of 7] Generating styled output (~10s)...

Apply the user's chosen style from Step 0 to generate the final output.

1. Get the design system for the chosen style:

   - **Styles 1-3 (classic/modern/minimal)**: Run UI-UX-Pro-Max:
     `python skills/ui-ux-pro-max/scripts/search.py "resume <keywords>" --design-system`
     Extract colors, fonts, spacing from the design system output.

   - **Style 4 (keep mine)**: Extract `resume.docx` style:
     `python -c "import docx; d=docx.Document('resume.docx'); n=d.styles['Normal']; hs=[s for s in d.styles if s.type==1]; h=hs[0] if hs else n; print(f'{n.font.name}|{n.font.size}|{h.font.name}|{n.font.color.rgb}')"`
     Parse: body-font | body-size | heading-font | accent-color.
     Use these as the design system for the styled output.

   - **Custom URL**: Use the design system extracted during Step 0 preview.

2. Generate HTML from markdown:
   `pandoc tailored-resumes/<company>-<role>/Resume.md -t html5 -o <tempdir>/resume.html`
   `pandoc tailored-resumes/<company>-<role>/CoverLetter.md -t html5 -o <tempdir>/cover.html`

3. Inject the design system as CSS into the HTML using `templates/resume/base.html`
   and `templates/resume/cover-base.html` as the foundation.

4. Convert to the user's chosen format:
   - **DOCX**: `pandoc <tempdir>/resume.html -o tailored-resumes/<company>-<role>/Resume.docx`
   - **PDF**: `weasyprint <tempdir>/resume.html tailored-resumes/<company>-<role>/Resume.pdf`
   - Same for cover letter.

   If weasyprint is not available, try `python -c "import weasyprint"`
   or fall back to pandoc + wkhtmltopdf for PDF.

5. Print final summary:

```
═══════════════════════════════════════════════════════════════════════
                             Done
═══════════════════════════════════════════════════════════════════════

<Company Name> — <Role Title>
Style: <chosen> | Format: <format> | Score: X/100

📍 tailored-resumes/<company>-<role>/
     Resume.<format>
     CoverLetter.<format>
     analysis.md
     audit-round-1.md (up to 3)
```

6. Clean temporary files: remove `<tempdir>/resume-base.txt`, `<tempdir>/*.html`, previews.
   Do not remove `tailored-resumes/` contents.

## Pitfalls

- If MoA presets are not configured, stop early and tell the user: "MoA presets are missing. Run `python scripts/setup.py` to configure them."
- If `resume.docx` is not found in the project root, stop and ask the user to place it there.
- Subagents timeout after 50 iterations by default. If a subagent times out, re-spawn it
  (respecting the max retry limit for that step) with a narrower scope.
- Fabrication is the hardest failure mode. Auditor must cross-reference every major claim
  against `<tempdir>/resume-base.txt`. If uncertain, flag it.
- The `<company>-<role>` slug is derived from the analysis. If the Analyzer fails to
  extract these, use a fallback like `job-<timestamp>`.
- If pandoc is not installed, stop and tell the user: "Pandoc is required. Install: https://pandoc.org/installing.html"
- If the user's chosen style generates visual errors, fall back to the default modern style.

## Verification

To test the pipeline:

1. Run `/apply-job <url>` with a known job listing
2. Verify all files are created in `tailored-resumes/`
3. Check the audit score
4. Review the tailored resume for accuracy (cross-reference against resume.docx)
5. Run `/apply-job` with a different role/company to verify consistent behavior
