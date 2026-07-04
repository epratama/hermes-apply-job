// modern.typ — Clean sans-serif resume with accent color and spacing discipline
// Designed to look professional, modern, and human — not AI-generated.

#let accent = rgb("2563eb")    // blue
#let muted  = rgb("555555")
#let dark   = rgb("1a1a1a")

#set page(margin: (x: 2.2cm, y: 1.8cm), paper: "us-letter")
#set text(font: ("Inter", "Helvetica Neue", "Arial"), size: 10pt, fallback: true)
#set par(leading: 0.55em, justify: false)

// ── Header — bold name, muted contact on two lines ──────
#show heading.where(level: 1): it => {
  set align(center)
  set text(size: 24pt, weight: "bold", fill: dark)
  v(0.8em)
  it
  v(0.15em)
  line(length: 25%, stroke: 1.2pt + accent)
  v(0.7em)
}

// ── Section headers — uppercase, accent color, crisp rule ──
#show heading.where(level: 2): it => {
  v(1.3em)
  set text(size: 10.5pt, weight: "bold", fill: accent)
  text(tracking: 2.5pt)[#smallcaps(it)]
  v(0.25em)
  line(length: 100%, stroke: 1pt + accent)
  v(0.4em)
}

// ── Job titles — bold, with muted date/company on next line ──
#show heading.where(level: 3): it => {
  v(0.8em)
  set text(size: 10.5pt, weight: "bold", fill: dark)
  it
}

// ── Bullet lists — tight, readable, with accent markers ──
#show list: it => {
  set par(leading: 0.4em)
  set text(size: 10pt, fill: rgb("333333"))
  it
}

// ── Contact line — auto-styled by heading(level: 1) ─────
#show par: set text(fill: rgb("333333"))

{{CONTENT}}
