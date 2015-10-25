## Rule をクラスタリングする
library(rlist)
source("~/R/ppdm/cluster.R")
source("~/R/ppdm/get_PPDM_Measure.R")

# ルールの集合rulesをdfに変換する関数
convert_df_from_rules <- function(rules){
  condition_attr <- attributes(rules)$colnames
  decision_attr <- attributes(rules)$dec.attr
  list.df <- lapply(rules, function(rule){
    idx <- rule$idx
    values <- rule$values
    df.onerule <- data.frame(matrix(vector(), 0, length(c(condition_attr, decision_attr)), 
                            dimnames=list(c(), 
                                          c(condition_attr, decision_attr))), stringsAsFactors=F)
    for(i in 1:length(idx)){
      df.onerule[1,idx[i]] <- values[[i]]
    }
    df.onerule[1, decision_attr] <- rule$consequent
    return(df.onerule)
  })  
  df <- list.stack(list.df)
  return(df)
}

## ルール間の距離をルールの集合dfから求める
cal_dist_rules <- function(df){
  list.df <- do.call(Zip, df)
  mat.df.dist <- matrix(0.0, nrow=nrow(df), ncol=nrow(df))
  for(i in 1:(nrow(df)-1)){
    for(j in (i+1):nrow(df)){
      x <- list.df[[i]] 
      y <- list.df[[j]]
      mat.df.dist[i,j] <- dist_kusunoki(x,y)
      mat.df.dist[j,i] <- dist_kusunoki(x,y)
    }
  }
  return(mat.df.dist)
  #clust.df <- hclust(as.dist(mat.df.dist), method = 'ward.D2')
  #plot(clust.df)
}

## 2つのルールをマージして新しいルールを作る
mergeRules <- function(rule1, rule2){
  #print(rule1)
  #print(rule2)
  
  # 2つのルールに両方持つ条件属性集合を抽出
  idxs <- intersect(rule1$idx, rule2$idx)
  
  # 属性値リストの定義
  list.values.new <- list()
  len.idxs <- length(idxs)
  for(ind.idx in 1:len.idxs){
    ## num
    if(is.numeric(rule1$values[[ind.idx]])){
      # 小さい値
      # min.value
      # 大きい値
      # max.value
      # values.list <- list.append(values.list, c(min.value, max.value))
    }
    ## nom
    else{
      # 指定した条件属性のルールの値が一致したら
      if(rule1$values[[which(idxs[ind.idx] == rule1$idx)]] == 
           rule2$values[[which(idxs[ind.idx] == rule2$idx)]]){
        list.values.new <- list.append(list.values.new, 
                                       rule1$values[[which(idxs[ind.idx] == rule1$idx)]])
      }else{
        list.values.new <- list.append(list.values.new, 
                                       c(rule1$values[[which(idxs[ind.idx] == rule1$idx)]], 
                                         rule2$values[[which(idxs[ind.idx] == rule2$idx)]]))
      }
    }
  }
  # consequentの計算
  if(rule1$consequent == rule2$consequent){
    consequent.new <- rule1$consequent
  }else{
    consequent.new <- c(rule1$consequent,rule2$consequent)
  }
  # support数の計算
  suport.new <- sort(union(rule1$support, rule2$support))
  # 新ルールを生成
  rule.new <- list(idx = idxs, 
                   values=list.values.new, 
                   consequent = consequent.new, 
                   support = suport.new)
  
  return(rule.new)
}


## ルール間の距離から、ルールを併合して新しいルールを作る
recreate_rules_by_dist <- function(mat.df.dist, rules, k=3){
  # 初期化
  rules.new <- rules 
  for(di in 1:length(rules)){
    mat.df.dist[di, di] <- Inf
  }
  vec.supportsize <- sapply(rules, function(rule){
    return(length(rule$support))
  })
  minSupportValue <- min(vec.supportsize)
  # support sizeがk以下のルールがある内は繰り返す
  while(minSupportValue < k){
    ind.minValue <- which(vec.supportsize == minSupportValue)
    if(length(ind.minValue) == 1){
      ind.merge.target.rule <- ind.minValue
    }else{
      ind.merge.target.rule <- ind.minValue[1]
    }
    vec.dist <- mat.df.dist[ind.merge.target.rule,] 
    minDistValue <- min(vec.dist)
    # 最も距離が近いルールを求める
    ind.minDistValue <- which(vec.dist == minDistValue)
    if(length(ind.minDistValue) == 1){
      ind.merge.target.rule2 <- ind.minDistValue
      rule.new <- mergeRules(rules[[ind.merge.target.rule]], rules[[ind.merge.target.rule2]])
    }else{
      # 結論部が同じルールかどうか
      vec.consequent <- sapply(ind.minDistValue, function(x){
        return(rules[[x]]$consequent)
      })
      ind.minConsequentValue <- ind.minDistValue[vec.consequent == rules[[ind.merge.target.rule]]$consequent]
      # 結論部が同じルールが1つ
      if(length(ind.minConsequentValue) == 1){
        ind.merge.target.rule2 <- ind.minConsequentValue
        rule.new <- mergeRules(rules[[ind.merge.target.rule]], rules[[ind.merge.target.rule2]])
      # 結論部が同じルールが2つ以上 or ない
      }else{
        # ないなら、距離が小さいルールを再度入れなおす
        if(length(ind.minConsequentValue) == 0){
          ind.minConsequentValue <- ind.minDistValue
        }
        # 条件部を構成する属性名がなるべく同じであるか
        vec.match.length.idx <- sapply(ind.minConsequentValue, function(x){
          return(length(intersect(rules[[x]]$idx, rules[[ind.merge.target.rule]]$idx)))
        })
        maxConditionValue <- max(vec.match.length.idx)
        ind.maxConditionValue <- ind.minConsequentValue[vec.match.length.idx == maxConditionValue]
        if(length(ind.maxConditionValue) == 1){
          ind.merge.target.rule2 <- ind.maxConditionValue
          rule.new <- mergeRules(rules[[ind.merge.target.rule]], rules[[ind.merge.target.rule2]])
        }else{
          # support sizeが小さいルールにマージする
          minSupportValue <- min(vec.supportsize[ind.maxConditionValue])
          ind.minSupportValue <- ind.maxConditionValue[which(vec.supportsize[ind.maxConditionValue] == minSupportValue)]
          if(length(ind.minSupportValue) == 1){
            ind.merge.target.rule2 <- ind.minSupportValue
            rule.new <- mergeRules(rules[[ind.merge.target.rule]], rules[[ind.merge.target.rule2]])
          }else{
            # なければ、候補ルールの中の最初のルールとマージする
            ind.merge.target.rule2 <- ind.minSupportValue[1]
            rule.new <- mergeRules(rules[[ind.merge.target.rule]], rules[[ind.merge.target.rule2]])
          }
        }
      }
    }
    rules.new <- rules.new[-c(ind.merge.target.rule, ind.merge.target.rule2)]
    rules.new <- list.append(rules.new, rule.new)
    vec.supportsize <- sapply(rules.new, function(rule){
      return(length(rule$support))
    })
    print(vec.supportsize)
    minSupportValue <- min(vec.supportsize)
  }
  
  # attributeをつける
  attr(rules.new, "uniqueCls") <- attributes(rules)$uniqueCls
  attr(rules.new, "clsProbs") <- attributes(rules)$clsProbs
  attr(rules.new, "majorityCls") <- attributes(rules)$majorityCls
  attr(rules.new, "method") <- "MLEM2Rules"
  attr(rules.new, "dec.attr") <- attributes(rules)$dec.attr
  attr(rules.new, "colnames") <- attributes(rules)$colnames
  
  # RuleSetRSTクラスを付与し、rulesの記述を指定フォーマットに変える
  source("~/R/roughsets/My.ObjectFactory.R")
  rules.new <- My.ObjectFactory(rules.new, classname = "RuleSetRST")
  return(rules.new)
}

# main 関数
get_rule_clustering <- function(rules, k=3){
  df.rules <- convert_df_from_rules(rules)
  mat.df.dist <- cal_dist_rules(df.rules)
  rules.new <- recreate_rules_by_dist(mat.df.dist, rules, k)
  return(rules.new)
}



