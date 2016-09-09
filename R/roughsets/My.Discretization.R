D.discretization.RST <- function(decision.table, type.method = "unsupervised.quantiles", ...){
	if (!(type.method %in% c("local.disc.matrix", "max.disc.matrix", "global.discernibility", 
                           "unsupervised.intervals", "unsupervised.quantiles", "convert.nominal"))) {
    stop("Unrecognized discretization type.")
	}
  
	if (!inherits(decision.table, "DecisionTable")) {
		stop("Provided data should inherit from the \'DecisionTable\' class.")
	}
    
	if (is.null(attr(decision.table, "decision.attr"))) {
		decisionIdx = ncol(decision.table) + 1
	} else decisionIdx = attr(decision.table, "decision.attr")
  
	if (all(attr(decision.table, "nominal.attrs")[-decisionIdx])) {
		warning("All the conditional attributes are nominal.")
	} else {
		if(any(attr(decision.table, "nominal.attrs")[-decisionIdx]) && type.method == "global.discernibility") {
			stop("This discretization method is not implemented for decision tables with mixed attribute types.")
		}
	}
  	  
	cut.values = switch(type.method,  
    	                unsupervised.quantiles = D.discretize.quantiles.RST(decision.table, ...),
    	                unsupervised.intervals = D.discretize.equal.intervals.RST(decision.table, ...),
                      global.discernibility = D.global.discernibility.heuristic.RST(decision.table, ...),
    	                local.disc.matrix = D.local.discernibility.matrix.RST(decision.table),
    	                max.disc.matrix = D.max.discernibility.matrix.RST(decision.table),
                      convert.nominal = D.convert.nominal.RST(decision.table))
  	
	return(cut.values)
}

D.convert.nominal.RST <- function(decision.table){
  ## get data
  objects <- decision.table
  desc.attrs <- attr(decision.table, "desc.attrs")
  nominal.attr <- attr(decision.table, "nominal.attrs")
  decision.attr <- attr(decision.table, "decision.attr")
  if (is.null(decision.attr)) stop("A decision attribute is not indicated.")
  
  ## rangeから各値に変更する
  desc.attrs[which(!nominal.attr)] = lapply(objects[which(!nominal.attr)], unique)
    
  ## integer, numericもnominalにする
  class.vector = sapply(objects, class)
  nominal.attr[class.vector %in% c("integer", "numeric")] = TRUE
  
  ## construct decision.table again
  attr(objects, "nominal.attrs") = nominal.attr
  attr(objects, "desc.attrs") = desc.attrs
  attr(objects, "decision.attr") = decision.attr 
  objects = My.ObjectFactory(objects, "DecisionTable")
  return(objects)
}

D.local.discernibility.matrix.RST <- function(decision.table){
	## get data
	objects <- decision.table
	desc.attrs <- attr(decision.table, "desc.attrs")
	nominal.att <- attr(decision.table, "nominal.attrs")
	decision.attr <- attr(decision.table, "decision.attr")
    if (is.null(decision.attr)) stop("A decision attribute is not indicated.")
	num.att <- ncol(objects)

	## get non nominal attribute 
	non.nominal.obj <- objects[, which(nominal.att == FALSE), drop = FALSE]
	dec.nominal.obj <- cbind(non.nominal.obj, objects[, ncol(objects), drop = FALSE])
	
	## get cut for each attributes
	if (nrow(non.nominal.obj) == 1 || ncol(non.nominal.obj) < 1)
		stop("the number of object is only 1 or there is no nominal attribute")
	else {	
		ready.list <- gen.cut.values(non.nominal.obj)
	}
	
	## initialization 
	exit <- FALSE
	tree.objects <- list()
	root <- matrix(ncol = 2)
	tree.objects <- list(seq(1, nrow(non.nominal.obj)))
	cut.save.list <- list()
	status.tree <- matrix(c(0))		
	while (any(status.tree == 0)){
		unready.indx <- which(status.tree == 0)
		
		## loop for any unready leave of tree
		for (iii in unready.indx){		
			non.objects <- non.nominal.obj[tree.objects[[iii]], ,drop = FALSE]		
			dec.objects <- dec.nominal.obj[tree.objects[[iii]], ,drop = FALSE]
			
			## check if objects have the same decision rules
			if (length(unique(c(dec.objects[, ncol(dec.objects)]))) == 1){
				status.tree[[iii]] <- 1
			} 
			else {	
				temp <- matrix()
				 for (i in 1 : nrow(ready.list)){
					# compute value W
					 temp[i] <- def.discern.mat(dec.objects, cut.val = c(ready.list[i, 2], ready.list[i, 1]), type = "func.w")			
				 }
				 
				## get cut value that gives max number of pairs discerned by (a, c) or cut value
				## indx.max.cut <- which.max(temp)		
				indx.max <- which(temp == max(temp))
				if (length(indx.max) > 1){
					indx.max.cut <- indx.max[which(ready.list[indx.max, 2] %in% root[, 2] == FALSE)[1]]					
					if (is.na(indx.max.cut)) indx.max.cut <- indx.max[1]
				}
				else indx.max.cut <- indx.max[1]
				
				## save the cut value and its attribute
				root <- rbind(root, ready.list[indx.max.cut, 1 : 2])				
				names.att <- names(desc.attrs[ready.list[indx.max.cut, 2]])
				
				if ((names.att %in% names(cut.save.list)) == FALSE){
					cut.save.list[names.att] <- c(ready.list[indx.max.cut, 1])
				}
				else {
					cut.save.list[[names.att]] <- c(cut.save.list[[names.att]], ready.list[indx.max.cut, 1])
				}
				
				## change status to be ready or 1
				status.tree[[iii]] <- 1
				
				## get the cut value
				max.cut.val <- ready.list[indx.max.cut, 1]
				
				## split into left and right of tree
				temp.left.tree <- c()
				temp.right.tree <- c()
					
				for (i in 1 : length(tree.objects[[iii]])){
					## check each data considering with index of attributes and then compare with max.cut.value
					if (non.nominal.obj[tree.objects[[iii]][i], ready.list[indx.max.cut, 2]] < max.cut.val){
						## collect the index of data which a(u) < max.cut.val
						temp.left.tree <- c(temp.left.tree, tree.objects[[iii]][i])
					} else {	
						temp.right.tree <- c(temp.right.tree, tree.objects[[iii]][i])
					}
				}
				
				## collect into tree
				if (!is.null(temp.left.tree)){
					tree.objects <- c(tree.objects, list(temp.left.tree))
					status.tree <- cbind(status.tree, 0)
				}
				
				if (!is.null(temp.right.tree)){
					tree.objects <- c(tree.objects, list(temp.right.tree))
					status.tree <- cbind(status.tree, 0)
				}
				
				## delete the cut value
				ready.list <- ready.list[-indx.max.cut, ,drop = FALSE]
				status.tree[[iii]] <- 1
			}
		}
	 }	
	 names.all.cont <- names(desc.attrs)[-decision.attr]
	 names.miss <- names.all.cont[which(names.all.cont %in% names(cut.save.list) == FALSE)]
	
	 if (length(names.miss) >= 1){
		for (i in 1 : length(names.miss)) {
			cut.save.list[[names.miss[i]]] <- numeric(0)
		}
	 }
	 	 
     ## construct class
	 mod <- list(cut.values = cut.save.list, type.method = "local.strategy", 
	            type.task = "discretization", model = "RST")
				
	class.mod <- ObjectFactory(mod, classname = "Discretization")	
	return(class.mod)  
}

#' This is a function that implements the maximal discernibility algorithm based on rough set theory proposed 
#' by (Bazan et al, 2000), for discretization tasks.
#' 
#' Let \eqn{A = (U, A \cup \{d\})}  be a decision table. An arbitrary attribute \eqn{a \in A} defines a sequence \eqn{v_{1}^a < v_{2}^a < \ldots < v_{n_{a}}^a}, where
#' \eqn{\{v_{1}^a, v_{2}^a, \ldots, v_{n_{a}}^a \} = \{a(x): x : \in U \}} and \eqn{n_{a} \leq n}. Then the set of all possible cuts on \eqn{a} is denoted by
#'
#' \eqn{C_{a} = \{ (a, \frac{v_{1}^a + v_{2}^a}{2}), (a, \frac{v_{2}^a + v_{3}^a}{2}), \ldots, (a, \frac{v_{n_{a}-1}^a + v_{n_{a}}^a}{2})\}}
#'
#' The set of possible cuts on all attributes is denoted by
#'
#' \eqn{C_{A} = \cup_{a \in A}C_{a}}
#'
#' The main points employed in this algorithm are to choose the cut \eqn{c_{max} \in C_{A}} which discerns the largest number of pairs of objects in 
#' the decision-relative discernibility matrix \eqn{L = \{(x, y) \in U \times U : d(x) \neq d(y)\}}. Then insert \eqn{c_{max}} into a list \eqn{D} and remove it from \eqn{C_{A}}.
#' All pairs of objects from \eqn{L} discerned by \eqn{c_{max}} are deleted as well. 
#'
#' This function will detect and perform converting the real into nominal values according to states \code{FALSE} in parameter \code{nominal.attributes}.
#' And, it should be noted that the output of this function is a class containing cut values. 
#' In order to generate new decision table, \code{\link{SF.applyDecTable}} is executed. It should be noted that
#' this algorithm needs a large memory and long time for discretization a big dataset.
#'
#' @title The maximal discernibility algorithm
#' @author Lala Septem Riza
#'
#' @param decision.table a \code{"DecisionTable"} class representing the decision table. See \code{\link{SF.asDecisionTable}}.
#'        It should be noted that the function need the nominal decision attribute.
#' @seealso \code{\link{D.local.discernibility.matrix.RST}}, \code{\link{D.discretize.quantiles.RST}},
#'
#' \code{\link{D.discretize.equal.intervals.RST}}, and \code{\link{D.global.discernibility.heuristic.RST}}
#' @return A class \code{"Discretization"} that contains the following components:
#' \itemize{
#' \item \code{cut.values}: a list representing cut values of each considered attributes.
#' \item \code{type.method}: a type of method which is used to define cut values. 
#'
#'        In this case, it is \code{"max.discernibility"}.
#' \item \code{type.task}: a type of task which is \code{"discretization"}.
#' \item \code{model}: a type of model which is \code{"RST"}.
#' }
#' @references
#' Jan G. Bazan, Hung Son Nguyen, Sinh Hoa Nguyen, Piotr Synak, and Jakub Wroblewski, 
#' "Rough Set Algorithms in Classification Problem", Chapter 2
#'  In: L. Polkowski, S. Tsumoto and T.Y. Lin (eds.): Rough Set Methods and Applications
#' Physica-Verlag, Heidelberg, New York, p. 49 - 88 (2000). 
#' @examples
#' #################################################################
#' ## Example: Determine cut values and generate new decision table
#' #################################################################
#'  dt.ex1 <- data.frame(c(1, 1.2, 1.3, 1.4, 1.4, 1.6, 1.3), c(2, 0.5, 3, 1, 2, 3, 1),
#'                              c(1, 0, 0, 1, 0, 1, 1))
#' colnames(dt.ex1) <- c("a", "b", "d")
#' decision.table <- SF.asDecisionTable(dataset = dt.ex1, decision.attr = 3, indx.nominal = c(3)) 
#'
#' cut.values <- D.max.discernibility.matrix.RST(decision.table)
#'
#' ## generate new decision table
#' new.decTable <- SF.applyDecTable(decision.table, cut.values)
#' @export
D.max.discernibility.matrix.RST <- function(decision.table){
	
	## get data
	objects <- decision.table
	desc.attrs <- attr(decision.table, "desc.attrs")
	nominal.att <- attr(decision.table, "nominal.attrs")
	decision.attr <- attr(decision.table, "decision.attr")
	if(is.null(decision.attr)) stop("A decision attribute is not indicated.")
	num.att <- ncol(objects)

	## get non nominal attribute only to be discretize
	non.nominal.obj <- objects[, which(nominal.att == FALSE), drop = FALSE]
	dec.nominal.obj <- cbind(non.nominal.obj, objects[, ncol(objects), drop = FALSE])
	nrow.data <- nrow(dec.nominal.obj)
	ncol.data <- ncol(dec.nominal.obj)
	
	## get cut for each attributes
	if (nrow(non.nominal.obj) == 1 || ncol(non.nominal.obj) < 1)
		stop("the number of object is only 1 or there is no the nominal attribute")
	else {
		cut.att.all <- gen.cut.values(non.nominal.obj)
	}
	
	## initialize
	exit <- FALSE	
	cut.save <- matrix(NA, nrow = 1, ncol = 2)
	
	## run discernibility matrix for first cut value
	cut.res <- def.discern.mat(data = dec.nominal.obj, cut.val = c(cut.att.all[1, 2], cut.att.all[1, 1]), type = "table")
	mat.disc <- cut.res
	cut.save.list <- list()

	## run discernibility matrix for rest cut values
	for (i in 2 : nrow(cut.att.all)){
		## construct discernibility matrix which constitutes pairs of objects toward cut values
		cut.res <- def.discern.mat(data = dec.nominal.obj, cut.val = c(cut.att.all[i, 2], cut.att.all[i, 1]), type = "table")
		temp.mat.disc <- cut.res
		
		## collect them
		mat.disc <- cbind(mat.disc, temp.mat.disc)
	}
	
	while (exit == FALSE){	
		## search max discern object
		indx.max <- which.max(apply(mat.disc, 2, function(x) sum(x)))

		## save it as reduct 
		temp.cut.save <- cut.att.all[indx.max, ,drop = FALSE]
		
		## delete the table containing cut
		mat.disc <- mat.disc[-c(which(mat.disc[, indx.max] == 1)), ,drop = FALSE]
		mat.disc <- mat.disc[, -indx.max, drop = FALSE]
		
		## collect all reducts
		cut.save <- rbind(cut.save, temp.cut.save)
		names.att <- names(desc.attrs[temp.cut.save[1, 2]])
		if ((names.att %in% names(cut.save.list)) == FALSE){
			cut.save.list[names.att] <- c(temp.cut.save[1, 1])
		}
		else {
			cut.value <- c(temp.cut.save[1, 1])
			cut.save.list[[names.att]] <- c(cut.save.list[[names.att]], cut.value)
		}
		
		## stopping criteria
		if (nrow(mat.disc) <= 1 || ncol(mat.disc) <= 1)
			exit <- TRUE
	}
	
	names.all.cont <- names(desc.attrs)[-decision.attr]
	names.miss <- names.all.cont[which(names.all.cont %in% names(cut.save.list) == FALSE)]
	
	if (length(names.miss) >= 1){
		for (i in 1 : length(names.miss)) {
			cut.save.list[[names.miss[i]]] <- numeric(0)
		}
	}
	 ## construct class
	  mod <- list(cut.values = cut.save.list, type.method = "max.discernibility", 
	            type.task = "discretization", model = "RST")
				
	 class.mod <- ObjectFactory(mod, classname = "Discretization")	
	 return(class.mod) 
}

#' This function implements unsupervised discretization into intervals containing similar number of instances ("quantile-based").
#'
#' This approach belongs to a class of unsupervised discretization methods 
#' since it does not consider the class labels. Each numeric attribute is divided in \code{k} intervals which contain approximately 
#' the same number of data instances (objects).
#' Detailed information regarding this method can be found in (Dougherty et al, 1995).
#'
#' It should be noted that the output of this function is an object of a class \code{"Discretization"} 
#' which contains the cut values. 
#' The function \code{\link{SF.applyDecTable}} has to be used in order to generate the new (discretized) decision table.
#'
#' @title The quantile-based discretization
#' @author Andrzej Janusz
#'
#' @param decision.table an object inheriting from the \code{"DecisionTable"} class, which represents a decision system. 
#'        See \code{\link{SF.asDecisionTable}}.
#' @param nOfIntervals a positive integer giving the number of intervals.
#' 
#' @return An object of a class \code{"Discretization"} which stores cuts for each conditional attribute. 
#'         See \code{\link{D.discretization.RST}}.
#'
#' @seealso \code{\link{D.discretize.equal.intervals.RST}}, \code{\link{D.global.discernibility.heuristic.RST}},
#'          \code{\link{SF.applyDecTable}}.
#'                           
#' @references
#' J. Dougherty, R. Kohavi, and M. Sahami, "Supervised and Unsupervised Discretization of Continuous Features",
#' In A. Prieditis & S. J. Russell, eds. Work. Morgan Kaufmann, p. 194-202 (1995).
#'
#' @examples
#' #################################################################
#' ## Example: Determine cut values and generate new decision table
#' #################################################################
#' data(RoughSetData)
#' wine.data <- RoughSetData$wine.dt
#' cut.values <- D.discretize.quantiles.RST(wine.data, nOfIntervals = 5)
#' 
#' ## generate a new decision table
#' wine.discretized <- SF.applyDecTable(wine.data, cut.values)
#' dim(wine.discretized)
#' lapply(wine.discretized, unique)
#' 
#' @export
D.discretize.quantiles.RST <- function(decision.table, nOfIntervals = 4) {
  
  nominalAttrs = attr(decision.table, "nominal.attrs")
  if (!is.null(attr(decision.table, "decision.attr"))) {
    nominalAttrs = nominalAttrs[-attr(decision.table, "decision.attr")]
    decision.table = decision.table[-attr(decision.table, "decision.attr")]
  }
  
  if (nOfIntervals < 1 || nOfIntervals > nrow(decision.table)) {
    stop("Wrong value of the parameter nOfIntervals.")
  }
	
  if(sum(nominalAttrs) > 0) {
    cutsList = list()
    cutsList[1:ncol(decision.table)] = list(numeric())
    cutsList[!nominalAttrs] = lapply(decision.table[!nominalAttrs], discretize.quantiles, n = nOfIntervals)
  } else cutsList = lapply(decision.table, discretize.quantiles, n = nOfIntervals)
    
	cutsList = list(cut.values = cutsList, type.method = "unsupervised.quantiles",
                type.task = "discretization", model = "RST")
	cutsList = ObjectFactory(cutsList, classname = "Discretization")
	return(cutsList)
}

#' This function implements unsupervised discretization into intervals of equal size.
#'
#' This approach belongs to a class of unsupervised discretization methods 
#' since it does not consider the class labels. Each numeric attribute is divided in \code{k} intervals of equal length.
#' Detailed information regarding this method can be found in (Dougherty et al, 1995).
#' 
#' It should be noted that the output of this function is an object of a class \code{"Discretization"} 
#' which contains the cut values. 
#' The function \code{\link{SF.applyDecTable}} has to be used in order to generate the new (discretized) decision table.
#'
#' @title Unsupervised discretization into intervals of equal length.
#' @author Andrzej Janusz
#'
#' @param decision.table an object inheriting from the \code{"DecisionTable"} class, which represents a decision system. 
#'        See \code{\link{SF.asDecisionTable}}.
#' @param nOfIntervals a positive integer giving the number of intervals.
#' 
#' @return An object of a class \code{"Discretization"} which stores cuts for each conditional attribute. 
#'         See \code{\link{D.discretization.RST}}.
#'         
#' @seealso \code{\link{D.discretize.quantiles.RST}}, \code{\link{D.global.discernibility.heuristic.RST}}, 
#'          \code{\link{SF.applyDecTable}}.
#'
#' @references
#' J. Dougherty, R. Kohavi, and M. Sahami, "Supervised and Unsupervised Discretization of Continuous Features",
#' In A. Prieditis & S. J. Russell, eds. Work. Morgan Kaufmann, p. 194-202 (1995).
#'
#' @examples
#' #################################################################
#' ## Example: Determine cut values and generate new decision table
#' #################################################################
#' data(RoughSetData)
#' wine.data <- RoughSetData$wine.dt
#' cut.values <- D.discretize.equal.intervals.RST(wine.data, nOfIntervals = 3)
#' 
#' ## generate a new decision table
#' wine.discretized <- SF.applyDecTable(wine.data, cut.values)
#' dim(wine.discretized)
#' lapply(wine.discretized, unique)
#' 
#' @export
D.discretize.equal.intervals.RST <- function(decision.table, nOfIntervals = 4) {
	
  nominalAttrs = attr(decision.table, "nominal.attrs")
  if (!is.null(attr(decision.table, "decision.attr"))) {
    nominalAttrs = nominalAttrs[-attr(decision.table, "decision.attr")]
		decision.table = decision.table[-attr(decision.table, "decision.attr")]
	}
  
  if (nOfIntervals < 1 || nOfIntervals > nrow(decision.table)) {
    stop("Wrong value of the parameter nOfIntervals.")
  }
  
  if(sum(nominalAttrs) > 0) {
	  cutsList = list()
	  cutsList[1:ncol(decision.table)] = list(numeric())
    cutsList[!nominalAttrs] = lapply(decision.table[!nominalAttrs], discretize.equal.intervals, n = nOfIntervals)
  } else cutsList = lapply(decision.table, discretize.equal.intervals, n = nOfIntervals)
  
	cutsList = list(cut.values = cutsList, type.method = "unsupervised.intervals",
                type.task = "discretization", model = "RST")
	cutsList = ObjectFactory(cutsList, classname = "Discretization")
	return(cutsList)
}

#' It is a function used for computing globally semi-optimal cuts using the maximum discernibility heuristic.
#'
#' A complete description of the implemented algorithm can be found in (Nguyen, 2001).
#' 
#' It should be noted that the output of this function is an object of a class \code{"Discretization"} 
#' which contains the cut values. 
#' The function \code{\link{SF.applyDecTable}} has to be used in order to generate the new (discretized) decision table.
#'
#' @title Supervised discretization based on the maximum discernibility heuristic
#' @author Andrzej Janusz
#'
#' @param decision.table an object inheriting from the \code{"DecisionTable"} class, which represents a decision system. 
#'        See \code{\link{SF.asDecisionTable}}.
#'        It should be noted that especially for this method, all conditional attributes
#'        must in real values. So, in the case we have mixed values, we should choose other methods.
#' @param maxNOfCuts a positive integer indicating the maximum number of allowed cuts.
#' @param attrSampleSize an integer between 1 and the number of conditional attributes (the default). It indicates 
#'        the attribute sample size for the Monte Carlo selection of candidating cuts. 
#' @param cutCandidatesList an optional list containing candidates for optimal cut values.
#' @param discFunction a function used for computation of cuts. Currently only one implementation of maximu discernibility heuristic 
#'        is available (the default). However, this parameter can be used to integrate custom implementations of 
#'        discretization functions with the \code{RoughSets} package.
#' @param ... additional parameters to the \code{discFunction} (currently unsupported).
#' 
#' @seealso \code{\link{D.discretize.quantiles.RST}}, \code{\link{D.discretize.equal.intervals.RST}}
#'          and \code{\link{SF.applyDecTable}}.
#' 
#' @return An object of a class \code{"Discretization"} which stores cuts for each conditional attribute. 
#'         See \code{\link{D.discretization.RST}}.
#'         
#' @references
#' S. H. Nguyen, "On Efficient Handling of Continuous Attributes in Large Data Bases", 
#' Fundamenta Informaticae, vol. 48, p. 61 - 81 (2001). 
#' 
#' @examples
#' #################################################################
#' ## Example: Determine cut values and generate new decision table
#' #################################################################
#' data(RoughSetData)
#' wine.data <- RoughSetData$wine.dt
#' cut.values <- D.global.discernibility.heuristic.RST(wine.data)
#' 
#' ## generate a new decision table:
#' wine.discretized <- SF.applyDecTable(wine.data, cut.values)
#' dim(wine.discretized)
#' lapply(wine.discretized, unique)
#' 
#' ## remove attributes with only one possible value:
#' to.rm.idx <- which(sapply(lapply(wine.discretized, unique), function(x) length(x) == 1))
#' to.rm.idx
#' wine.discretized.reduced <- wine.discretized[-to.rm.idx]
#' dim(wine.discretized.reduced)
#' 
#' ## check whether the attributes in the reduced data are a super-reduct of the original data:
#' colnames(wine.discretized.reduced)
#' class.idx <- which(colnames(wine.discretized.reduced) == "class")
#' sum(duplicated(wine.discretized.reduced)) == sum(duplicated(wine.discretized.reduced[-class.idx])) 
#' ## yes it is
#' 
#' @export
D.global.discernibility.heuristic.RST <- function(decision.table, maxNOfCuts = 2*ncol(decision.table),
                                                 attrSampleSize = ncol(decision.table)-1,
                                                 cutCandidatesList = NULL,
                                                 discFunction = global.discernibility, ...)  {

	if (!is.null(attr(decision.table, "decision.attr"))) {
		infoSystem = decision.table[-attr(decision.table, "decision.attr")] 
		decisionAttr = factor(decision.table[[attr(decision.table, "decision.attr")]])
	} else {
    stop("A decision attribute is not indicated.")
	}
  
  if (maxNOfCuts < 1) {
    stop("Wrong value of maxNOfCuts. It should be a positive integer.")
  }
  
	if (attrSampleSize < 1 || attrSampleSize > ncol(decision.table) - 1) {
	  stop("Wrong value of attrSampleSize. It should be a positive integer, not larger than the number of conditional attributes.")
	}
  
	if (is.null(cutCandidatesList)) {
		cutCandidatesList = lapply(infoSystem, chooseCutCandidates, decisionAttr)
	} else {
    if (length(cutCandidatesList) != ncol(decision.table) - 1) {
      stop("Wrong length of a list containing candidate cuts. Its length should equal the number of conditional attributes.")
    }
	}
	
	candidatesCounterVec = sapply(cutCandidatesList, length)
	nonNullIdx = which(sapply(cutCandidatesList, function(x) return(length(x) > 0)))
  
	cutsList = list()
	cutsList[1:ncol(infoSystem)] = list(numeric())
  
	tmpCutsList = discFunction(as.list(infoSystem)[nonNullIdx], cutCandidatesList[nonNullIdx], 
                             decVec = decisionAttr, nOfCuts = maxNOfCuts, 
                             nAttrs = attrSampleSize, ...)
	cutsList[nonNullIdx] = tmpCutsList
  
  
	names(cutsList) = colnames(infoSystem)
	cutsList = list(cut.values = cutsList, type.method = "global.discernibility",
                  type.task = "discretization", model = "RST")
	cutsList = ObjectFactory(cutsList, classname = "Discretization")
	
	return(cutsList)
}

