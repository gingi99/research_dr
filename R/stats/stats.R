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

FILENAME <- "nursery"
DIRPATH <- paste0("/data/uci/",FILENAME)
files.all <- list.files(DIRPATH)
files.target <- files.all[str_detect(files.all, "LERS")]
df <- lapply(files.target, function(f){
  return(read_csv(paste0(DIRPATH,"/",f), col_names = F))
}) %>% list.stack()   

# hayes-rothのみ
df <- read_csv("/Users/ooki/git/research_dr/python/Experiment/hayes-roth-mlem2.log",col_names = F)

# ===========================================
# データクレンジング
# ===========================================

df %>%
  setnames(c("date","code","method","k","filename","iter1","iter2","acc"))
df %>%
  setnames(c("method","k","filename","iter1","iter2","acc"))

# ===========================================
# 可視化
# ===========================================

# acc の boxplot
df %>%
  filter(method == "MLEM2_LERS" | 
         method == "MLEM2_OnlyK_LERS" | 
         #method == "MLEM2_RuleClusteringBySim_LERS" | 
         method == "MLEM2_RuleClusteringByRandom_LERS" |
         method == "MLEM2_RuleClusteringBySameCondition_LERS" |
         method == "MLEM2_RuleClusteringByConsistentSim_LERS" |
         method == "MLEM2_RuleClusteringByConsistentSimExceptMRule_LERS") %>%
  mutate(k = formatC(.$k, width=2, flag="0")) %>%
  mutate(k = as.character(k)) %>%
  ggplot(aes(x=k, y=acc, color=method)) +
    geom_boxplot() +
    facet_grid(filename~.) +
    theme(legend.position = "bottom")

# acc の 平均線
df %>%
  filter(method == "MLEM2_LERS" | 
           method == "MLEM2_OnlyK_LERS" | 
           #method == "MLEM2_RuleClusteringBySim_LERS" | 
           method == "MLEM2_RuleClusteringByRandom_LERS" |
           method == "MLEM2_RuleClusteringBySameCondition_LERS" |
           method == "MLEM2_RuleClusteringByConsistentSim_LERS" |
           method == "MLEM2_RuleClusteringByConsistentSimExceptMRule_LERS") %>%
  mutate(k = formatC(.$k, width=2, flag="0")) %>%
  mutate(k = as.character(k)) %>%
  group_by(filename, k, method) %>%
  summarise(mean_acc = mean(acc,na.rm=T), 
            sd_acc = sd(acc,na.rm=T)) %>% 
  ggplot(aes(x=k, y=mean_acc, group = method, color=method)) +
    geom_line() +
    geom_point(size=3, shape = 21) +
    #geom_text(aes(x="01", y=mean_acc, label=method))
    facet_grid(filename~.) +
    scale_color_brewer(palette = "Set1") +
    labs(x="k", y="正答率の平均値") +
    theme_bw(base_family = "HiraKakuProN-W3") +
    theme(axis.title.x = element_text(size=15)) +
    theme(axis.text.x = element_text(size=12)) +
    theme(axis.title.y = element_text(size=15)) +
    theme(axis.text.y = element_text(size=12)) +
    theme(legend.position = "bottom")

# ===========================================
# MLEM2 のみ
# ===========================================
df %>%
  filter(method == "MLEM2_LERS") %>%
  group_by(method) %>%
  summarise(mean_acc = format(round(mean(acc,na.rm=T),3),nsmall=3), 
            sd_acc = format(round(sd(acc,na.rm=T),3),nsmall=3))

# ===========================================
# latex 形式の表
# ===========================================
df %>%
  filter(method == "MLEM2_RuleClusteringByConsistentSim_LERS" |
         method == "MLEM2_RuleClusteringByConsistentSimExceptMRule_LERS" |
         method == "MLEM2_RuleClusteringByRandom_LERS" |
         method == "MLEM2_RuleClusteringBySameCondition_LERS" |
         method == "MLEM2_OnlyK_LERS") %>%
  mutate(k = formatC(.$k, width=2, flag="0")) %>%
  #mutate(k = paste0("k=",as.character(k))) %>%
  mutate(method = factor(.$method, 
                        levels = c("MLEM2_RuleClusteringByConsistentSim_LERS",
                                   "MLEM2_RuleClusteringByConsistentSimExceptMRule_LERS",
                                   "MLEM2_RuleClusteringByRandom_LERS",
                                   "MLEM2_RuleClusteringBySameCondition_LERS",
                                   "MLEM2_OnlyK_LERS"),
                        labels = c("提案法1",
                                   "提案法2",
                                   "Random",
                                   "Same Condition",
                                   "Only K Rules"))) %>%
  group_by(k, method) %>%
  summarise(mean_acc = format(round(mean(acc,na.rm=T),3),nsmall=3), sd_acc = format(round(sd(acc,na.rm=T),3),nsmall=3)) %>% 
  unite(col = result, mean_acc, sd_acc, sep="_{\\pm ") %>%
  mutate(result = paste0("$",result,"}$")) %>%
  spread(key = method, value = result) %>%
  data.frame(., row.names = .$k) %>%
  select(-k) %>%
  latex(
    file="",              # LaTeX ファイルの保存先
    title="k",            # 1行1列目のセルの内容
    label="comparison",       # LaTeX の \label に相当
    caption="正答率の実験結果" # LaTeX の \caption に相当
  )
