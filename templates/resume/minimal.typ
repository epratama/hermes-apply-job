// minimal.typ — Monochrome, hairline rules, maximum whitespace
// Inspired by: simple-technical-resume (ATS-friendly, one-page)

#set page(margin: (x: 2cm, y: 1.8cm), paper: "us-letter")
#set text(font: ("Helvetica Neue", "Arial", "DejaVu Sans"), size: 10pt, fallback: true)
#set par(leading: 0.6em)

// Section headers — simple bold, faint rule below
#show heading.where(level: 2): it => {
  v(1em)
  set text(size: 11pt, weight: "bold")
  it
  v(0.15em)
  line(length: 100%, stroke: 0.4pt + rgb("999999"))
  v(0.3em)
}

// Sub-headings — bold only
#show heading.where(level: 3): it => {
  v(0.6em)
  set text(size: 10pt, weight: "bold")
  it
}

// Lists — clean spacing
#show list: it => {
  set par(leading: 0.3em)
  it
}

// Title — simple, centered
#show heading.where(level: 1): it => {
  set align(center)
  set text(size: 18pt, weight: "bold")
  v(0.3em)
  it
  v(0.8em)
}

{{CONTENT}}
