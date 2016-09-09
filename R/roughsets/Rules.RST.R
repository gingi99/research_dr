## MLEM2 用パッケージ
library(rlist)
library(dplyr)
library(data.table)
library(pforeach)

My.RI.MLEM2Rules.RST <- function(decision.table)  {
  if (!inherits(decision.table, "DecisionTable")) {
    stop("Provided data should inherit from the \'DecisionTable\' class.")
  }
  
  if(is.null(attr(decision.table, "decision.attr"))) {
    stop("A decision attribute is not indicated.")
  } else {
    # 決定属性がある列を求める（irisなら5）
    decIdx = attr(decision.table, "decision.attr")
  }
    
  ## 決定属性の決定クラスのFactor型ベクトルを求める（irisなら、決定クラス150要素）
  clsVec <- dplyr::select(decision.table, decIdx)[[1]]
  
  ## ユニークな決定クラスを求める（irisなら、setosa、versicolor、virginicaの3つ） 
  uniqueCls <- unique(clsVec)
  
  ## 決定属性の列名を求める（irisなら、"Species"）
  decisionName <- colnames(decision.table)[decIdx]
  
  ## 各決定クラスの度数を求める（irisなら、50,50,50）
  clsFreqs <- table(clsVec)

  ## 識別不能関係のリストを返す
  INDrelation = BC.IND.relation.RST(decision.table, (1:ncol(decision.table))[-decIdx])
  
  ## 各決定クラスの上下近似を求める
  approximations = BC.LU.approximation.RST(decision.table, INDrelation)
  lowerApproximations = approximations$lower.approximation
  
  ## 結局、下近似だけを使うので残りを削除
  rm(INDrelation, approximations)
  
  ## 各条件属性の取りうる条件属性値を返す
  descriptorsList = attr(decision.table, "desc.attrs")[-decIdx]
  
  ## cutpoint型の各条件属性の取りうる条件属性値候補集合をリスト構造で返す
  attributeValuePairs = list()
  for (i in 1:length(descriptorsList)) {
    tmpAttributeValuePairs <- list()
    v <- descriptorsList[[i]]
    if(class(v) %in% c("factor", "character")){
      for(j in 1:length(v)){
        suppIdx <- which(decision.table[,i] == v[j])
        tmpAttributeValuePairs <- list(idx = i, type="nom", values = v[j], support = suppIdx)
        attributeValuePairs <- list.append(attributeValuePairs, tmpAttributeValuePairs)
      }
    }else if(class(v) %in% c("numeric", "integer")){
      v <- sort(v)
      v.min <- min(v)
      v.max <- max(v)
      for(j in 1:(length(v)-1)){
        v.cutvalue <- (v[j] + v[j+1])/2
        suppIdx <- which(decision.table[,i] >= v.min & decision.table[,i] < v.cutvalue)
        tmpAttributeValuePairs <- list(idx = i, type="num", values1 = v.min, values2 = v.cutvalue, support = suppIdx)
        attributeValuePairs <- list.append(attributeValuePairs, tmpAttributeValuePairs)
        
        suppIdx <- which(decision.table[,i] > v.cutvalue & decision.table[,i] <= v.max)
        tmpAttributeValuePairs <- list(idx = i, type="num", values1 = v.cutvalue, values2 = v.max, support = suppIdx)
        attributeValuePairs <- list.append(attributeValuePairs, tmpAttributeValuePairs)        
      }
    }else{
      stop("error : no type")
    }
  }
  
  rm(descriptorsList)

  ## T := 0 のところ
  rules <- list()
  Rules <- list()
  Rules <- pforeach(i = 1:length(lowerApproximations), .c=list, .multicombine=TRUE, .verbose = TRUE)({
  #for(i in 1:length(lowerApproximations)) {
    print(paste("Lower Approximation : ",i,sep=""))
    concept <- lowerApproximations[[i]]
    decisionValues <- clsVec
    if(length(unique(decisionValues[unname(concept)])) == 1){
      conclusion <- unique(decisionValues[unname(concept)])
    }else{
      stop("error : not right decisionValues")
    }
      
    ## concept が空ならストップ
    if(length(concept) == 0){
      stop("Empty lower approximation of a decision class.")
    }
    
    ## 初期設定（G = Bのところ）
    uncoveredConcept = concept
     
    ## G が空じゃないならループを続ける
    while(length(uncoveredConcept) > 0) {

      print(paste("uncoveredConcept : ", length(uncoveredConcept), sep=""))
      ## T := 0 のところ
      tmpRule <- list()
      
      ## TG := {t : t ^ G}のところ
      TG <- list()
      TG <- lapply(attributeValuePairs, function(avp){
        if(length(intersect(uncoveredConcept, avp$support)) > 0){
          return(avp)
        }
      })
      TG <- list.clean(TG, recursive = F)
      names(TG) <- paste("bes",seq(1,length(TG)), sep="")
      
      totalSupport <- 0
      
      # 1つのrule を求める(ここがボトルネック)
      while(length(tmpRule) == 0 | any(!totalSupport %in% concept)) {
        
        #print(paste("tmpRule, totalSupport : ", length(tmpRule),", ",length(totalSupport), sep=""))
        
        ## 基本条件e の候補を探索する
        t.best <- list()
        vec.cover.num <- sapply(TG, function(tg){
          length(intersect(uncoveredConcept, tg$support))
        })
        #vec.cover.num <- pforeach(i = 1:length(TG))({
        #  length(intersect(uncoveredConcept, TG[[i]]$support))
        #})
        vec.cover.num <- unname(vec.cover.num)
        tmpMaxValue <- max(vec.cover.num)
        tmpMaxIndexs <- which(vec.cover.num == tmpMaxValue)
        if(length(tmpMaxIndexs) == 1){
          t.best <- TG[tmpMaxIndexs]
        }else if (length(tmpMaxIndexs) > 1){
          t.best.cdt <- TG[tmpMaxIndexs]
          tmpMinValue <- min(list.mapv(t.best.cdt, length(support)))
          tmpMinIndexs <- which(list.mapv(t.best.cdt, length(support)) == tmpMinValue)
          if(length(tmpMinIndexs) == 1){
            t.best <- t.best.cdt[tmpMinIndexs]
          }else{
            t.best <- t.best.cdt[tmpMinIndexs[[1]]]
          }
        }else{
          stop("error")
        }

        ## T : T U {t}; のところ
        tmpRule <- list.append(tmpRule, t.best[[1]])
        if(length(list.select(tmpRule, support)) == 1){
          totalSupport <- t.best[[1]]$support
        }else{
          totalSupport <- intersect(totalSupport, t.best[[1]]$support) 
        }
        
        ## G := [t] ^ G のところ
        uncoveredConcept <- intersect(uncoveredConcept, t.best[[1]]$support)
        
        ##  TG := {t : t ^ G}のところ
        TG <- list()
        TG <- lapply(attributeValuePairs, function(avp){
          if(length(intersect(uncoveredConcept, avp$support)) > 0){
            return(avp)
          }
        })
        #TG <- pforeach(i = 1:length(attributeValuePairs), .c=list)({
        #  if(length(intersect(uncoveredConcept, attributeValuePairs[[i]]$support)) > 0){
        #    return(attributeValuePairs[[i]])
        #  }
        #})
        TG <- list.clean(TG, recursive = F)
        names(TG) <- paste("bes",seq(1,length(TG)), sep="")
              
        ## T(G) := T(G) - T のところ
        #microbenchmark(
        # 案1
        #for(tmp.rule in tmpRule){
        #  TG <- lapply(TG, function(tg){
        #    if(tg$idx == tmp.rule$idx){
        #      if(tg$type == "num"){
        #        if(tg$values1 == tmp.rule$values1 & tg$values2 == tmp.rule$values2){
        #          return(NULL)
        #        }else{
        #          return(tg)
        #        }
        #      }else{
        #        if(tg$values == tmp.rule$values){
        #          return(NULL)
        #        }else{
        #          return(tg)
        #        }
        #      }
        #    }else{
        #      return(tg)
        #    }
        #  })
        #  TG <- list.clean(TG, recursive = F)
        #}
        ## 案2
        for(tmp.rule in tmpRule){
          if(tmp.rule$type == "num"){
            TG <- list.filter(TG,
                              idx != tmp.rule$idx | 
                              values1 != tmp.rule$values1 | 
                              values2 != tmp.rule$values2)
          }else{
            TG <- list.filter(TG,
                              idx != tmp.rule$idx | 
                              values != tmp.rule$values)
          }
        }
        ## 案3
        #TG.rm <- lapply(tmpRule, function(tmp.rule){
        #  if(tmp.rule$type == "num"){
        #    return(list.filter(TG,
        #                      idx == tmp.rule$idx & 
        #                      values1 == tmp.rule$values1 & 
        #                      values2 == tmp.rule$values2))
        #  }else{
        #    return(list.filter(TG,
        #                       idx == tmp.rule$idx & 
        #                       values == tmp.rule$values))
        #  }
        #})
        #for(tg.rm in TG.rm){
        #  if(tg.rm$type == "num"){
        #    TG <- list.filter(TG,
        #                      idx == tg.rm$idx &
        #                      values1 == tg.rm$values1 & 
        #                      values2 == tg.rm$values2)
        #  }else{
        #    TG <- list.filter(TG,
        #                      idx == tg.rm$idx &
        #                      values == tg.rm$values)
        #  }
        #}
      }
      
      # tmpRuleの確定のところ
      values.list <- list()
      names(tmpRule) <- paste("can",seq(1,length(tmpRule)), sep="")
      length.tmpRule <- length(tmpRule)
      if(length.tmpRule > 1){
        for(ei in 1:length.tmpRule){
          ei.name <- paste("can",ei,sep="")
          tmp.rule <- list.remove(tmpRule, ei.name) 
          tmp.total.support <- list.select(tmp.rule, support) %>% list.common(support)
          if(all(tmp.total.support %in% unname(concept))){
            tmpRule <- list.remove(tmpRule, ei.name)
          }else{
            if(tmpRule[[ei.name]]$type == "nom"){
              values.list <- list.append(values.list, tmpRule[[ei.name]]$values)
            }else if(tmpRule[[ei.name]]$type  == "num"){
              values.list <- list.append(values.list, c(tmpRule[[ei.name]]$values1, tmpRule[[ei.name]]$values2))
            }else{
              stop("error : no right type")
            }
          }
          if(length(tmpRule) == 1){
            break  
          }
        }
      }else{
        if(tmpRule[[1]]$type == "nom"){
          values.list <- list.append(values.list, tmpRule[[1]]$values)
        }else if(tmpRule[[1]]$type  == "num"){
          values.list <- list.append(values.list, c(tmpRule[[1]]$values1, tmpRule[[1]]$values2))
        }else{
          stop("error : no right type")
        }
      }

      # ルール集合にtmpRuleを追加
      rule <- list(idx = integer(), values=list(), consequent=character(), support=integer())
      rule <- list(idx = list.select(tmpRule, idx) %>% list.mapv(idx) %>% unname(), 
                   values=values.list, 
                   consequent = conclusion, 
                   support = list.select(tmpRule, support) %>% list.common(support))
      rules <- list.append(rules, rule)
      
      # Gの更新（G := B - [T] のところ）
      #uncoveredConcept <- concept
      #for(len in 1:length(rules)){
      #  uncoveredConcept <- setdiff(uncoveredConcept, rules[[len]]$support)
      #}
      uncoveredConcept <- setdiff(concept, list.cases(rules, support))
    }
    
    # 最後のスクリーニング
    ind.rules <- which(list.mapv(rules, consequent) == conclusion)
    if(length(ind.rules) > 1){
      for(ind.rule in ind.rules){
        rules.except.one <- list.remove(rules, ind.rule)
        if(all(concept %in% list.cases(rules.except.one, support))){
          rules <- list.remove(rules, ind.rule)
        }        
      }
    }
    return(rules)
  #}
  })
  rules <- list()
  for(r in 1:length(Rules)){
    rules <- append(rules, Rules[[r]])
  }
  
  # simplicity conditions
  rules.simple <- list()
  for(ind.rule in 1:length(rules)){
    is.dup <- duplicated(rules[[ind.rule]]$idx)
    if(any(is.dup)){
      new.rule <- list(idx = integer(), values=list(), consequent=character(), support=integer())
      new.idx <- integer()
      new.values.list <- list()
      ind.dup <- unique(rules[[ind.rule]]$idx[is.dup])
      for(ind.idx in ind.dup){
        list.intervals <- rules[[ind.rule]]$values[rules[[ind.rule]]$idx == ind.idx] # MLEM2の性質上、大きさは2なはず
        vec.interval <- c(max(list.intervals[[1]][1],list.intervals[[2]][1]), 
                          min(list.intervals[[1]][2],list.intervals[[2]][2]))
        new.idx <- list.append(new.idx, ind.idx)
        new.values.list <- list.append(new.values.list, vec.interval)
      }
      ind.not.dup <- setdiff(rules[[ind.rule]]$idx, unique(rules[[ind.rule]]$idx[is.dup]))
      for(ind.idx in ind.not.dup){
        new.idx <- list.append(new.idx, ind.idx)
        new.values.list <- list.append(new.values.list, rules[[ind.rule]]$values[rules[[ind.rule]]$idx == ind.idx][[1]])
      }
      new.rule <- list(idx = new.idx, 
                       values = new.values.list, 
                       consequent = rules[[ind.rule]]$consequent, 
                       support = rules[[ind.rule]]$support)
      rules.simple <- list.append(rules.simple, new.rule)
    }else{
      rules.simple <- list.append(rules.simple, rules[[ind.rule]])
    }
  }
  
  #rules2 = unlist(rules.simple, recursive = FALSE)
  rules2 = rules.simple
  
  attr(rules2, "uniqueCls") <- as.character(sort(uniqueCls))
  attr(rules2, "clsProbs") <- clsFreqs/sum(clsFreqs)
  attr(rules2, "majorityCls") <- as.character(sort(uniqueCls)[which.max(clsFreqs)])
  attr(rules2, "method") <- "MLEM2Rules"
  attr(rules2, "dec.attr") <- decisionName
  attr(rules2, "colnames") <- colnames(decision.table)[-decIdx]
  
  # RuleSetRSTクラスを付与し、rulesの記述を指定フォーマットに変える
  source("~/roughsets/My.ObjectFactory.R")
  rules2 = My.ObjectFactory(rules2, classname = "RuleSetRST")
  
  return(rules2);
}

My.RI.LEM2Rules.RST <- function(decision.table)  {
  if (!inherits(decision.table, "DecisionTable")) {
    stop("Provided data should inherit from the \'DecisionTable\' class.")
  }
  
  if(is.null(attr(decision.table, "decision.attr"))) {
    stop("A decision attribute is not indicated.")
  } else {
    # 決定属性がある列を求める（irisなら5）
    decIdx = attr(decision.table, "decision.attr")
  }
  
  if(!all(attr(decision.table, "nominal.attrs"))) {
    stop("Some of the attributes are numerical.
         Discretize attributes before calling RST-based rule induction methods.")
  }
  ## 決定属性の決定クラスのFactor型ベクトルを求める（irisなら、決定クラス150要素）
  clsVec <- decision.table[,decIdx]
  ## ユニークな決定クラスを求める（irisなら、setosa、versicolor、virginicaの3つ） 
  uniqueCls <- unique(clsVec)
  ## 決定属性の列名を求める（irisなら、"Species"）
  decisionName = colnames(decision.table)[decIdx]
  ## 各決定クラスの度数を求める（irisなら、50,50,50）
  clsFreqs <- table(clsVec)
  
  ## 識別不能関係のリストを返す
  INDrelation = BC.IND.relation.RST(decision.table, (1:ncol(decision.table))[-decIdx])
  ## 各決定クラスの上下近似を求める
  approximations = BC.LU.approximation.RST(decision.table, INDrelation)
  lowerApproximations = approximations$lower.approximation
  ## 結局、下近似だけを使うので残りを削除
  rm(INDrelation, approximations)
  
  ## 各条件属性の取りうる条件属性値を返す
  descriptorsList = attr(decision.table, "desc.attrs")[-decIdx]
  ## 各条件属性の取りうる条件属性値をリスト構造を変えて返す
  descriptorCandidates = list()
  for (i in 1:length(descriptorsList)) {
    descriptorCandidates = c(descriptorCandidates,
                             lapply(descriptorsList[[i]],
                                    function(v, x) return(list(idx = x, values = v)), i))
  }
  
  ## ５つの要素を持つ条件属性ペアを返す(idx: int 4, values:chr "(0.867,1.6]", consequent: chr "versicolor", support   : int [1:48] 6 7 8 9 10 21 22 23 24 25 ..., laplace   : Named num 0.882)
  ### laplaceEstimate,関数は RuleInduction.OtherFuncCollections.Rにある。
  ### decision.tableがdata.table型だと動かないので注意
  attributeValuePairs = lapply(descriptorCandidates, 
                               laplaceEstimate, 
                               decision.table[,-decIdx], 
                               clsVec, 
                               uniqueCls)
  rm(descriptorsList, descriptorCandidates)
  print("debug : start rules")
  rules = list()
  # ecoliだとここで詰まる
  for(i in 1:length(lowerApproximations)) {
    print(paste("lowerAppr:",i,sep=""))
    rules[[i]] = computeLEM2covering(as.integer(lowerApproximations[[i]]), 
                                     attributeValuePairs, 
                                     clsVec, 
                                     uniqueCls)
  }
  print("debug : end rules")
  rules = unlist(rules, recursive = FALSE)
  rules = lapply(rules, function(x) laplaceEstimate(list(idx = x$idx, values = x$values), 
                                                    decision.table, clsVec, uniqueCls, suppIdx = x$support))
  
  attr(rules, "uniqueCls") <- as.character(sort(uniqueCls))
  attr(rules, "clsProbs") <- clsFreqs/sum(clsFreqs)
  attr(rules, "majorityCls") <- as.character(sort(uniqueCls)[which.max(clsFreqs)])
  attr(rules, "method") <- "LEM2Rules"
  attr(rules, "dec.attr") <- decisionName
  attr(rules, "colnames") <- colnames(decision.table)[-decIdx]
  
  # RuleSetRSTクラスを付与し、rulesの記述を指定フォーマットに変える
  source("~/roughsets/My.ObjectFactory.R")
  rules = My.ObjectFactory(rules, classname = "RuleSetRST")
  
  return(rules);
}