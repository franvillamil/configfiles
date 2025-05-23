cleantex
rm -vf main.pdf appendix.pdf response_memo.pdf
rm -vf main.aux appendix.aux response_memo.aux
git add .
git commit -m "update"
git push