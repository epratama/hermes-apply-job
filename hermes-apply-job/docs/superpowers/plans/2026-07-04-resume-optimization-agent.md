# Resume Optimization Agent Consortium Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a Hermes Agent skill (`/apply-job`) that orchestrates a multi-agent MoA consortium to tailor your resume and cover letter for a specific job listing.

**Architecture:** A Hermes skill (`apply-job`) loaded as a slash command. Hermes acts as the orchestrator — switching MoA presets between steps, spawning subagents for each role (Analyzer, Writer, Auditor), and running a consortium loop for iterative improvement. Project context lives in `AGENTS.md`. MoA presets are configured in `~/.hermes/config.yaml`.

**Tech Stack:** Hermes Agent skills system, Mixture of Agents (MoA), subagent delegation, markdown for output.

## Global Constraints

- Output: `tailored-resumes/<company>-<role>/Resume.md` and `CoverLetter.md`
- Base resume: `master-resume.pdf` in project root
- Never fabricate experience — all claims must be traceable to `master-resume.pdf`
- 3 MoA presets: `resume-analyzer`, `resume-writer`, `resume-auditor`
- Auditor scores resume + cover letter on keyword coverage, ATS, fabrication, length, tone, personalization
- Consortium loop: iterate until score ≥90 or 3 rounds completed
- PDF conversion is a manual step after markdown is final

---

### Task 1: Project Context (AGENTS.md)

**Files:**
- Create: `AGENTS.md`

**Interfaces:**
- Consumes: `IDEA.md` (spec document, not loaded by Hermes)
- Produces: Project context that Hermes auto-loads when in this directory

- [ ] **Step 1: Write AGENTS.md**

```markdown
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
  Resume.md
  CoverLetter.md
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
```

- [ ] **Step 2: Verify Hermes can discover it**

Run: `ls -la AGENTS.md`
Expected: file exists and is readable

- [ ] **Step 3: Init git and commit**

```bash
git init
git add AGENTS.md IDEA.md
git commit -m "feat: initial commit — resume optimization project spec and context"
```

---

### Task 2: Output Directory

**Files:**
- Create: `tailored-resumes/.gitkeep`

**Interfaces:**
- Produces: Output directory for tailored resumes

- [ ] **Step 1: Create directory**

```bash
mkdir -p tailored-resumes
```

- [ ] **Step 2: Verify**

```bash
ls -la tailored-resumes/
```
Expected: empty directory exists

- [ ] **Step 3: Commit**

```bash
git add tailored-resumes/
git commit -m "feat: add tailored-resumes output directory"
```

---

### Task 3: MoA Preset Configuration

**Files:**
- Modify: `~/.hermes/config.yaml` (user runs this manually)

**Interfaces:**
- Consumes: None
- Produces: Three MoA presets available to the model picker

- [ ] **Step 1: Document the MoA snippet**

User adds this to `~/.hermes/config.yaml` under the existing `moa:` key (or creates the section):

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

- [ ] **Step 2: Verify presets are registered**

Run: `hermes moa list`
Expected: `resume-analyzer`, `resume-writer`, `resume-auditor` appear in the list

---

### Task 4: Apply-Job Skill (SKILL.md)

**Files:**
- Create: `~/.hermes/skills/career/apply-job/SKILL.md`

**Interfaces:**
- Consumes: MoA presets (`resume-analyzer`, `resume-writer`, `resume-auditor`), `master-resume.pdf`
- Produces: Slash command `/apply-job <url>` that runs the full pipeline

- [ ] **Step 1: Write the SKILL.md**

```markdown
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

If the URL is inaccessible or the page has no parseable job description,
report the failure to the parent and do not create any files.
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

Write a tailored resume saved to tailored-resumes/<company>-<role>/Resume.md.

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

Write a tailored cover letter saved to tailored-resumes/<company>-<role>/CoverLetter.md.

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
- tailored-resumes/<company>-<role>/Resume.md (tailored resume)
- tailored-resumes/<company>-<role>/CoverLetter.md (tailored cover letter)
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
2. Give the resume writer subagent this prompt (increment N for each round):

```
Read the latest audit at tailored-resumes/<company>-<role>/audit-round-<N-1>.md.
Read the current resume at tailored-resumes/<company>-<role>/Resume.md.
Read the current cover letter at tailored-resumes/<company>-<role>/CoverLetter.md.

Address every flagged issue from the audit. Apply all suggested fixes unless
they would introduce fabrication. Save updated versions of both files.

If the auditor flagged fabricated claims, REMOVE them — do not try to justify.
```

3. Wait for the subagent to finish.
4. Re-run the Auditor (Step 4, incrementing N).
5. If overall score ≥ 90, break out of the loop.
6. If this is round 3, stop and take the best score.

### Step 6 — Present Results

1. Print a summary:

```
Resume and cover letter ready for <Company Name> — <Role Title>.

Files:
  tailored-resumes/<company>-<role>/Resume.md
  tailored-resumes/<company>-<role>/CoverLetter.md

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
```

- [ ] **Step 2: Install the skill**

```bash
mkdir -p ~/.hermes/skills/career/apply-job
# Write the SKILL.md content from Step 1 to ~/.hermes/skills/career/apply-job/SKILL.md
```

- [ ] **Step 3: Verify the skill is registered**

Run: `hermes skills list | grep apply-job`
Expected: `apply-job` appears in the list with description "Tailor your resume and cover letter..."

- [ ] **Step 4: Dry-run test**

```bash
# In the project directory, start Hermes and run:
/apply-job https://example.com/jobs/sample
```
Expected: Hermes reads the skill, begins the pipeline with Job Analyzer. Stop after verification.

---

### Task 5: End-to-End Verification

**Files:**
- None (test only)

**Interfaces:**
- Consumes: All prior tasks

- [ ] **Step 1: Run the full pipeline**

In the project directory, start Hermes and run:
```
/apply-job https://boards.greenhouse.io/example/jobs/12345
```
(Use a real, accessible job listing URL)

- [ ] **Step 2: Verify output files exist**

```bash
ls -la tailored-resumes/<company>-<role>/
```
Expected: `analysis.md`, `Resume.md`, `CoverLetter.md`, at least one `audit-round-*.md`

- [ ] **Step 3: Verify guardrails**

```bash
# Check no fabricated claims — spot-check 3 claims against master-resume.pdf
python3 -c "
import pdfplumber
with pdfplumber.open('master-resume.pdf') as pdf:
    base_text = ' '.join([p.extract_text() or '' for p in pdf.pages])
# Read tailored resume and check key phrases exist in base_text
"
```

- [ ] **Step 4: Verify audit quality**

Read the audit report. Confirm it:
- Lists specific missing keywords (not just a score)
- Cross-references claims against the base resume
- Provides actionable fixes, not vague suggestions
- Has a numeric overall score

- [ ] **Step 5: Commit (if in git repo)**

```bash
git status
# If git repo initialized, commit verification results or .gitignore
```
