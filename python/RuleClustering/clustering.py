# coding: utf-8
# python 3.5
from sklearn.metrics import accuracy_score
from itertools import product
import numpy as np
import sys
import os
import random
sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/../MLEM2')
#sys.path.append('/Users/ooki/git/research_dr/python/MLEM2')
import importlib
import mlem2
importlib.reload(mlem2)  
import LERS

# =====================================
# list同士のintersectを返す
# =====================================
def intersect(list_a, list_b) :
    return(list(set(list_a) & set(list_b)))

# =====================================
# list 同士のunionを返す
# =====================================
def union(list_a, list_b) :
    return(list(set(list_a) | set(list_b)))

# =====================================
# list 同士のdiffを返す
# =====================================
def setdiff(list_a, list_b) :
    return(list(set(list_a) - set(list_b)))

# =====================================
# list a が b に包含されているかを判定する
# =====================================
def isSuperList(list_a, list_b) :
    return(set(list_b).issuperset(set(list_a)))

# =====================================
# list a が b に または、b が a に包含されているかを判定する
# =====================================
def isEitherSuperList(list_a, list_b) :
    return(set(list_b).issuperset(set(list_a)) or set(list_a).issuperset(set(list_b)))

# =====================================
# Rule 間の類似度を返す関数
# =====================================
def getSimilarity(rule1, rule2, colnames, list_judgeNominal) :
    similarity = 0
    for col in colnames :
        # 両要素ともNAなら、0.5
        if (not rule1.getValue(col)) and (not rule2.getValue(col)) :       
            similarity += 0.5 
            #print("0.5")
            continue
        # どちらかがNAなら、0
        if (not rule1.getValue(col)) or (not rule2.getValue(col)) :
            similarity += 0
            #print("0")
            continue
        # 名義属性なら
        if list_judgeNominal[col] :
            # 包含関係があるなら
            if isEitherSuperList(rule1.getValue(col), rule2.getValue(col)):
                similarity += 1.0
                #print("1")
            else :
                similarity += 1/3
                #print("1/3")
        # 数値属性なら
        else :
            print("suuchi ha mada")
            #v <- 1.0 - (x[[i]] - y[[i]])/(3.0 * sd)
            #if(v < 0.0){
                #v <- 0
            #}
            similarity += 0
    similarity /= len(colnames)
    return(similarity)

# =====================================
# ななめが発生するかを返す
# =====================================
def isNaname(rule1, rule2, c_rule) :
    # rule 1 チェック
    judge = []
    for key in rule1.getKey() :        
        if c_rule.getValue(key) == None : 
            pass
        else : 
            judge.append(isSuperList(c_rule.getValue(key), rule1.getValue(key)))
    
    if all(judge) : return(False)
    # rule 2 チェック
    judge = []
    for key in rule2.getKey() :        
        if c_rule.getValue(key) == None : 
            pass
        else : 
            judge.append(isSuperList(c_rule.getValue(key), rule2.getValue(key)))
    
    if all(judge) : return(False)
    else : return(True)

# =====================================
# 決定ルールのマージのための矛盾識別行列の要素を返す
# =====================================
def getElementDiscernibieRule(rule1, rule2):
    merge_rule = mergeRule(rule1,rule2)
    
    # 各条件属性から1つずつ選んた斜め判定ルール集合を作る
    list_pattern = [merge_rule.getValue(key,onecase=False) for key in merge_rule.getKey()]
    list_setvalues = list(product(*list_pattern))
    candidate_rules = []    
    for setvalue in list_setvalues:
        rule = mlem2.Rule2()
        for i,v in enumerate(setvalue):
            rule.setValue(merge_rule.getKey()[i], v)
            #print(i,v)
        candidate_rules.append(rule)    

    # 斜めが発生している個数を数えて返す
    list_judge = [isNaname(rule1, rule2, c_rule) for c_rule in candidate_rules]
    return(sum(list_judge))

# =====================================
# Random にルールを選ぶ関数
# =====================================
def choiceRandomRule(list_rules) :
    return(random.choice(list_rules))

# =====================================
# Rule を構成する条件属性名が同じ数
# =====================================
def getCountSameCondition(rule1, rule2) :
    keys_rule1 = rule1.getKey()
    keys_rule2 = rule2.getKey()
    return(len(set(keys_rule1) & set(keys_rule2)))

# =====================================
# 2つのRuleを併合する関数：数値属性のときのsetValueはまだ実装できていない
# =====================================
def mergeRule(rule1, rule2):
    
    merge_rule = mlem2.Rule2()    
    
    # 2つのルールに両方持つ条件属性集合を抽出
    common_keys = intersect(rule1.getKey(), rule2.getKey())
    
    # 共通の条件属性がないなら
    if not common_keys :
        union_keys = union(rule1.getKey(), rule2.getKey())
        for key in union_keys :
            if rule1.getValue(key) != None : merge_rule.setValue(key, rule1.getValue(key))
            if rule2.getValue(key) != None : merge_rule.setValue(key, rule2.getValue(key))
    
    # 1つ以上共通の条件属性があるなら
    else :
        for key in common_keys :
            if rule1.getValue(key) != None : merge_rule.setValue(key, rule1.getValue(key))
            if rule2.getValue(key) != None : merge_rule.setValue(key, rule2.getValue(key))
    
    # consequent 
    merge_rule.setConsequent(rule1.getConsequent())
    merge_rule.setConsequent(rule2.getConsequent())
    
    # supportの計算
    merge_rule.setSupport(union(rule1.getSupport(), rule2.getSupport()))
      
    return(merge_rule)    

# =====================================
# Main 関数 : ななめが発生しないように + similarity
# =====================================
def getRuleClusteringByConsistentSimilarity(rules, colnames, list_judgeNominal, k=3) :
    
    rules_new = list()    
    
    # 結論部別
    for cls in mlem2.getEstimatedClass(rules) :
        target_rules = [r for r in rules if r.getConsequent() == cls]

        # ルール群のサポート値の最小値がk以下のルールがある内は繰り返す
        min_support = mlem2.getMinSupport(target_rules) 
        while min_support < k :

            # target_rules が 1つなら
            if len(target_rules) == 1 :
                print("shori")

            # merge対象ルールを見つける
            merged_rules = [r for r in target_rules if len(r.getSupport()) == min_support]
            merged_rule = merged_rules[0]
            target_rules.remove(merged_rule)

            # 斜めが発生しないルールを探す
            list_inconsistency = [getElementDiscernibieRule(r, merged_rule) for r in target_rules]

            # もっとも斜めが発生しないルールに絞る
            max_inconsistency = np.max(list_inconsistency)
            max_rules = [target_rules[i] for i,c in enumerate(list_inconsistency) if c == max_inconsistency]
            
            # 一意でなければ、類似度で判断
            if len(max_rules) > 1 :

                # merged_rule との類似度を求める
                list_similarities = [getSimilarity(merged_rule, r, colnames, list_judgeNominal) for r in max_rules] 
                #combi_rule = list(combinations(tuple(target_rules),2))
                #list_similarities = [getSimilarity(combi[0], combi[1], colnames, list_judgeNominal) for combi in combi_rule]
            
                # 最も類似度が大きいルールを見つける
                max_similarity = np.max(list_similarities)
                max_rules = [max_rules[i] for i,s in enumerate(list_similarities) if s == max_similarity]
                #print("First : " + str(len(max_rules)))
            
            # 一意でなければ、条件部を構成する属性数で判断
            if len(max_rules) > 1 :
                list_count_same_conditions = [getCountSameCondition(merged_rule, r) for r in max_rules]
                max_count = np.max(list_count_same_conditions)
                max_rules = [max_rules[i] for i,c in enumerate(list_count_same_conditions) if c == max_count]
                #print("Second : " + str(len(max_rules)))

            # 一意でなければ、supportの小ささで判断           
            if len(max_rules) > 1 :
                list_supports = [len(r.getSupport()) for r in max_rules]
                min_support = np.min(list_supports)
                max_rules = [max_rules[i] for i,s in enumerate(list_supports) if s == min_support]
                #print("Third : " + str(len(max_rules)))
            
            # 先頭のルールでmerge 
            merge_rule = mergeRule(merged_rule, max_rules[0])
            target_rules.remove(max_rules[0])
            
            # 新しいルールを追加
            target_rules.append(merge_rule)
            
            # min_support 更新
            min_support = mlem2.getMinSupport(target_rules)
            print(min_support)
            
        rules_new.extend(target_rules)
        
    return(rules_new)

# =====================================
# Main 関数 : Similarity
# =====================================
def getRuleClusteringBySimilarity(rules, colnames, list_judgeNominal, k=3) :
    
    rules_new = list()    
    
    # 結論部別
    for cls in mlem2.getEstimatedClass(rules) :
        target_rules = [r for r in rules if r.getConsequent() == cls]

        # ルール群のサポート値の最小値がk以下のルールがある内は繰り返す
        min_support = mlem2.getMinSupport(target_rules) 
        while min_support < k :

            # target_rules が 1つなら
            if len(target_rules) == 1 :
                print("shori")

            # merge対象ルールを見つける
            merged_rules = [r for r in target_rules if len(r.getSupport()) == min_support]
            merged_rule = merged_rules[0]
            target_rules.remove(merged_rule)

            # merged_rule との類似度を求める
            list_similarities = [getSimilarity(merged_rule, r, colnames, list_judgeNominal) for r in target_rules] 
            #combi_rule = list(combinations(tuple(target_rules),2))
            #list_similarities = [getSimilarity(combi[0], combi[1], colnames, list_judgeNominal) for combi in combi_rule]
            
            # 最も類似度が大きいルールを見つける
            max_similarity = np.max(list_similarities)
            max_rules = [target_rules[i] for i,s in enumerate(list_similarities) if s == max_similarity]
            #print("First : " + str(len(max_rules)))
            
            # 一意でなければ、条件部を構成する属性数で判断
            if len(max_rules) > 1 :
                list_count_same_conditions = [getCountSameCondition(merged_rule, r) for r in max_rules]
                max_count = np.max(list_count_same_conditions)
                max_rules = [max_rules[i] for i,c in enumerate(list_count_same_conditions) if c == max_count]
                #print("Second : " + str(len(max_rules)))

            # 一意でなければ、supportの小ささで判断           
            if len(max_rules) > 1 :
                list_supports = [len(r.getSupport()) for r in max_rules]
                min_support = np.min(list_supports)
                max_rules = [max_rules[i] for i,s in enumerate(list_supports) if s == min_support]
                #print("Third : " + str(len(max_rules)))
            
            # 先頭のルールでmerge 
            merge_rule = mergeRule(merged_rule, max_rules[0])
            target_rules.remove(max_rules[0])
            
            # 新しいルールを追加
            target_rules.append(merge_rule)
            
            # min_support 更新
            min_support = mlem2.getMinSupport(target_rules)
            print(min_support)
            
        rules_new.extend(target_rules)
        
    return(rules_new)
        
# ========================================
# 比較：ランダム結合でクラスタリング
# ========================================
def getRuleClusteringByRandom(rules, k=3) :
    
    rules_new = list()    
    
    # 結論部別
    for cls in mlem2.getEstimatedClass(rules) :
        target_rules = [r for r in rules if r.getConsequent() == cls]

        # ルール群のサポート値の最小値がk以下のルールがある内は繰り返す
        min_support = mlem2.getMinSupport(target_rules) 
        while min_support < k :

            # target_rules が 1つなら
            if len(target_rules) == 1 :
                print("shori")

            # merge対象ルールを見つける
            merged_rules = [r for r in target_rules if len(r.getSupport()) == min_support]
            merged_rule = merged_rules[0]
            target_rules.remove(merged_rule)

            # ランダムにもう一つのルールを求める
            random_rule = choiceRandomRule(target_rules)
            
            # 先頭のルールでmerge 
            merge_rule = mergeRule(merged_rule, random_rule)
            target_rules.remove(random_rule)
            
            # 新しいルールを追加
            target_rules.append(merge_rule)
            
            # min_support 更新
            min_support = mlem2.getMinSupport(target_rules)
            print(min_support)
            
        rules_new.extend(target_rules)
        
    return(rules_new)

# ========================================
# 比較：マッチした属性の数だけでクラスタリング
# ========================================
def getRuleClusteringBySameCondition(rules, k=3) :
    
    rules_new = list()    
    
    # 結論部別
    for cls in mlem2.getEstimatedClass(rules) :
        target_rules = [r for r in rules if r.getConsequent() == cls]

        # ルール群のサポート値の最小値がk以下のルールがある内は繰り返す
        min_support = mlem2.getMinSupport(target_rules) 
        while min_support < k :

            # target_rules が 1つなら
            if len(target_rules) == 1 :
                print("shori")

            # merge対象ルールを見つける
            merged_rules = [r for r in target_rules if len(r.getSupport()) == min_support]
            merged_rule = merged_rules[0]
            target_rules.remove(merged_rule)

            # 同じ条件属性の数でマージするルールを決定
            list_count_same_conditions = [getCountSameCondition(merged_rule, r) for r in target_rules]
            max_count = np.max(list_count_same_conditions)
            max_rules = [target_rules[i] for i,c in enumerate(list_count_same_conditions) if c == max_count]
            
            # 先頭のルールでmerge 
            merge_rule = mergeRule(merged_rule, max_rules[0])
            target_rules.remove(max_rules[0])
            
            # 新しいルールを追加
            target_rules.append(merge_rule)
            
            # min_support 更新
            min_support = mlem2.getMinSupport(target_rules)
            print(min_support)
            
        rules_new.extend(target_rules)
        
    return(rules_new)

        
# ========================================
# main
# ========================================
if __name__ == "__main__":

    FILENAME = 'hayes-roth'
    iter1 = 1
    iter2 = 10
    
    rules = mlem2.getRulesByMLEM2(FILENAME, iter1, iter2)
    
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table = mlem2.getDecisionTable(filepath)
    colnames = mlem2.getColNames(decision_table)
    
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)
    list_judgeNominal = mlem2.getJudgeNominal(decision_table, list_nominal)
    
    # ルールクラスタリング
    #rules_new = getRuleClusteringBySimilarity(rules, colnames, list_judgeNominal, k=3)
    #rules_new = getRuleClusteringByRandom(rules, k=3)
    #rules_new = getRuleClusteringBySameCondition(rules, k=3)
    rules_new = getRuleClusteringByConsistentSimilarity(rules, colnames, list_judgeNominal, k=3)

    # predict by LERS
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-test'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table_test = mlem2.getDecisionTable(filepath)
    decision_table_test = decision_table_test.dropna()
    decision_class = decision_table_test[decision_table_test.columns[-1]].values.tolist()
    
    predictions = LERS.predictByLERS(rules_new, decision_table_test, list_judgeNominal)
    print(accuracy_score(decision_class, predictions))  

    # 全セットで確かめ
    #for iter1 in range(1,11):
    #    for iter2 in range(1,11):
    #        print('i1:{iter1} i2:{iter2}'.format(iter1=iter1,iter2=iter2))
    #        rules = mlem2.getRulesByMLEM2(FILENAME, iter1, iter2)
    #        filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.tsv'
    #        decision_table = mlem2.getDecisionTable(filepath)
    #        colnames = mlem2.getColNames(decision_table)
    
    #        filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'.nominal'
    #        list_nominal = mlem2.getNominalList(filepath)
    #        list_judgeNominal = mlem2.getJudgeNominal(decision_table, list_nominal)
    
    #        rules_new = getRuleClusteringBySimilarity(rules, colnames, list_judgeNominal, k=3)
