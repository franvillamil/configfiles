mypandoc() {
  local input="$1"
  local output="${2:-${input%.md}.pdf}"
  pandoc "$input" -o "$output" \
    --pdf-engine=xelatex \
    -V mainfont="Palatino" \
    -V geometry:margin=0.75in \
    -V fontsize=11pt \
    -V linestretch=1.1
}