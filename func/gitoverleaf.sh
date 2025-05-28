rm -vf main.pdf appendix.pdf response_memo.pdf
rm -vf main.aux response_memo.aux
rm -rvf *.toc *.log *.out *.bbl *.blg *.fdb_latexmk *.thm *.fls *.synctex.gz *.lof *.lot *.bcf *.nav *.run.xml *.snm
git add .
git commit -m "update"
git push