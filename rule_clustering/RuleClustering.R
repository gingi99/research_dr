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



