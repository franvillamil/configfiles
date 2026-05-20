find ./ -iname '*.docx' -type f -exec sh -c '
  /Applications/LibreOffice.app/Contents/MacOS/soffice --headless --convert-to pdf --outdir "$(dirname "$0")" "$0" && rm "$0"
' {} \;