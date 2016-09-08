# 実験用にa1,a2,...D1,D2,D3のようにデータを作る

# ===========================================
# ライブラリ読み込み
# ===========================================
library(dplyr)
library(readr)
library(rlist)
library(data.table)
library(stringr)
library(tidyr)

# ===========================================
# 読み取り用のデータ準備
# ===========================================
FILENAME <- "adult_cleansing2"
FILENAME <- "hayes-roth"
FILENAME <- "nursery"
FILENAME <- "german_credit_categorical"
DIRPATH <- paste0("/mnt/data/uci/",FILENAME)
files.all <- list.files(DIRPATH)
files.train <- files.all[str_detect(files.all, "train[0-9]")]
files.test <- files.all[str_detect(files.all, "test")]
files.target <- c(files.train, files.test)

# ===========================================
# データ作成
# ===========================================
# 各ファイルごとにdfとしてロードして処理
for(f in files.target){
  # 読み込み
  df <- read_tsv(paste0(DIRPATH,"/",f), col_names = T)
  df <- na.omit(df)
  
  # カラム名を定義
  colnames_new <- c(letters[1:ncol(df)-1],"D")
  setnames(df, colnames_new)
  
  # 属性値を変更する
  df.alpha <- df
  for(i in seq(1,ncol(df))){
    new_vals <- paste0(colnames_new[i], seq(1,length(unique(df[[i]]))))
    df.alpha[[i]] <- factor(df[[i]], levels = sort(unique(df[[i]])), labels = new_vals)
  }
  
  # 保存
  f_new <- stringr::str_replace(string = f, pattern = ".tsv", replacement = ".txt")
  write.table(df.alpha, 
              paste0("/mnt/data/uci/",FILENAME,"/alpha/",f_new), 
              sep = " ", row.names=F, quote=F, col.names = F)
}
