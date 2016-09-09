## LERS
predict.LERS <- function(rules, data.test) {
  library(stringr)
  if(!inherits(rules, "RuleSetRST")) stop("The rule set does not an object from the \'RuleSetRST\' class")
  
  if(!inherits(data.test, "DecisionTable")) stop("Provided data should inherit from the \'DecisionTable\' class.")
  
  method = attr(rules, "method")
  if (!(method %in% c("indiscernibilityBasedRules", "CN2Rules", "MLEM2Rules", "AQRules"))) {
    stop("Unrecognized classification method")
  }
  
  # predict values
  #predVec <- vector()
  predVec <- pforeach(ind.obj = 1:nrow(data.test), .multicombine=TRUE, .verbose = TRUE)({
  #for(ind.obj in 1:nrow(data.test)){
    judges <- sapply(rules, function(rule){
      idxs <- rule$idx
      values <- rule$values
      # bug。なぜかvalues が list()なのがあるのでその回避
      if(length(values) == 0){
        return(FALSE)
      }
      judge <- TRUE
      for(ind.idx in 1:length(idxs)){      
        # num 
        if(is.numeric(values[[ind.idx]])){
          if(data.test[ind.obj,][idxs[ind.idx]] > values[[ind.idx]][1]&
             data.test[ind.obj,][idxs[ind.idx]] < values[[ind.idx]][2]){ 
            judge <- TRUE
          }else{
            return(FALSE)
          }
        # nom  
        }else{
          # 基本条件が複数の条件でルールができている場合
          if(str_detect(values[[ind.idx]][1], "^\\[.*\\]$")){
            v <- values[[ind.idx]][1]
            v <- str_replace_all(v, "^\\[", "")
            v <- str_replace_all(v, "\\]$", "")
            v <- str_split(v, ",")[[1]]
            if(data.test[ind.obj,][idxs[ind.idx]] %in% v){
              judge <- TRUE
            }else{
              return(FALSE)
            }
            # 基本条件が1つの条件でルールができている場合
          }else{
            if(data.test[ind.obj,][idxs[ind.idx]] == values[[ind.idx]][1]){
              judge <- TRUE
            }else{
              return(FALSE)
            } 
          }
        }  
      }
      return(TRUE)
    })

    # objにマッチするrule が 1つでもある
    estimatedClass <- NULL
    if(any(judges)){
      # マッチしたルールが1つだけのとき
      if(length(which(judges)) == 1){
        estimatedClass <- list.select(rules[which(judges)], consequent) %>% list.mapv(consequent)
      # マッチしたルールが2つ以上で同じクラスを推定しているとき
      }else if(length(which(judges)) > 1 & length(unique(list.select(rules[which(judges)], consequent))) == 1){
        estimatedClass <- unique(list.select(rules[which(judges)], consequent) %>% list.mapv(consequent))
      # マッチしたルールが2つ以上で別のクラスを推定しているとき
      }else if(length(which(judges)) > 1 & length(unique(list.select(rules[which(judges)], consequent))) > 1){
        support_D <- -1
        for(rule in rules[which(judges)]){
          strength <- length(rule$support)
          specificity <- length(rule$values)
          if((strength * specificity) > support_D){
            estimatedClass <- rule$consequent
            support_D <- strength * specificity
          }
        }
      }else{
        stop("LERS doesn't estimate the decision class")
      }
    }
    # rule が objに1つもマッチしない場合は部分一致ルールによる推定
    else{
      p_support <- -1
      for(rule in rules){
        strength <- length(rule$support)
        specificity <- length(rule$values)
        matching_factor <- 0
        idxs <- rule$idx
        values <- rule$values
        # bug。なぜかvalues が list()なのがあるのでその回避
        if(length(values) == 0){
          next
        }
        for(ind.idx in 1:length(idxs)){
          # num 
          if(is.numeric(values[[ind.idx]])){
            if(data.test[ind.obj,][idxs[ind.idx]] > values[[ind.idx]][1]&
              data.test[ind.obj,][idxs[ind.idx]] < values[[ind.idx]][2]){ 
              matching_factor <- matching_factor + 1
            }
          # nom  
          }else{
            # 基本条件が複数の条件でルールができている場合
            if(str_detect(values[[ind.idx]][1], "^\\[.*\\]$")){
              v <- values[[ind.idx]][1]
              v <- str_replace_all(v, "^\\[", "")
              v <- str_replace_all(v, "\\]$", "")
              v <- str_split(v, ",")[[1]]
              if(data.test[ind.obj,][idxs[ind.idx]] %in% v){
                matching_factor <- matching_factor + 1  
              }
            # 基本条件が1つの条件でルールができている場合
            }else{
              if(data.test[ind.obj,][idxs[ind.idx]] == values[[ind.idx]][1]){
                matching_factor <- matching_factor + 1
              }              
            }
          }
        }
        matching_factor <- matching_factor / length(idxs)
        if((matching_factor * strength * specificity) > p_support){
          estimatedClass <- rule$consequent
          p_support <- matching_factor * strength * specificity
        }
      }
    }
  #  predVec <- append(predVec, estimatedClass)
  #}
  })
  return(predVec)
}