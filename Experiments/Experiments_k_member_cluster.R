# パス追加
.libPaths(c("/home/ooki/R/x86_64-pc-linux-gnu-library/3.1", .libPaths()))

#パッケージ
library(tidyr)
library(ggplot2)
library(rlist)
library(readr)
library(data.table)
library(dplyr)
library(pipeR)
library(RoughSets)
library(pforeach)

# 初期設定
rm(list = ls())
#kFilenames <- c("hayes-roth", "iris", "wine", "zoo")
fn <- "iris"
kIter1 <- 10
kIter2 <- 10
#mgs <- 1
mgs <- "max"
rpm <- "Merged"
#rpm <- "Randomed"
kAnomalities <- seq(1, 10, by=1)

# MLEM2 実験
source("~/R/roughsets/getResults_by_MLEME2.R")

# kAnomalyiesの実験
results <- list()
results <- pforeach(k = kAnomalities, .c=list)({
  getResults_by_MLEM2(kFilenames = fn,
                      kIter1 = kIter1, 
                      kIter2 = kIter2,
                      kms = 0,
                      kmr = 0,
                      mgs = mgs,
                      rpm = rpm,
                      k = k)
})
names(results) <- c(paste(fn, kAnomalities, sep=""))

# accurayを取る
dt.results <- data.table()
for(n in 1:length(fn)){
  dt.results <- rbind_list(dt.results, data.table(
    km00 = list.mapv(results[[10*n - 9]][[1]], precision) %>% unname %>% as.numeric,
    km01 = list.mapv(results[[10*n - 8]][[1]], precision) %>% unname %>% as.numeric,
    #km02 = list.mapv(results[[10*n - 7]][[1]], precision) %>% unname %>% as.numeric,
    #km03 = list.mapv(results[[10*n - 6]][[1]], precision) %>% unname %>% as.numeric,
    #km04 = list.mapv(results[[10*n - 5]][[1]], precision) %>% unname %>% as.numeric,
    #km05 = list.mapv(results[[10*n - 4]][[1]], precision) %>% unname %>% as.numeric,
    #km06 = list.mapv(results[[10*n - 3]][[1]], precision) %>% unname %>% as.numeric,
    #km07 = list.mapv(results[[10*n - 2]][[1]], precision) %>% unname %>% as.numeric,
    #km08 = list.mapv(results[[10*n - 1]][[1]], precision) %>% unname %>% as.numeric,
    #km09 = list.mapv(results[[10*n - 0]][[1]], precision) %>% unname %>% as.numeric,
    fn    = names(results[[10*n - 9]]))
  )
}
#setnames(dt.results, c(paste("kms", kMerged.size, sep=""), "fn"))

# entropyを取る
dt.entropy <- data.table()
for(n in 1:length(fn)){
  dt.entropy <- rbind_list(dt.entropy, data.table(
    km00 = list.mapv(results[[10*n - 9]][[1]], entropy) %>% unname %>% as.numeric,
    km01 = list.mapv(results[[10*n - 8]][[1]], entropy) %>% unname %>% as.numeric,
    km02 = list.mapv(results[[10*n - 7]][[1]], entropy) %>% unname %>% as.numeric,
    km03 = list.mapv(results[[10*n - 6]][[1]], entropy) %>% unname %>% as.numeric,
    km04 = list.mapv(results[[10*n - 5]][[1]], entropy) %>% unname %>% as.numeric,
    km05 = list.mapv(results[[10*n - 4]][[1]], entropy) %>% unname %>% as.numeric,
    km06 = list.mapv(results[[10*n - 3]][[1]], entropy) %>% unname %>% as.numeric,
    km07 = list.mapv(results[[10*n - 2]][[1]], entropy) %>% unname %>% as.numeric,
    km08 = list.mapv(results[[10*n - 1]][[1]], entropy) %>% unname %>% as.numeric,
    km09 = list.mapv(results[[10*n - 0]][[1]], entropy) %>% unname %>% as.numeric,
    fn    = names(results[[10*n - 9]]))
  )
}
#setnames(dt.entropy, c(paste("kms", kMerged.size, sep=""), "fn"))

# t検定
vec.pvalues.precision <- sapply(dplyr::select(dt.results, 2:10), function(result){
  p <- t.test(dt.results$km00, result)$p.value
  if(p <= 0.01){
    return("< 0.01")
  }else if(p > 0.01 & p <= 0.05){
    return("0.01 < p < 0.05")
  }else{
    return("no sig-diff")
  }
})
df.pvalues.precision <- data.frame(var  = as.factor(c("km00", names(vec.pvalues.precision))),
                                   tval = c("no sig-diff", unname(vec.pvalues.precision)))

# パレート可視化
dt.results %>>%
  gather(var, val, -fn) %>%
  inner_join(df.pvalues.precision, by="var") %>%
  ggplot() +
    geom_boxplot(aes(x=var, y=val, color=tval)) +
    geom_line(data = dt.results %>% gather(var, val, -fn) %>% group_by(fn, var) %>% 
                dplyr::summarise(m = mean(val)), 
              aes(x=var, y=m, group=1), size=rev(0.8)) +
    geom_point(data = dt.results %>% gather(var, val, -fn) %>% group_by(fn,var) %>% 
                 dplyr::summarise(m = mean(val)), 
               aes(x=var, y=m, group=1), shape=21, size=1.5) +
    facet_grid(fn~.) + 
  　scale_y_continuous(breaks=seq(0.0, 1.0, by=0.1)) +
    labs(x="k member clustering", y="分類精度") +
    scale_color_discrete(name="t検定によるp値の結果") -> gg
print(gg)
#ggsave(file="aaa.png", plot=gg, dpi = 320, width = 12, height = 8.52)
  
# t検定
vec.pvalues.entropy <- sapply(dplyr::select(dt.entropy, 1:10), function(entropy){
  p <- t.test(dt.entropy$km00, entropy)$p.value
  if(p <= 0.01){
    return("< 0.01")
  }else if(p > 0.01 & p <= 0.05){
    return("0.01 < p < 0.05")
  }else{
    return("no sig-diff")
  }
})
df.pvalues.entropy <- data.frame(var  = as.factor(names(vec.pvalues.entropy)),
                                 tval = unname(vec.pvalues.entropy))

# パレート Entropy 可視化
dt.entropy %>>%
  gather(var, val, -fn) %>%
  inner_join(df.pvalues.entropy, by="var") %>%
  ggplot() +
    geom_boxplot(aes(x=var, y=val, color=tval)) +
    geom_line(data = dt.entropy %>% gather(var, val, -fn) %>% group_by(fn,var) %>% summarise(m = mean(val)), 
            aes(x=var, y=m, group=1), size=rev(0.8)) +
    geom_point(data = dt.entropy %>% gather(var, val, -fn) %>% group_by(fn,var) %>% summarise(m = mean(val)), 
             aes(x=var, y=m, group=1), shape=21, size=1.5) +
    facet_grid(fn~.) +
    labs(x="pp cluster value", y="エントロピー") +
    scale_color_discrete(name="t検定によるp値の結果")-> gg
print(gg)
ggsave(file="aaa.png", plot=gg, dpi = 320, width = 12, height = 8.52)
