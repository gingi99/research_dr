# 分類精度の実験結果をまとめ、Latex形式で出力するもろもろ

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
library(rlist)

# ===========================================
# データ読み込み
# ===========================================

FILENAME <- "adult_cleansing2"
FILENAME <- "default_cleansing"
FILENAME <- "german_credit_categorical"
FILENAME <- "hayes-roth"
FILENAME <- "nursery"
FILENAMES <- c("adult_cleansing2", "default_cleansing", "german_credit_categorical", "hayes-roth", "nursery")
DIRPATH <- paste0("/mnt/data/uci/",FILENAMES)
files.all <- list.files(DIRPATH, full.names=T)
files.target <- files.all[str_detect(files.all, "STAT")]
df <- lapply(files.target, function(f){
  return(read_csv(f, col_names = F))
}) %>% list.stack()   

# ===========================================
# データクレンジング
# ===========================================
df %>%
  setnames(c("method","k","filename","iter1","iter2","num","len","support"))

# ===========================================
# MLEM2 のみ
# ===========================================
df %>%
  filter(method == "MLEM2_STAT") %>%
  group_by(method,filename) %>%
  summarise(mean_num = format(round(mean(num,na.rm=T),3),nsmall=3), 
            sd_num = format(round(sd(num,na.rm=T),3),nsmall=3),
            mean_len = format(round(mean(len,na.rm=T),3),nsmall=3), 
            sd_len = format(round(sd(len,na.rm=T),3),nsmall=3),
            mean_support = format(round(mean(support,na.rm=T),3),nsmall=3), 
            sd_support = format(round(sd(support,na.rm=T),3),nsmall=3))

# ===========================================
# latex 形式の表(横長)
# ===========================================
df %>%
  filter(#method == "MLEM2_RuleClusteringByConsistentSim_LERS" |
      method == "MLEM2_RuleClusteringByConsistentTimesSimExceptMRule_STAT" |
      method == "MLEM2_RuleClusteringBySimExceptMRule_STAT" |
      method == "MLEM2_RuleClusteringByConsistentExceptMRule_STAT" |
      method == "MLEM2_RuleClusteringByRandom_STAT" |
      method == "MLEM2_RuleClusteringBySameCondition_STAT" |
      method == "MLEM2_OnlyK_STAT") %>%
  mutate(k = formatC(.$k, width=2, flag="0")) %>%
  mutate(k = paste0("k=",as.character(k))) %>%
  mutate(method = factor(.$method, 
                         levels = c(#"MLEM2_RuleClusteringByConsistentSim_LERS",
                           "MLEM2_RuleClusteringByConsistentTimesSimExceptMRule_STAT",
                           "MLEM2_RuleClusteringBySimExceptMRule_STAT",
                           "MLEM2_RuleClusteringByConsistentExceptMRule_STAT",
                           "MLEM2_RuleClusteringByRandom_STAT",
                           "MLEM2_RuleClusteringBySameCondition_STAT",
                           "MLEM2_OnlyK_STAT"),
                         labels = c(#"提案法1",
                           "Sim $\\times$ Con",
                           "Sim",
                           "Con",
                           "Random",
                           "Match",
                           "Only $k$"))) %>%
  group_by(k, method) %>%
  summarise(mean_num = format(round(mean(num,na.rm=T),3),nsmall=3), 
            sd_num = format(round(sd(num,na.rm=T),3),nsmall=3),
            mean_len = format(round(mean(len,na.rm=T),3),nsmall=3), 
            sd_len = format(round(sd(len,na.rm=T),3),nsmall=3),
            mean_support = format(round(mean(support,na.rm=T),3),nsmall=3), 
            sd_support = format(round(sd(support,na.rm=T),3),nsmall=3)) %>% 
  unite(col = num, mean_num, sd_num, sep="_{\\pm ") %>%
  mutate(num = paste0("$",num,"}$")) %>%
  unite(col = len, mean_len, sd_len, sep="_{\\pm ") %>%
  mutate(len = paste0("$",len,"}$")) %>%
  unite(col = support, mean_support, sd_support, sep="_{\\pm ") %>%
  mutate(support = paste0("$",support,"}$")) %>%
  latex(
    file="",              # LaTeX ファイルの保存先
    title="",            # 1行1列目のセルの内容
    label="comparison",       # LaTeX の \label に相当
    caption="実験結果", # LaTeX の \caption に相当
    rowname=NULL
  )
  
  spread(key = k, value = result) %>%
  data.frame(., row.names = .$method) %>%
  select(-method) %>%
  latex(
    file="",              # LaTeX ファイルの保存先
    title="Method",            # 1行1列目のセルの内容
    label="comparison",       # LaTeX の \label に相当
    caption="正答率の実験結果" # LaTeX の \caption に相当
  )

  
# ===========================================
# 可視化
# ===========================================
df %>%
  filter(#method == "MLEM2_RuleClusteringByConsistentSim_LERS" |
    method == "MLEM2_RuleClusteringByConsistentTimesSimExceptMRule_STAT" |
    method == "MLEM2_RuleClusteringBySimExceptMRule_STAT" |
    method == "MLEM2_RuleClusteringByConsistentExceptMRule_STAT" |
    method == "MLEM2_RuleClusteringByRandom_STAT" |
    method == "MLEM2_RuleClusteringBySameCondition_STAT" |
    method == "MLEM2_OnlyK_STAT") %>%
  mutate(k = formatC(.$k, width=2, flag="0")) %>%
  mutate(k = paste0("k=",as.character(k))) %>%
  mutate(method = factor(.$method, 
                           levels = c(#"MLEM2_RuleClusteringByConsistentSim_LERS",
                             "MLEM2_RuleClusteringByConsistentTimesSimExceptMRule_STAT",
                             "MLEM2_RuleClusteringBySimExceptMRule_STAT",
                             "MLEM2_RuleClusteringByConsistentExceptMRule_STAT",
                             "MLEM2_RuleClusteringByRandom_STAT",
                             "MLEM2_RuleClusteringBySameCondition_STAT",
                             "MLEM2_OnlyK_STAT"),
                           labels = c(
                             "Sim×Con",
                             "Sim",
                             "Con",
                             "Random",
                             "Match",
                             "Only K"))) %>%
  group_by(k, filename, method) %>%
  summarise(mean_num = mean(num,na.rm=T), 
            sd_num = sd(num,na.rm=T),
            mean_len = format(round(mean(len,na.rm=T),3),nsmall=3), 
            sd_len = format(round(sd(len,na.rm=T),3),nsmall=3),
            mean_support = format(round(mean(support,na.rm=T),3),nsmall=3), 
            sd_support = format(round(sd(support,na.rm=T),3),nsmall=3)) -> tmp.df

# 1指標のみ
ggplot(tmp.df, aes(x=k, y=mean_num, group=method, fill=method)) +
  geom_bar(stat="identity", width = 0.7, position = position_dodge(width = 0.9)) +
  geom_errorbar(aes(ymax = mean_num + sd_num, ymin = mean_num - sd_num, color=method),
                width = 0.7, position = position_dodge(width = 0.9)) + 
  scale_fill_grey(start = 0, end = 0.6, name="Method") +
  scale_color_grey(start = 0.6, end = 0, name="Method") +
  facet_wrap(~filename, nrow=2, ncol=3, scales = "free") +
  #scale_y_continuous(breaks = seq(0.0,1.0,by=0.10)) +
  labs(x="", y="") +
  theme_bw(base_family = "HiraKakuProN-W3") +
  theme(axis.title.x = element_text(size=15)) +
  theme(axis.text.x = element_text(size=10, angle = 45, hjust = 1)) +
  theme(axis.title.y = element_text(size=15)) +
  theme(axis.text.y = element_text(size=10))

# まとめて表示
tmp.df %>%
  ungroup() %>%
  mutate(filename = factor(.$filename, 
                         levels = c("adult_cleansing2","default_cleansing",
                                    "german_credit_categorical","hayes-roth",
                                    "nursery"),
                         labels = c("adult","default","german-credit",
                                    "hayes-roth","nursery"))) %>%
  gather(kagi1, atai1, -k, -filename, -method, -sd_num, -sd_len, -sd_support) %>%
  gather(kagi2, atai2, -k, -filename, -method, -kagi1, -atai1) %>%
  filter((kagi1 == "mean_len" & kagi2 == "sd_len") | 
         (kagi1 == "mean_num" & kagi2 == "sd_num") |
         (kagi1 == "mean_support" & kagi2 == "sd_support")) %>%
  mutate(kagi1 = factor(.$kagi1, 
                        levels = c("mean_num","mean_len","mean_support"),
                        labels = c("num","length","support"))) %>%
  mutate(kagi1 = paste0(filename," / ",kagi1)) %>%
  mutate(atai1 = as.numeric(atai1)) %>%
  mutate(atai2 = as.numeric(atai2)) %>%
  ggplot(aes(x=k, y=atai1, group=method, fill=method)) +
    geom_bar(stat="identity", width = 0.7, position = position_dodge(width = 0.9)) +
    geom_errorbar(aes(ymax = atai1 + atai2, ymin = atai1 - atai2, color=method),
                  width = 0.7, position = position_dodge(width = 0.9)) + 
    scale_fill_grey(start = 0, end = 0.6, name="Method") +
    scale_color_grey(start = 0.6, end = 0, name="Method") +
    facet_wrap(~kagi1, ncol=3, scales = "free") +
    #facet_grid(kagi1~filename, scales = "free") +
    labs(x="", y="") +
    theme_bw(base_family = "HiraKakuProN-W3") +
    theme(axis.title.x = element_text(size=15)) +
    theme(axis.text.x = element_text(size=10, angle = 30, hjust = 1)) +
    theme(axis.title.y = element_text(size=15)) +
    theme(axis.text.y = element_text(size=10))
