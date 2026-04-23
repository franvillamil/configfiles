rm -vf main.pdf response_memo.pdf appendix.pdf
rm -vf main.aux response_memo.aux
rm -rvf *.toc *.log *.out *.bbl *.blg *.fdb_latexmk *.thm *.fls *.synctex.gz *.lof *.lot *.bcf *.nav *.run.xml *.snm *.pgf
rm -f .DS_Store
git add .
git commit -m "update"
git push