// modern-cover.typ — Sans-serif cover letter with accent
#set page(margin: (x: 2.2cm, y: 2cm), paper: "us-letter")
#set text(font: ("Inter", "Helvetica Neue", "Arial"), size: 10.5pt, fallback: true)
#set par(leading: 0.6em)

#let accent = rgb("2563eb")

#show heading.where(level: 1): it => {
  set align(right)
  set text(size: 14pt, weight: "bold", fill: accent)
  it
  v(0.1em)
  line(length: 100%, stroke: 1pt + accent)
  v(1em)
}

{{CONTENT}}
