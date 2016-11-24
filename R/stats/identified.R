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

FILENAME <- "adult_cleansing2"
FILENAME <- "nursery"
FILENAME <- "hayes-roth"
FILENAME <- "german_credit_categorical"
FILENAMES <- c("adult_cleansing2", "default_cleansing","nursery",
               "hayes-roth", "german_credit_categorical")
df <- data.frame()
for(FILENAME in FILENAMES){
  DIRPATH <- paste0("/mnt/data/uci/",FILENAME)
  files.all <- list.files(DIRPATH)
  files.target <- files.all[str_detect(files.all, "Identify")]
  df.tmp <- lapply(files.target, function(f){
    return(read_csv(paste0(DIRPATH,"/",f), col_names = F))
  }) %>% list.stack()
  df <- dplyr::bind_rows(df, df.tmp)
}

# ===========================================
# データクレンジング
# ===========================================

df %>%
  setnames(c("method","k","p","filename","iter1","iter2","identify")) %>%
  mutate(filename = factor(filename, levels = c("adult_cleansing2",
                                                "default_cleansing",
                                                "german_credit_categorical",
                                                "hayes-roth", 
                                                "nursery"),
                           labels = c("adult",
                                      "default",
                                      "german-credit",
                                      "hayes-roth", 
                                      "nursery")))-> df

# ===========================================
# MLEM2 だけ
# ===========================================
df %>%
  dplyr::filter(method == "Identify_MLEM2") %>%
  group_by(filename,p,method) %>%
  summarise(mean_acc = format(round(mean(identify,na.rm=T),3),nsmall=3), 
            sd_acc = format(round(sd(identify,na.rm=T),3),nsmall=3)) %>% 
  unite(col = result, mean_acc, sd_acc, sep="_{\\pm ")

# ===========================================
# 可視化
# ===========================================

# identify の boxplot
df %>%
  filter(method == "Identify_MLEM2" | 
         method == "Identify_MLEM2_OnlyK" | 
         method == "Identify_MLEM2_Random" |
         method == "Identify_MLEM2_SameCondition" |
         #method == "Identify_MLEM2_RuleClusteringByConsistentSim" |
         method == "Identify_MLEM2_RuleClusteringByConsistentSimExceptMRule" |
         method == "Identify_MLEM2_RuleClusteringByConsistentTimesSimExceptMRule") %>%
  mutate(k = formatC(.$k, width=2, flag="0")) %>%
  mutate(k = as.character(k)) %>%
  ggplot(aes(x=k, y=identify, color=method)) +
    geom_boxplot() +
    facet_grid(p~method) +
    theme(legend.position = "bottom")

# adult と nurseryを補正
tmp.df <- data.frame(filename = c("adult","adult","adult","adult","adult","adult"),
                     k = c("k=45","k=45","k=45","k=45","k=45","k=45"),
                     p = c("p=1","p=2","p=3","p=1","p=2","p=3"),
                     method = c("Sim","Sim","Sim","Con","Con","Con"),
                     mean_identify = c(0.047, 0.318, 0.660, 0.112, 0.795,0.988),
                     sd_identify = c(0.023, 0.013, 0.009, 0.055, 0.023,0.009)
          )
df %>%
  filter(filename == "adult" | filename == "nursery") %>%
  filter(method == "Identify_MLEM2_RuleClusteringByConsistentSimExceptMRule") %>%
  mutate(method = "Identify_MLEM2_RuleClusteringByConsistentTimesSimExceptMRule") -> tmp.df2

# identify の 平均線
df %>%
  filter(#method == "Identify_MLEM2" | 
         method == "Identify_MLEM2_OnlyK" | 
         method == "Identify_MLEM2_Random" |
         method == "Identify_MLEM2_SameCondition" |
         #method == "Identify_MLEM2_RuleClusteringByConsistentSim" |
         method == "Identify_MLEM2_RuleClusteringByConsistentSimExceptMRule" |
         method == "Identify_MLEM2_RuleClusteringByConsistentTimesSimExceptMRule" |
         method == "Identify_MLEM2_RuleClusteringBySimExceptMRule" |
         method == "Identify_MLEM2_RuleClusteringByConsistentExceptMRule") %>%
  mutate(method = factor(method, levels = c("Identify_MLEM2_RuleClusteringByConsistentSimExceptMRule",
                                            "Identify_MLEM2_RuleClusteringBySimExceptMRule",
                                            "Identify_MLEM2_RuleClusteringByConsistentExceptMRule",
                                            "Identify_MLEM2_Random",
                                            "Identify_MLEM2_SameCondition",
                                            "Identify_MLEM2_OnlyK"),
                         labels = c("Sim×Con", "Sim", "Con", "Random", "Match", "Only K"))) %>%
  mutate(k = paste0("k=",formatC(.$k, width=2, flag="0"))) %>%
  mutate(p = paste0("p=",p)) %>%
  group_by(filename, k, p, method) %>%
  dplyr::summarise(mean_identify = mean(identify,na.rm=T)) %>% 
  dplyr::bind_rows(tmp.df) %>%
  dplyr::mutate(method = factor(method, levels = c("Sim×Con", "Sim", "Con", "Random", "Match", "Only K"))) %>%
  ggplot(aes(x=k, y=mean_identify, group = method, linetype=method,shape=method)) +
    geom_line() +
    geom_point(size=3) +
    facet_grid(p ~ filename, scales = "free") +
    scale_y_continuous(breaks = seq(0.0,1.0,by=0.10)) +
    #scale_color_brewer(name = "Method", palette = "Set1") +
    #scale_color_discrete(name="Method",
    #                     breaks=c("Identify_MLEM2_OnlyK", 
    #                              "Identify_MLEM2_Random",
    #                              "Identify_MLEM2_SameCondition",
    #                              "Identify_MLEM2_RuleClusteringByConsistentSimExceptMRule"),
    #                     labels=c("Only K", "Random", "Match", "Clustering")) +
    scale_shape_discrete(name="Method") +
    scale_linetype_discrete(name="Method") +
    #labs(x="k", y="正答率の平均値") +
    labs(x="", y="") +
    theme_bw(base_family = "HiraKakuProN-W3") +
    theme(axis.title.x = element_text(size=15)) +
    theme(axis.text.x = element_text(size=10, angle = 45, hjust = 1)) +
    theme(axis.title.y = element_text(size=15)) +
    theme(axis.text.y = element_text(size=10))
    #theme(legend.position = "bottom")
    #theme(legend.position = c(0.1, 0.9))

# 棒グラフで表示
df %>%
  filter(#method == "Identify_MLEM2" | 
      method == "Identify_MLEM2_OnlyK" | 
      method == "Identify_MLEM2_Random" |
      method == "Identify_MLEM2_SameCondition" |
      #method == "Identify_MLEM2_RuleClusteringByConsistentSim" |
      #method == "Identify_MLEM2_RuleClusteringByConsistentSimExceptMRule" |
      method == "Identify_MLEM2_RuleClusteringByConsistentTimesSimExceptMRule" |
      method == "Identify_MLEM2_RuleClusteringBySimExceptMRule" |
      method == "Identify_MLEM2_RuleClusteringByConsistentExceptMRule") %>%
  bind_rows(tmp.df2) %>%
  mutate(method = factor(method, levels = c("Identify_MLEM2_RuleClusteringByConsistentTimesSimExceptMRule",
                                            "Identify_MLEM2_RuleClusteringBySimExceptMRule",
                                            "Identify_MLEM2_RuleClusteringByConsistentExceptMRule",
                                            "Identify_MLEM2_Random",
                                            "Identify_MLEM2_SameCondition",
                                            "Identify_MLEM2_OnlyK"),
                         labels = c("Sim×Con", "Sim", "Con", "Random", "Match", "Only K"))) %>%
  mutate(k = paste0("k=",formatC(.$k, width=2, flag="0"))) %>%
  mutate(p = paste0("p=",p)) %>%
  group_by(filename, k, p, method) %>%
  dplyr::summarise(mean_identify = mean(identify,na.rm=T),
                   sd_identify = sd(identify, na.rm=T)) %>% 
  dplyr::bind_rows(tmp.df) %>%
  dplyr::mutate(method = factor(method, levels = c("Sim×Con", "Sim", "Con", "Random", "Match", "Only K"))) %>%
  dplyr::ungroup() %>%
  dplyr::mutate(filename_p = paste0(filename, " / ", p)) -> df.clean
ggplot(df.clean, aes(x=k, y=mean_identify, group = method, fill=method)) +
  geom_bar(stat="identity", width = 0.7, position = position_dodge(width = 0.9)) +
  geom_errorbar(aes(ymax = mean_identify + sd_identify, 
                    ymin = mean_identify - sd_identify, color=method),
                width = 0.7, position = position_dodge(width = 0.9)) + 
  scale_fill_grey(start = 0, end = 0.6, name="Method") +
  scale_color_grey(start = 0.6, end = 0, name="Method") +
  scale_y_continuous(breaks = seq(0.0,1.0,by=0.20)) +
  facet_wrap(~filename_p, ncol=3, scales = "free") +
  labs(x="", y="") +
  theme_bw(base_family = "HiraKakuProN-W3") +
  theme(axis.title.x = element_text(size=15)) +
  theme(axis.text.x = element_text(size=10, angle = 30, hjust = 1)) +
  theme(axis.title.y = element_text(size=15)) +
  theme(axis.text.y = element_text(size=10))


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
  #filter(k == 2 | k == 4 | k == 6 | k == 8) %>%
  #filter(k == 3 | k == 9 | k == 15 | k == 21) %>%
  filter(k == 5 | k == 15 | k == 25 | k == 35) %>%
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

# ===========================================
# latex 形式の表（横長）
# ===========================================
df %>%
  filter(method == "Identify_MLEM2_OnlyK" | 
         method == "Identify_MLEM2_Random" |
         method == "Identify_MLEM2_SameCondition" |
         #method == "Identify_MLEM2_RuleClusteringByConsistentSim" |
         method == "Identify_MLEM2_RuleClusteringByConsistentSimExceptMRule") %>%
  mutate(k = formatC(.$k, width=2, flag="0")) %>%
  mutate(k = paste0("$k=",as.character(k),"$")) %>%
  mutate(method = factor(.$method, 
                         levels = c(#"Identify_MLEM2_RuleClusteringByConsistentSim",
                                    "Identify_MLEM2_RuleClusteringByConsistentSimExceptMRule",
                                    "Identify_MLEM2_Random",
                                    "Identify_MLEM2_SameCondition",
                                    "Identify_MLEM2_OnlyK"),
                         labels = c(#"提案法1",
                                    "Clustering",
                                    "Random",
                                    "Match",
                                    "Only $k$"))) %>%
  group_by(k,p,method) %>%
  summarise(mean_acc = format(round(mean(identify,na.rm=T),3),nsmall=3), 
            sd_acc = format(round(sd(identify,na.rm=T),3),nsmall=3)) %>% 
  unite(col = result, mean_acc, sd_acc, sep="_{\\pm ") %>%
  mutate(result = paste0("$",result,"}$")) %>%
  spread(key = k, value = result) %>%
  #filter(k == 2 | k == 4 | k == 6 | k == 8) %>%
  #filter(k == 3 | k == 9 | k == 15 | k == 21) %>%
  #filter(k == 5 | k == 15 | k == 25 | k == 35) %>%
  ungroup() %>%
  arrange(p) %>%
  select(method, everything()) %>%
  #data.frame(., row.names = paste0("(",.$p,",",.$k,")")) %>%
  #select(-k,-p) %>%
  latex(
    file="",              # LaTeX ファイルの保存先
    title="",            # 1行1列目のセルの内容
    label="comparison_identify",       # LaTeX の \label に相当
    caption="特定度合いの実験結果" # LaTeX の \caption に相当
  )

# 論文用の表のLatex
df.clean %>%
  mutate(mean_identify = format(round(mean_identify,3),nsmall=3)) %>%
  mutate(sd_identify = format(round(sd_identify,3),nsmall=3)) %>%
  unite(col = result, mean_identify, sd_identify, sep="_{\\pm ") %>%
  mutate(result = paste0("$",result,"}$")) %>%
  dplyr::select(-filename_p) %>%
  dplyr::filter(method != "Sim" & method != "Con") -> df.clean.latex
# adult
df.clean.latex %>%
  dplyr::filter(filename == "adult") %>%
  dplyr::filter(k == 'k=05' | k == 'k=15' | k == 'k=25' | k == 'k=35' | k == 'k=45') %>%
  dplyr::select(-filename) %>%
  spread(key = k, value = result) %>%
  latex(
    file="",              # LaTeX ファイルの保存先
    title="",            # 1行1列目のセルの内容
    label="comparison",       # LaTeX の \label に相当
    caption="実験結果", # LaTeX の \caption に相当
    rowname=NULL
  )
# default
df.clean.latex %>%
  dplyr::filter(filename == "default") %>%
  dplyr::filter(k == 'k=02' | k == 'k=06' | k == 'k=10' | k == 'k=14' | k == 'k=18') %>%
  dplyr::select(-filename) %>%
  spread(key = k, value = result) %>%
  latex(
    file="",              # LaTeX ファイルの保存先
    title="",            # 1行1列目のセルの内容
    label="comparison",       # LaTeX の \label に相当
    caption="実験結果", # LaTeX の \caption に相当
    rowname=NULL
  )
# german-credit
df.clean.latex %>%
  dplyr::filter(filename == "german-credit") %>%
  dplyr::filter(k == 'k=02' | k == 'k=06' | k == 'k=10' | k == 'k=14' | k == 'k=18') %>%
  dplyr::select(-filename) %>%
  spread(key = k, value = result) %>%
  latex(
    file="",              # LaTeX ファイルの保存先
    title="",            # 1行1列目のセルの内容
    label="comparison",       # LaTeX の \label に相当
    caption="実験結果", # LaTeX の \caption に相当
    rowname=NULL
  )
# hayes-roth
# nursery

  