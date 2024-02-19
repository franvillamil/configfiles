# Default options
options(scipen = 999, stringsAsFactors = FALSE)

# Default CRAN mirror
options(repos=structure(c(CRAN="https://cloud.r-project.org/")))

# Default library path
# .libPaths(c("/Library/Frameworks/R.framework/Versions/4.2/Resources/library"))

# Shortcuts and other functions
# (NOTE: adapt2 for some reason does not work when including here in .Rprof, why?)

# as.data.frame
adf = function(x){as.data.frame(x)}

# Capitalize words
capitalize = function(str){
  c = strsplit(str, " ")
  cu = lapply(c, function(x)
    paste(toupper(substring(x, 1,1)), substring(x, 2), sep="", collapse=" "))
  return(unlist(cu))
}

# Silent library loading (stackoverflow.com/a/76678272/2319134)
silentlibrary = function (...) {
   packages = as.character(match.call(expand.dots = FALSE)[[2]])
   suppressWarnings(suppressMessages(lapply(packages, base::library, character.only = TRUE)))
   return(invisible())
}