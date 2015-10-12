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

## ルール間の距離から、ルールを併合して新しいルールを作る
recreate_rules_by_dist <- function(mat.dist, rules, k){
  for(di in 1:length(rules)){
    mat.dist[di, di] <- Inf
  }
  vec.supportsize <- sapply(rules, function(rule){
    return(length(rule$support))
  })
  minValue <- min(vec.supportsize)
  # support sizeがk以下のルールがある内は繰り返す
  while(minValue < k){
    ind.minValue <- which(vec.supportsize == minValue)
    if(length(ind.minValue) == 1){
      ind.merge.target.rule <- ind.minValue
    }else{
      ind.merge.target.rule <- ind.minValue[1]
    }
    vec.dist <- mat.dist[ind.merge.target.rule,] 
    minValue <- min(vec.dist)
    # 最も距離が近いルールを求める
    ind.minValue <- which(vec.dist == minValue)
    if(length(ind.minValue) == 1){
      rule.new <- mergeRules(rules[[ind.merge.target.rule]], rules[[ind.minValue]])
    }else{
      # 結論部が同じルールかどうか
      vec.consequent <- sapply(ind.minValue, function(x){
        return(rules[[x]]$consequent)
      })
      ind.minValue <- ind.minValue[vec.consequent == rules[[ind.merge.target.rule]]$consequent]
      if(length(ind.minValue) == 1){
        rule.new <- mergeRules(rules[[ind.merge.target.rule]], rules[[ind.minValue]])
      }else{
        # 条件部を構成する属性名がなるべく同じであるか
        vec.match.length.idx <- sapply(ind.minValue, function(x){
          return(length(intersect(rules[[x]]$idx, rules[[ind.merge.target.rule]]$idx)))
        })
        minValue <- min(vec.match.length.idx)
        ind.minValue <- ind.minValue[vec.match.length.idx == minValue]
        if(length(ind.minValue) == 1){
          rule.new <- mergeRules(rules[[ind.merge.target.rule]], rules[[ind.minValue]])
        }else{
          # support sizeが小さいルールにマージする
          minValue <- min(vec.supportsize[ind.minValue])
          ind.minValue <- ind.minValue[which(vec.supportsize[ind.minValue] == minValue)]
          if(length(ind.minValue) == 1){
            rule.new <- mergeRules(rules[[ind.merge.target.rule]], rules[[ind.minValue]])
          }else{
            # なければ、候補ルールの中の最初のルールとマージする
            ind.minValue <- ind.minValue[1]
            rule.new <- mergeRules(rules[[ind.merge.target.rule]], rules[[ind.minValue])
          }
        }
      }
    }
    rules <- rules[-c(ind.merge.target.rule,ind.minValue)]
    rules <- list.append(rules, rule.new)
    vec.supportsize <- sapply(rules, function(rule){
      return(length(rule$support))
    })
    minValue <- min(vec.supportsize)
  }
  return(rules)
}

## 2つのルールをマージして新しいルールを作る
mergeRule <- function(rule1, rule2){
  
  return(rule)
}


