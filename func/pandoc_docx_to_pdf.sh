find ./ -iname '*.docx' -type f -exec sh -c 'pandoc "${0}" -o "${0%.docx}.pdf" -V geometry:margin=0.75in --pdf-engine=xelatex -V fontsize=12pt -V linestretch=1.2;rm "${0}"' {} \;
