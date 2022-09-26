find ./ -iname '*.docx' -type f -exec sh -c 'pandoc "${0}" -o "${0%.docx}.pdf" -V geometry:margin=0.3in --pdf-engine=xelatex -V fontsize=11pt;rm "${0}"' {} \;
