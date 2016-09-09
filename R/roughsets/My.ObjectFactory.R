My.ObjectFactory <- function(mod, classname){
  class(mod) <- unique(c(classname, class(mod)))
  return(mod)
}