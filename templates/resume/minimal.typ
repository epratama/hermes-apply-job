// minimal.typ — Maximum whitespace, nothing unnecessary
// Designed to get out of the way of the content. ATS-friendly.

#set page(margin: (x: 2.0cm, y: 1.8cm), paper: "us-letter")
#set text(font: ("Helvetica Neue", "Arial", "DejaVu Sans"), size: 10pt, fallback: true)
#set par(leading: 0.6em, justify: false)

// ── Header — clean, centered, no decoration ─────────────
#show heading.where(level: 1): it => {
  set align(center)
  set text(size: 20pt, weight: "bold")
  v(0.5em)
  it
  v(0.8em)
}

// ── Section headers — bold only, thin rule beneath ──────
#show heading.where(level: 2): it => {
  v(1.2em)
  set text(size: 10.5pt, weight: "bold")
  it
  v(0.2em)
  line(length: 100%, stroke: 0.4pt + rgb("cccccc"))
  v(0.4em)
}

// ── Job titles — bold, no extra spacing ─────────────────
#show heading.where(level: 3): it => {
  v(0.7em)
  set text(size: 10pt, weight: "bold")
  it
}

// ── Lists — clean spacing, no decoration ────────────────
#show list: it => {
  set par(leading: 0.35em)
  it
}

{{CONTENT}}
