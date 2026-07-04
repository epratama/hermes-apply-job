// classic-cover.typ — Traditional serif cover letter with date/to block

#set page(margin: (x: 2.2cm, y: 2cm), paper: "us-letter")
#set text(font: ("New Computer Modern", "Latin Modern Roman", "Georgia", "Times New Roman"), size: 11pt, fallback: true)
#set par(leading: 0.7em, justify: false)

#show heading.where(level: 1): it => {
  set align(right)
  set text(size: 14pt, weight: "bold")
  it
  v(0.3em)
  line(length: 100%, stroke: 0.7pt + black)
  v(1em)
}

{{CONTENT}}
