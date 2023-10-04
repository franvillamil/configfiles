# Default options
options(scipen = 999, stringsAsFactors = FALSE)

# Default CRAN mirror
options(repos=structure(c(CRAN="https://cloud.r-project.org/")))

# Default library path
# .libPaths(c("/Library/Frameworks/R.framework/Versions/4.2/Resources/library"))

# Shortcuts for functions
adf = function(x){as.data.frame(x)}

adapt2 = function(str){
  str = gsub("\u00fa", "u", str)
  str = gsub("\u00f3", "o", str)
  str = gsub("\u00f1", "n", str)
  str = gsub("\u00ed", "i", str)
  str = gsub("\u00e1", "a", str)
  str = gsub("\u00e9", "e", str)
  str = gsub("\u00fc", "u", str)
  str = gsub("\u00c1", "A", str)
  str = gsub("\u00e0", "a", str)
  str = gsub("\u00d3", "o", str)
  str = gsub("\u00f2", "o", str)
  str = gsub("\u00d2", "o", str)
  str = gsub("\u00e7", "c", str)
  str = gsub("\u00c7", "c", str)
  str = gsub("\u00e8", "e", str)
  str = gsub("\u00c9", "e", str)
  str = gsub("\u00c8", "e", str)
  str = gsub("\u00cd", "i", str)
  str = gsub("\u00c0", "a", str)
  str = gsub("\u00da", "u", str)
  str = gsub("\u00ba", "º", str)
  str = gsub("\u2019", "'", str)
  str = gsub("\u201d", "'", str)
  str = gsub("(El|La|Los|Las) (.*)", "\\2, \\1", str)
  str = gsub(" \\((El|La|Los|Las)\\)", ", \\1", str)
  str = gsub("\\s\\s+", " ", str)
  return(str)
}


capitalize = function(str){
  c = strsplit(str, " ")
  cu = lapply(c, function(x)
    paste(toupper(substring(x, 1,1)), substring(x, 2), sep="", collapse=" "))
  return(unlist(cu))
}
