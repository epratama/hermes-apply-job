// classic.typ — Traditional serif resume with crisp typography
// Styled to look professional and human, not AI-generated.

#set page(margin: (x: 2.2cm, y: 1.8cm), paper: "us-letter")
#set text(font: ("New Computer Modern", "Latin Modern Roman", "Georgia", "Times New Roman"), size: 10.5pt, fallback: true)
#set par(leading: 0.6em, justify: false)

// ── Header (candidate name + contact) ───────────────────
#show heading.where(level: 1): it => {
  set align(center)
  set text(size: 22pt, weight: "bold")
  v(0.8em)
  it
  v(0.15em)
  line(length: 30%, stroke: 1.2pt + black)
  v(0.8em)
}

// ── Section headers ─────────────────────────────────────
#show heading.where(level: 2): it => {
  v(1.4em)
  set text(size: 11pt, weight: "bold")
  text(tracking: 2pt)[#smallcaps(it)]
  v(0.3em)
  line(length: 100%, stroke: 0.7pt + black)
  v(0.4em)
}

// ── Job titles / subheadings ────────────────────────────
#show heading.where(level: 3): it => {
  v(0.9em)
  set text(size: 10.5pt, weight: "bold")
  it
}

// ── Bullet lists — readable, not cramped ────────────────
#show list: it => {
  set par(leading: 0.45em)
  it
}

// ── Paragraphs (for descriptions, dates) ────────────────
#show par: set par(leading: 0.55em)

{{CONTENT}}
