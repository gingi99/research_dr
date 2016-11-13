# coding: utf-8
# python 3.5
import sys
import os
sys.path.append('/Users/ooki/git/research_dr/python/MLEM2')
sys.path.append(os.path.dirname(os.path.abspath("__file__"))+'/../MLEM2')
from sklearn.metrics import accuracy_score
import importlib
import mlem2
import LERS
import copy
importlib.reload(mlem2)  
importlib.reload(LERS)  
    
# =====================================
# 公正配慮すべき属性list_sをdecision_tableから削除する
# =====================================
def delDiscriminativeAttributes(decision_table, list_s):
    return(decision_table.drop(list_s, axis=1))

# =====================================
# Rules のうち 基本条件 e(属性attrの値v) を含むルールセットを返す
# =====================================    
def getRulesIncludeE(list_rules, attr, v) :
    rules = [r for r in list_rules if r.getValue(attr) == v]
    return(rules)
    
# =====================================
# Rules のうち 属性attr / 基本条件e を 含まないルールセットを返す
# =====================================    
def getRulesExcludeAttr(list_rules, attr) :
    rules = [r for r in list_rules if not attr in r.getKey()]
    return(rules)
 
def getRulesExcludeE(list_rules, attr, v) :
    rules = [r for r in list_rules if r.getValue(attr) != v]
    return(rules)

# =====================================
# Rules のうち 属性attr / 基本条件e を 削除したルールセットを返す
# Rule の 属性attr / 基本条件　e を削除したルールを返す
# =====================================
def getRulesDelAttr(list_rules, attr) :
    rules = [delAttrFromRule(r, attr) for r in list_rules]
    return(rules)
    
def getRulesDelE(list_rules, attr, v) :
    rules = [delEFromRule(r, attr, v) for r in list_rules]
    return(rules)
 
def delAttrFromRule(rule, attr) :
    rule_new = copy.deepcopy(rule)
    rule_new.delKey(attr)
    return(rule_new)

def delEFromRule(rule, attr, v) :
    if rule.getValue(attr) == v : return(delAttrFromRule(rule, attr))
    else : return(rule)
    
# =====================================
# alpha差別的な Rule を含まないルールセットを返す
# alpha差別的な Rule の 基本条件　e を削除したルールを返す
# =====================================   
def getAlphaRulesExcludeE(list_rules, attr, v, decision_table, list_judgeNominal, alpha = 0) :
    rules = [r for r in list_rules if getElift(r, attr, v, decision_table, list_judgeNominal) <= alpha ]
    return(rules)

def getAlphaRulesDelE(list_rules, attr, v, decision_table, list_judgeNominal, alpha = 0) :
    rules = [delEFromAlphaRule(r, attr, v, decision_table, list_judgeNominal, alpha = 0) for r in list_rules]
    return(rules)
    
def delEFromAlphaRule(rule, attr, v, decision_table, list_judgeNominal, alpha = 0):
    if rule.getValue(attr) == v :
        elift = getElift(rule, attr, v, decision_table, list_judgeNominal)
        if elift > alpha : return(delAttrFromRule(rule, attr))
        else : return(rule)
    else : 
        return(rule)

# =====================================
# M差別的な Rule の を含まないルールセットを返す
# M差別的な Rule の 基本条件　e を削除したルールを返す
# =====================================  
def getMRulesFUN(list_rules, attr, v, target_cls, DELFUN, m = 0) :
    num_target_cls, num_other_cls, list_num_other_cls = 0, 0, []
    classes = getClassFromRules()
    for cls in classes :
        if cls == target_cls :
            num_target_cls = getNumAttrClass(list_rules, attr, v, cls)
        else :
            list_num_other_cls.append(getNumAttrClass(list_rules, attr, v, cls))
    num_other_cls = sum(list_num_other_cls) / len(list_num_other_cls)
    if num_target_cls / num_other_cls > m : #m保護なら
        return(list_rules)
    else :
        return(DELFUN(list_rules, attr, v))

# 有利な決定クラスのルールを減らす関数 配慮変数sを
# 不利な決定クラスのルールを増やす関数 配慮変数sをもつ対象だけの決定表を作りルール抽出

# =====================================
# Rule の 配慮変数s での decision_tableにおける　elift
# =====================================
def getElift(rule, attr, v, decision_table, list_judgeNominal):
    supp, conf = LERS.getSupportConfidence(rule, decision_table, list_judgeNominal)
    rule_s = delEFromRule(rule, attr, v)
    supp_s, conf_s = LERS.getSupportConfidence(rule_s, decision_table, list_judgeNominal)
    if conf_s == 0: elift = 999
    else : elift = conf / conf_s
    return(elift)
    
# =====================================
# Rule の 配慮変数s での decision_tableにおける　slift
# =====================================
def getSlift(rule, s, decision_table, operator):
    conditions = mlem2.getConditionValues(decision_table, s)
    clifts = [getClift(rule, s, c, decision_table) for c in conditions]
    slift = operator(clifts)
    return(slift)

# =====================================
# Rule の 配慮変数s と 代替する変数c での decision_tableにおける　clift
# =====================================
def getClift(rule, s, c, decision_table, list_judgeNominal):
    supp, conf = LERS.getSupportConfidence(rule, decision_table,list_judgeNominal)
    rule_c = mlem2.delEfromRule(rule,s)
    rule_c = rule_c.setValue(s,c)
    supp_c, conf_c = LERS.getSupportConfidence(rule_c, decision_table, list_judgeNominal)
    clift = conf / conf_c
    return(clift)

# ========================================
# main
# ========================================
if __name__ == "__main__":

    # 設定
    DIR_UCI = '/mnt/data/uci/'
    FILENAME = 'german_credit_categorical'    
    iter1 = 1
    iter2 = 1
    
    # rule induction
    rules = mlem2.getRulesByMLEM2(FILENAME, iter1, iter2)

    # test data
    filepath = DIR_UCI+FILENAME+'/'+FILENAME+'-test'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table_test = mlem2.getDecisionTable(filepath)
    decision_table_test = decision_table_test.dropna()
    decision_class = decision_table_test[decision_table_test.columns[-1]].values.tolist()

    # nominal data
    filepath = DIR_UCI+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)
    list_judgeNominal = mlem2.getJudgeNominal(decision_table_test, list_nominal)
    
    # predict by LERS
    predictions = LERS.predictByLERS(rules, decision_table_test, list_judgeNominal)
    
    # 正答率を求める
    accuracy_score(decision_class, predictions)
    
    # rules の数を求める
    num = len(rules)
    # 平均の長さを求める
    mean_length = mlem2.getMeanLength(rules)

    # train data setup
    decision_table_train, decision_class = getData(FILENAME, iter1, iter2, T = "train")
    list_judgeNominal = getJudgeNominal(decision_table_train, FILENAME)

    # 平均支持度と平均確信度を求める
    mean_support, mean_conf = LERS.getSupportConfidenceRules(rules, decision_table_train, list_judgeNominal)
    # AccとRecallを求める
    acc_recall = LERS.getAccurayRecall(rules, decision_table_train, list_judgeNominal)
    for i,c in enumerate(mlem2.getEstimatedClass(rules)):
        print(str(acc_recall[i][0])+","+str(acc_recall[i][1]))
    
    ###### 公正配慮のテスト    
    
    # 基本条件を含むルールセット
    rules_sex_2 = mlem2.getRulesIncludeE(rules, "Sex_Marital_Status", "2.0")
    rules_sex_4 = mlem2.getRulesIncludeE(rules, "Sex_Marital_Status", "4.0")    
    # 条件を含まないルールセット    
    rules_exclude_sex = mlem2.getRulesExcludeAttr(rules, "Sex_Marital_Status")
    # 基本条件を含まないルールセット    
    rules_exclude_sex_1 = mlem2.getRulesExcludeE(rules, "Sex_Marital_Status", "1.0")
    # 条件を削除したルールセット
    rules_del_value = mlem2.getRulesDelAttr(rules, "Value_Savings_Stocks")    
    # 基本条件を削除したルールセット
    rules_del_value_1 = mlem2.getRulesDelE(rules, "Value_Savings_Stocks", "1.0")    
    
    # 条件を1つ削除する例
    rule = mlem2.delAttrFromRule(rules[12],'No_of_dependents')
    rule = mlem2.delAttrFromRule(rules[12],'Concurrent_Credits')

 
    
    # ====
        
    # read data
    filepath = '/mnt/data/uci/'+FILENAME+'/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table = mlem2.getDecisionTable(filepath)
    decision_table = decision_table.dropna()
    decision_table.index = range(decision_table.shape[0])

    # read nominal
    filepath = '/mnt/data/uci/'+'/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)
    
    # ルールを満たすやつ ほとんどないな。。
    match_objects = decision_table.apply(lambda obj: isExplainRule(obj, rules[12], list_judgeNominal), axis=1)    

    # confidence
    getConfidence(rule, decision_table, list_judgeNominal)
    
    rules_sex_2 = mlem2.getRulesIncludeE(rules, "Sex_Marital_Status","2.0")

    