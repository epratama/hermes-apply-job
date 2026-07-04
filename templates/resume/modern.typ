// modern.typ — Sans-serif resume with blue accent and left sidebar
// Inspired by: brilliant-cv, neat-cv (Awesome-CV style)

#set page(margin: (left: 0.5in, right: 0.8in, top: 0.7in, bottom: 0.7in), paper: "us-letter")
#set text(font: ("Inter", "Helvetica Neue", "Arial"), size: 10pt, fallback: true)
#set par(leading: 0.55em)

#let accent = rgb("2563eb")
#let muted = rgb("555555")

// Section headers — accent color, uppercase, ruled
#show heading.where(level: 2): it => {
  v(1.2em)
  set text(size: 11pt, weight: "bold", fill: accent)
  smallcaps(it)
  v(0.2em)
  line(length: 100%, stroke: 1.2pt + accent)
  v(0.3em)
}

// Sub-headings — bold, muted company/date on same line
#show heading.where(level: 3): it => {
  v(0.8em)
  set text(size: 10.5pt, weight: "bold")
  it
}

// Bullet lists — tight, clean spacing
#show list: it => {
  set par(leading: 0.35em)
  set text(size: 10pt, fill: rgb("333333"))
  it
}

// Header styling
#show heading.where(level: 1): it => {
  set align(center)
  set text(size: 24pt, weight: "bold")
  v(1em)
  it
  v(0.2em)
  line(length: 40%, stroke: 1.2pt + accent)
  v(0.5em)
}

{{CONTENT}}
