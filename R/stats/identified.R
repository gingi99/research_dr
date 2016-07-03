# 特定度合いの実験結果をまとめ、Latex形式で出力するもろもろ

# ===========================================
# ライブラリ読み込み
# ===========================================
library(dplyr)
library(readr)
library(rlist)
library(data.table)
library(ggplot2)
library(stringr)
library(tidyr)
library(Hmisc)

# ===========================================
# データ読み込み
# ===========================================

FILENAME <- "hayes-roth"
DIRPATH <- paste0("/data/uci/",FILENAME)
files.all <- list.files(DIRPATH)
files.target <- files.all[str_detect(files.all, "Identify")]
df <- lapply(files.target, function(f){
  return(read_csv(paste0(DIRPATH,"/",f), col_names = F))
}) %>% list.stack()   

# ===========================================
# データクレンジング
# ===========================================

df %>%
  setnames(c("method","k","p","filename","iter1","iter2","identify"))

# ===========================================
# 可視化
# ===========================================

# identify の boxplot
df %>%
  filter(method == "Identify_MLEM2" | 
         method == "Identify_MLEM2_OnlyK" | 
         method == "Identify_MLEM2_Random" |
         method == "Identify_MLEM2_SameCondition" |
         method == "Identify_MLEM2_RuleClusteringByConsistentSim" |
         method == "Identify_MLEM2_RuleClusteringByConsistentSimExceptMRule") %>%
  mutate(k = formatC(.$k, width=2, flag="0")) %>%
  mutate(k = as.character(k)) %>%
  ggplot(aes(x=k, y=identify, color=method)) +
    geom_boxplot() +
    facet_grid(filename~p) +
    theme(legend.position = "bottom")

# identify の 平均線
df %>%
  filter(method == "Identify_MLEM2" | 
           method == "Identify_MLEM2_OnlyK" | 
           method == "Identify_MLEM2_Random" |
           method == "Identify_MLEM2_SameCondition" |
           method == "Identify_MLEM2_RuleClusteringByConsistentSim" |
           method == "Identify_MLEM2_RuleClusteringByConsistentSimExceptMRule") %>%
  mutate(k = formatC(.$k, width=2, flag="0")) %>%
  mutate(k = as.character(k)) %>%
  group_by(filename, k, p, method) %>%
  summarise(mean_identify = mean(identify,na.rm=T), 
            sd_identify = sd(identify,na.rm=T)) %>% 
  ggplot(aes(x=k, y=mean_identify, group = method, color=method)) +
    geom_line() +
    geom_point(size=3, shape = 21) +
    facet_grid(p~filename) +
    scale_y_continuous(breaks = seq(0.0,1.0,by=0.1)) +
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
  filter(method == "Identify_MLEM2") %>%
  group_by(p) %>%
  summarise(mean_acc = format(round(mean(identify,na.rm=T),3),nsmall=3), 
            sd_acc = format(round(sd(identify,na.rm=T),3),nsmall=3))

# ===========================================
# latex 形式の表
# ===========================================
df %>%
  filter(method == "Identify_MLEM2_OnlyK" | 
         method == "Identify_MLEM2_Random" |
         method == "Identify_MLEM2_SameCondition" |
         method == "Identify_MLEM2_RuleClusteringByConsistentSim" |
         method == "Identify_MLEM2_RuleClusteringByConsistentSimExceptMRule") %>%
  #mutate(k = formatC(.$k, width=2, flag="0")) %>%
  #mutate(k = paste0("k=",as.character(k))) %>%
  mutate(method = factor(.$method, 
                         levels = c("Identify_MLEM2_RuleClusteringByConsistentSim",
                                    "Identify_MLEM2_RuleClusteringByConsistentSimExceptMRule",
                                    "Identify_MLEM2_Random",
                                    "Identify_MLEM2_SameCondition",
                                    "Identify_MLEM2_OnlyK"),
                         labels = c("提案法1",
                                    "提案法2",
                                    "Random",
                                    "Same Condition",
                                    "Only K Rules"))) %>%
  group_by(k,p,method) %>%
  summarise(mean_acc = format(round(mean(identify,na.rm=T),3),nsmall=3), 
            sd_acc = format(round(sd(identify,na.rm=T),3),nsmall=3)) %>% 
  unite(col = result, mean_acc, sd_acc, sep="_{\\pm ") %>%
  mutate(result = paste0("$",result,"}$")) %>%
  spread(key = method, value = result) %>%
  filter(k == 2 | k == 4 | k == 6 | k == 8) %>%
  ungroup() %>%
  arrange(p) %>%
  data.frame(., row.names = paste0("(",.$p,",",.$k,")")) %>%
  select(-k,-p) %>%
  latex(
    file="",              # LaTeX ファイルの保存先
    title="(p,k)",            # 1行1列目のセルの内容
    label="comparison_identify",       # LaTeX の \label に相当
    caption="特定度合いの実験結果" # LaTeX の \caption に相当
  )

