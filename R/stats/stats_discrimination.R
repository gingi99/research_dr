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
DIRPATH <- paste0("/mnt/data/uci/",FILENAME,"/fairness/02_alpha_preserve/")
files.all <- list.files(DIRPATH)

df.normal <- read_csv("/mnt/data/uci/german_credit_categorical/fairness/00_normal/MLEM2_LERS.csv", col_names = F)

df <- read_csv(paste0(DIRPATH,"/",files.all[3]), col_names = F)

cmd <- paste0("sed -e 's/0,25/0-25/g' ",DIRPATH,"/",files.all[4])
df <- fread(cmd, header = F)

cmd <- paste0("sed -e 's/0,25/0-25/g' ",DIRPATH,"/",files.all[2])
df <- fread(cmd, header = F)

# ===========================================
# データクレンジング
# ===========================================
df.normal %>%
  setnames(c("method","filename","iter1","iter2",
             "acc","num","num_class1","num_class2","len","support","conf","acc1","recall1","acc2","recall2"))

df %>%
  setnames(c("method","delfun","filename","class","attributes","iter1","iter2",
             "acc","num","num_class1","num_class2","len","support","conf","acc1","recall1","acc2","recall2"))

df %>%
  setnames(c("method","delfun","class","filename","attributes","iter1","iter2",
             "acc","num","num_class1","num_class2","len","support","conf","acc1","recall1","acc2","recall2"))

df %>%
  setnames(c("method","delfun","class","filename","attributes","alpha","iter1","iter2",
             "acc","num","num_class1","num_class2","len","support","conf","acc1","recall1","acc2","recall2"))

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
df.normal %>%
  dplyr::group_by(method,filename) %>%
  summarise(mean_acc = mean(acc,na.rm=T), 
            sd_acc = sd(acc,na.rm=T),
            mean_num = mean(num, na.rm=T),
            mean_num_class1 = mean(num_class1, na.rm=T),
            mean_num_class2 = mean(num_class2, na.rm=T),
            mean_len = mean(len, na.rm=T),
            mean_support = mean(support, na.rm=T),
            mean_conf = mean(conf, na.rm=T),
            mean_acc1 = mean(acc1, na.rm=T),
            mean_recall1 = mean(recall1, na.rm=T),
            mean_acc2 = mean(acc2, na.rm=T),
            mean_recall2 = mean(recall2, na.rm=T)) -> df.result

df %>%
  dplyr::group_by(method,delfun,filename,class,attributes) %>%
  summarise(mean_acc = mean(acc,na.rm=T), 
            sd_acc = sd(acc,na.rm=T),
            mean_num = mean(num, na.rm=T),
            mean_num_class1 = mean(num_class1, na.rm=T),
            mean_num_class2 = mean(num_class2, na.rm=T),
            mean_len = mean(len, na.rm=T),
            mean_support = mean(support, na.rm=T),
            mean_conf = mean(conf, na.rm=T),
            mean_acc1 = mean(acc1, na.rm=T),
            mean_recall1 = mean(recall1, na.rm=T),
            mean_acc2 = mean(acc2, na.rm=T),
            mean_recall2 = mean(recall2, na.rm=T)) -> df.result

df %>%
  dplyr::group_by(method,delfun,filename,alpha,class,attributes) %>%
  summarise(mean_acc = mean(acc,na.rm=T), 
            sd_acc = sd(acc,na.rm=T),
            mean_num = mean(num, na.rm=T),
            mean_num_class1 = mean(num_class1, na.rm=T),
            mean_num_class2 = mean(num_class2, na.rm=T),
            mean_len = mean(len, na.rm=T),
            mean_support = mean(support, na.rm=T),
            mean_conf = mean(conf, na.rm=T),
            mean_acc1 = mean(acc1, na.rm=T),
            mean_recall1 = mean(recall1, na.rm=T),
            mean_acc2 = mean(acc2, na.rm=T),
            mean_recall2 = mean(recall2, na.rm=T)) -> df.result
