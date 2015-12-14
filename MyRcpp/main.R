# Rcpp ロード
library(Rcpp)
library(rbenchmark)
library(microbenchmark)

# サンプル1
sourceCpp("/home/ooki/R/MyRcpp/mysource01.cpp") # ローカルのC++ソースファイルをロード
returnMaxCpp(c(-1,0,1,2,3))

# サンプル2
sourceCpp("/home/ooki/R/MyRcpp/mysource02.cpp")
timesTwo(2)
lapply1(rnorm(10), function(x){x*2})

### ネイティブのR関数には負けるみたい。
benchmark(lapply1(rnorm(100), function(x){x*2}),
          lapply(rnorm(100), function(x){x*2}),
          order="relative",
          replications = 10)

## サンプル3
returnMaxR <- function(x) {
  length <- length(x) # length of given vector x
  temp_max <- x[1]
  for(i in 1:length) {
    if (x[i] > temp_max) {
      temp_max = x[i]
    }
  }
  
  return(temp_max)
}
sourceCpp("/home/ooki/R/MyRcpp/mysource03.cpp")
returnMaxCpp(rnorm(3))

### ネイティブR max() には負けるが、R実装よりは早い。
benchmark(returnMaxCpp(rnorm(1000)),
          returnMaxR(rnorm(1000)),
          max(rnorm(1000)),
          order="relative",
          replications = 1000)

## サンプル4
df1 <- convert_df_from_rules(rules)
mat1 <- cal_dist_rules(df1)
sourceCpp("/home/ooki/R/MyRcpp/RuleClustering.cpp")
is_naC(c(1,NA,3))
f4(x)
attribs(a)
convert_df_from_rules_Rcpp(rules)
dist_kusunoki_Rcpp(x, y)

# test1
df <- convert_df_from_rules(rules)
df$class <- as.character(df$class)
list.df <- do.call(Zip, df)
aaa <- cal_dist_rules_Rcpp(df, list.df)
benchmark(cal_dist_rules(df),
          cal_dist_rules_Rcpp(df, list.df),
          order="relative",
          replications=200)

## サンプル5
sourceCpp("/home/ooki/R/MyRcpp/MLEM2.cpp")
benchmark(cover_num(TG, unname(uncoveredConcept)),
          sapply(TG, function(tg){
            length(intersect(uncoveredConcept, tg$support))
          }),
          order = "relative",
          replications=200)
microbenchmark(cover_num(TG, unname(uncoveredConcept)),
               sapply(TG, function(tg){
                 length(intersect(uncoveredConcept, tg$support))
               }))


#######################################################
### Rule Clustering Rcpp 化にむけてここにおいただけ
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
      # valuesが複数持つ場合に応じて条件分岐
      if(length(values[[i]]) == 1){
        df.onerule[1,idx[i]] <- values[[i]]
      }else{
        df.onerule[1,idx[i]] <- values[[i]][1]
      }
    }
    # 結論部が複数持つ場合に応じて条件分岐
    if(length(rule$consequent) == 1){
      df.onerule[1, decision_attr] <- rule$consequent
    }else{
      df.onerule[1, decision_attr] <- rule$consequent[1]
    }
    return(df.onerule)
  })
  df <- list.stack(list.df)
  return(df)
}

# データフレームをリストにする関数
Zip <- function(...) Map(list, ...)

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

dist_kusunoki <- function(x, y){
  len <- length(x)
  ans <- 0.0
  for(i in 1:len){
    # 両要素ともNAなら0
    if(all(is.na(c(x[[i]], y[[i]])))){
      v <- 0.0
    } else {
      # どちらかがNAなら1
      if(any(is.na(c(x[[i]], y[[i]])))){
        v <- 1.0
      }else{
        if(x[[i]] == "numeric"){
          v <- (x[[i]] - y[[i]])/(3.0 * sd)
          if(v > 1.0){
            v <- 1.0
          }
        }else{
          if(x[[i]] == y[[i]]){
            v <- 0.0
          }else{
            v <- 1.0
          }
        }
      }
    }
    ans <- ans + v
  }
  ans <- ans / len
  return(ans)
}
