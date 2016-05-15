# 実験結果をまとめ、Latex形式で出力するもろもろ

# ===========================================
# ライブラリ読み込み
# ===========================================
library(dplyr)
library(readr)
library(data.table)
library(ggplot2)
library(stringr)
library(tidyr)
library(Hmisc)

# ===========================================
# データ読み込み
# ===========================================

df <- read_csv("../../python/Experiment/ExperimentsMLEM2.log",col_names = F)

# ===========================================
# データクレンジング
# ===========================================

df %>%
  setnames(c("date","code","method","k","filename","iter1","iter2","acc"))

df %>%
  filter(method == "MLEM2_LERS") %>%
  

# ===========================================
# 可視化
# ===========================================

# acc の boxplot
df %>%
  filter(method == "MLEM2_LERS" | 
         method == "MLEM2_RuleClusteringBySim_LERS" | 
         method == "MLEM2_RuleClusteringByRandom_LERS" |
         method == "MLEM2_RuleClusteringBySameCondition_LERS") %>%
  mutate(k = formatC(.$k, width=2, flag="0")) %>%
  mutate(k = as.character(k)) %>%
  ggplot(aes(x=k, y=acc, color=method)) +
    geom_boxplot() +
    facet_grid(filename~.)


# ===========================================
# latex 形式の表
# ===========================================
df %>%
  filter(method == "MLEM2_RuleClusteringBySim_LERS" | 
         method == "MLEM2_RuleClusteringByRandom_LERS" |
         method == "MLEM2_RuleClusteringBySameCondition_LERS") %>%
  mutate(k = formatC(.$k, width=2, flag="0")) %>%
  mutate(k = paste0("k=",as.character(k))) %>%
  mutate(method = factor(.$method, 
                        levels = c("MLEM2_RuleClusteringBySim_LERS",
                                   "MLEM2_RuleClusteringByRandom_LERS",
                                   "MLEM2_RuleClusteringBySameCondition_LERS"),
                        labels = c("Similarity",
                                   "Random",
                                   "Same Condition"))) %>%
  group_by(k, method) %>%
  summarise(mean_acc = format(round(mean(acc,na.rm=T),3),nsmall=3), sd_acc = format(round(sd(acc,na.rm=T),3),nsmall=3)) %>% 
  unite(col = result, mean_acc, sd_acc, sep="_{¥pm ") %>%
  mutate(result = paste0("$",result,"}$")) %>%
  spread(key = k, value = result) %>%
  data.frame(., row.names = .$method) %>%
  select(-method) %>%
  latex(
    file="",              # LaTeX ファイルの保存先
    title="Model",        # 1行1列目のセルの内容
    label="table1",       # LaTeX の \label に相当
    caption="table1の結果" # LaTeX の \caption に相当
  )
