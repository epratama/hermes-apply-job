// minimal-cover.typ — Monochrome cover letter, maximum whitespace

#set page(margin: (x: 2.0cm, y: 1.8cm), paper: "us-letter")
#set text(font: ("Helvetica Neue", "Arial", "DejaVu Sans"), size: 10.5pt, fallback: true)
#set par(leading: 0.65em, justify: false)

#show heading.where(level: 1): it => {
  set align(right)
  set text(size: 14pt, weight: "bold")
  it
  v(0.1em)
  line(length: 100%, stroke: 0.4pt + rgb("cccccc"))
  v(1em)
}

{{CONTENT}}
