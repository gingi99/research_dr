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
FILENAME <- "german_credit_categorical"
DIRPATH <- paste0("/mnt/data/uci/",FILENAME,"/fairness/01_suppression/")
files.all <- list.files(DIRPATH)
df <- read_csv(paste0(DIRPATH,"/",files.all[1]), col_names = F)

# ===========================================
# データクレンジング
# ===========================================
df %>%
  setnames(c("method","delfun","filename","attributes","iter1","iter2",
             "acc","no","len","support","conf"))

# ===========================================
# 可視化
# ===========================================

# acc の boxplot
df %>%
  ggplot(aes(x=attributes, y=acc, color=method)) +
    geom_boxplot() +
    facet_grid(method~delfun) +
    theme(legend.position = "bottom")

# acc の 平均スコア
df %>%
  dplyr::group_by(method,delfun,filename,attributes) %>%
  summarise(mean_acc = mean(acc,na.rm=T), 
            sd_acc = sd(acc,na.rm=T),
            mean_no = mean(no, na.rm=T),
            mean_len = mean(len, na.rm=T),
            mean_support = mean(support, na.rm=T),
            mean_conf = mean(conf, na.rm=T)) -> df.result

