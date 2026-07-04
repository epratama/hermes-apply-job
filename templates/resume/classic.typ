// classic.typ — Traditional serif resume with horizontal rules
// Inspired by: moderncv (https://typst.app/universe/package/moderner-cv)

#set page(margin: (x: 2.2cm, y: 2cm), paper: "us-letter")
#set text(font: "New Computer Modern", size: 10.5pt, fallback: true)
#set par(leading: 0.55em, justify: true)

// Header — candidate name + contact
#show heading.where(level: 1): it => {
  set align(center)
  set text(size: 22pt, weight: "bold")
  v(0.5em)
  it
  v(0.3em)
}

// Section headers — uppercase, ruled below
#show heading.where(level: 2): it => {
  v(1.2em)
  set text(size: 11pt, weight: "bold")
  smallcaps(it)
  v(0.3em)
  line(length: 100%, stroke: 0.8pt + black)
  v(0.3em)
}

// Sub-headings (job titles) — bold, no extra spacing
#show heading.where(level: 3): it => {
  v(0.8em)
  set text(size: 10.5pt, weight: "bold")
  it
}

// Bullet lists — tight spacing for dense experience
#show list: it => {
  set par(leading: 0.35em)
  it
}

// Contact info styling
#show par.where(block: false): it => {}

{{CONTENT}}
