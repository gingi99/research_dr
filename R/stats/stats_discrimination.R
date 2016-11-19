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
files.all <- list.files(DIRPATH)

# MLEM2
df.normal <- read_csv("/mnt/data/uci/german_credit_categorical/fairness/00_normal/MLEM2_LERS.csv", col_names = F)

# 01_suppression Attr
DIRPATH <- paste0("/mnt/data/uci/",FILENAME,"/fairness/01_suppression/")
df.suppression.attr <- read_csv(paste0(DIRPATH,"/MLEM2_delAttrRule_LERS.csv"), col_names = F)

# 01_suppresion E
DIRPATH <- paste0("/mnt/data/uci/",FILENAME,"/fairness/01_suppression/")
cmd <- paste0("sed -e 's/0,25/0-25/g' ",DIRPATH,"/MLEM2_delERule_LERS.csv")
df.suppression.e <- fread(cmd, header = F)

# 02_alpha
DIRPATH <- paste0("/mnt/data/uci/",FILENAME,"/fairness/02_alpha_preserve/")
cmd <- paste0("sed -e 's/0,25/0-25/g' ",DIRPATH,"/MLEM2_delEAlphaRule_LERS.csv")
df.alpha <- fread(cmd, header = F)

# ===========================================
# データクレンジング
# ===========================================
df.normal %>%
  setnames(c("method","filename","iter1","iter2",
             "acc","num","num_class1","num_class2","len","support","conf","acc1","recall1","acc2","recall2"))

df.suppression.attr %>%
  setnames(c("method","delfun","filename","class","attributes","iter1","iter2",
             "acc","num","num_class1","num_class2","len","support","conf","acc1","recall1","acc2","recall2"))

df.suppression.e %>%
  setnames(c("method","delfun","class","filename","attributes","iter1","iter2",
             "acc","num","num_class1","num_class2","len","support","conf","acc1","recall1","acc2","recall2"))

df.alpha %>%
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

df.suppression.attr %>%
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

df.suppression.e %>%
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

df.alpha %>%
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

## Latex 形式の表

# ===========================================
# latex 形式の表
# Tex表だと"_"をなくす必要があるので注意
# ===========================================
df.suppression.attr %>%
  #dplyr::filter(class == 1) %>%
  mutate(attributes = stringr::str_replace_all(string = .$attributes, 
                                       pattern = "_", replacement = "")) %>%
  mutate(delfun = stringr::str_replace(string = .$delfun, 
                                       pattern = "getRules", replacement = "")) %>%
  dplyr::group_by(delfun,class,attributes) %>%
  dplyr::summarise(mean_acc = format(round(mean(acc,na.rm=T),3),nsmall=3), 
            sd_acc = format(round(sd(acc,na.rm=T),3),nsmall=3),
            num = mean(num, na.rm=T),
            num1 = mean(num_class1, na.rm=T),
            num2 = mean(num_class2, na.rm=T),
            len = format(round(mean(len, na.rm=T),3),nsmall=3),
            support = format(round(mean(support, na.rm=T),3),nsmall=3),
            conf = format(round(mean(conf, na.rm=T),3),nsmall=3),
            acc1 = format(round(mean(acc1, na.rm=T),3),nsmall=3),
            recall1 = format(round(mean(recall1, na.rm=T),3),nsmall=3),
            acc2 = format(round(mean(acc2, na.rm=T),3),nsmall=3),
            recall2 = format(round(mean(recall2, na.rm=T),3),nsmall=3)) %>%
  unite(col = result, mean_acc, sd_acc, sep="_{\\pm ") %>%
  mutate(result = paste0("$",result,"}$")) %>%
  latex(
    file="",              # LaTeX ファイルの保存先
    title="",            # 1行1列目のセルの内容
    label="comparison",       # LaTeX の \label に相当
    caption="実験結果", # LaTeX の \caption に相当
    rowname=NULL
  )

df.suppression.e %>%
  #dplyr::filter(class == 1) %>%
  mutate(attributes = stringr::str_replace_all(string = .$attributes, 
                                               pattern = "_", replacement = "")) %>%
  mutate(delfun = stringr::str_replace(string = .$delfun, 
                                       pattern = "getRules", replacement = "")) %>%
  dplyr::group_by(delfun,class,attributes) %>%
  dplyr::summarise(mean_acc = format(round(mean(acc,na.rm=T),3),nsmall=3), 
                   sd_acc = format(round(sd(acc,na.rm=T),3),nsmall=3),
                   num = mean(num, na.rm=T),
                   num1 = mean(num_class1, na.rm=T),
                   num2 = mean(num_class2, na.rm=T),
                   len = format(round(mean(len, na.rm=T),3),nsmall=3),
                   support = format(round(mean(support, na.rm=T),3),nsmall=3),
                   conf = format(round(mean(conf, na.rm=T),3),nsmall=3),
                   acc1 = format(round(mean(acc1, na.rm=T),3),nsmall=3),
                   recall1 = format(round(mean(recall1, na.rm=T),3),nsmall=3),
                   acc2 = format(round(mean(acc2, na.rm=T),3),nsmall=3),
                   recall2 = format(round(mean(recall2, na.rm=T),3),nsmall=3)) %>%
  unite(col = result, mean_acc, sd_acc, sep="_{\\pm ") %>%
  mutate(result = paste0("$",result,"}$")) %>%
  latex(
    file="",              # LaTeX ファイルの保存先
    title="",            # 1行1列目のセルの内容
    label="comparison",       # LaTeX の \label に相当
    caption="実験結果", # LaTeX の \caption に相当
    rowname=NULL
  )


