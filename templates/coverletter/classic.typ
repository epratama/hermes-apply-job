// classic-cover.typ — Traditional serif cover letter
#set page(margin: (x: 2.2cm, y: 2cm), paper: "us-letter")
#set text(font: "New Computer Modern", size: 11pt, fallback: true)
#set par(leading: 0.65em, justify: true)

#show heading.where(level: 1): it => {
  set align(right)
  set text(size: 14pt, weight: "bold")
  it
  v(1em)
}

{{CONTENT}}
