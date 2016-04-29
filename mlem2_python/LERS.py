# coding: utf-8
# python 3.5
import pandas as pd
import pprint
import sys
from collections import defaultdict

# ---------------------------
# Option
# ---------------------------
pp = pprint.PrettyPrinter(indent=4)
pd.set_option('display.max_columns', None)


# ====================================
# Ruleの1つの条件部が対象を説明するかどうか
# ====================================
def isExplainCondition(obj, rule, attr):
    if 
    
    return(True)

# ====================================
# Ruleが対象を説明するかどうか
# ====================================
def isExplainRule(obj, rule) :
    attributes = rule.getKey()
    for attr in attributes :
        print(rule.getValue(attr))

# ====================================
# 1 対象のクラスを予測する
# ====================================
def predictClass(obj, rules) :
    print(obj)
    list_judge = [ for r in rules]
    for i, v in obj.iteritems():    
        print(i)
        print(v)
    return(len(obj))

# ====================================
# LERSによるクラス推定
# ====================================
def predictByLERS(rules, decision_table_test) :
    
    # 各行に対して予測
    decision_table_test.apply(lambda row: predictClass(row, rules), axis=1)    
        
    return(predictions)
    
    
# ========================================
# main
# ========================================
if __name__ == "__main__":

    FILENAME = 'iris'
    iter1 = 1
    iter2 = 10
    
    # rule induction
    rules = getRulesByMLEM2(FILENAME, iter1, iter2)

    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-test'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table_test = getDecisionTable(filepath)
    decision_table_test = decision_table.dropna()
    
    # predict by LERS
    predictions = predict(rules, decision_table_test)
    
    
    exit(0)
    
    predVec <- pforeach(ind.obj = 1:nrow(data.test), .multicombine=TRUE, .verbose = TRUE)({
  #for(ind.obj in 1:nrow(data.test)){
    judges <- sapply(rules, function(rule){
      idxs <- rule$idx
      values <- rule$values
      # bug。なぜかvalues が list()なのがあるのでその回避
      if(length(values) == 0){
        return(FALSE)
      }
      judge <- TRUE
      for(ind.idx in 1:length(idxs)){
        # num 基本条件が1つの条件でルールができている場合
        if(is.numeric(values[[ind.idx]])){
          if(data.test[ind.obj,][idxs[ind.idx]] > values[[ind.idx]][1]&
             data.test[ind.obj,][idxs[ind.idx]] < values[[ind.idx]][2]){
            judge <- TRUE
          }else{
            return(FALSE)
          }
        # num 基本条件が区間でルールができている場合
        # まだ未実装…
        # nom
        }else{
          # 基本条件が複数の条件でルールができている場合
          if(str_detect(values[[ind.idx]][1], "^\\[.*\\]$")){
            v <- values[[ind.idx]][1]
            v <- str_replace_all(v, "^\\[", "")
            v <- str_replace_all(v, "\\]$", "")
            v <- str_split(v, ",")[[1]]
            if(data.test[ind.obj,][idxs[ind.idx]] %in% v){
              judge <- TRUE
            }else{
              return(FALSE)
            }
          # 基本条件が1つの条件でルールができている場合
          }else{
            if(data.test[ind.obj,][idxs[ind.idx]] == values[[ind.idx]][1]){
              judge <- TRUE
            }else{
              return(FALSE)
            }
          }
        }
      }
      return(TRUE)
    })

    # objにマッチするrule が 1つでもある
    estimatedClass <- NULL
    if(any(judges)){
      # マッチしたルールが1つだけのとき
      if(length(which(judges)) == 1){
        estimatedClass <- list.select(rules[which(judges)], consequent) %>% list.mapv(consequent)
      # マッチしたルールが2つ以上で同じクラスを推定しているとき
      }else if(length(which(judges)) > 1 & length(unique(list.select(rules[which(judges)], consequent))) == 1){
        estimatedClass <- unique(list.select(rules[which(judges)], consequent) %>% list.mapv(consequent))
      # マッチしたルールが2つ以上で別のクラスを推定しているとき
      }else if(length(which(judges)) > 1 & length(unique(list.select(rules[which(judges)], consequent))) > 1){
        support_D <- -1
        for(rule in rules[which(judges)]){
          strength <- length(rule$support)
          specificity <- length(rule$values)
          if((strength * specificity) > support_D){
            estimatedClass <- rule$consequent
            support_D <- strength * specificity
          }
        }
      }else{
        stop("LERS doesn't estimate the decision class")
      }
    }
    # rule が objに1つもマッチしない場合は部分一致ルールによる推定
    else{
      p_support <- -1
      for(rule in rules){
        strength <- length(rule$support)
        specificity <- length(rule$values)
        matching_factor <- 0
        idxs <- rule$idx
        values <- rule$values
        # bug。なぜかvalues が list()なのがあるのでその回避
        if(length(values) == 0){
          next
        }
        for(ind.idx in 1:length(idxs)){
          # num
          if(is.numeric(values[[ind.idx]])){
            if(data.test[ind.obj,][idxs[ind.idx]] > values[[ind.idx]][1]&
              data.test[ind.obj,][idxs[ind.idx]] < values[[ind.idx]][2]){
              matching_factor <- matching_factor + 1
            }
          # nom
          }else{
            # 基本条件が複数の条件でルールができている場合
            if(str_detect(values[[ind.idx]][1], "^\\[.*\\]$")){
              v <- values[[ind.idx]][1]
              v <- str_replace_all(v, "^\\[", "")
              v <- str_replace_all(v, "\\]$", "")
              v <- str_split(v, ",")[[1]]
              if(data.test[ind.obj,][idxs[ind.idx]] %in% v){
                matching_factor <- matching_factor + 1
              }
            # 基本条件が1つの条件でルールができている場合
            }else{
              if(data.test[ind.obj,][idxs[ind.idx]] == values[[ind.idx]][1]){
                matching_factor <- matching_factor + 1
              }
            }
          }
        }
        matching_factor <- matching_factor / length(idxs)
        if((matching_factor * strength * specificity) > p_support){
          estimatedClass <- rule$consequent
          p_support <- matching_factor * strength * specificity
        }
      }
    }
  #  predVec <- append(predVec, estimatedClass)
  #}
    return(estimatedClass)
  })
  return(predVec)
