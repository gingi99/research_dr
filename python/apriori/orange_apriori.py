# coding: utf-8
# python 2.7
import Orange
import pandas as pd
import numpy as np
import sys
import os
from collections import defaultdict
from itertools import chain
from itertools import combinations
from itertools import compress
from itertools import product
from sklearn.metrics import accuracy_score
from multiprocessing import Pool
from multiprocessing import freeze_support

# Global Setting
DIR_UCI = '/mnt/data/uci'

# ------------------------------------------------------
# Rule Class
# ------------------------------------------------------
class Rule :
   def __init__(self):
       self.value = list()
       self.consequent = list()
       self.support = float()
       self.conf = float()
   def setValue(self, values) :
       self.value = values
   def setConsequent(self, consequents) :
       self.consequent = consequents
   def setSupport(self, supports) :
       self.support = supports
   def setConf(self, confidence) :
       self.conf = confidence
   def getValue(self) :
       return(self.value)
   def getConsequent(self) :
       return(self.consequent)
   def getSupport(self) :
       return(self.support)
   def getSupportD(self) :
       return(self.support * len(self.value))
   def getConf(self) :
       return(self.conf)
   def output(self) :
       print("value:" + str(self.value))
       print("consequent:" + str(self.consequent))
       print("support:" + str(self.support))
       print("conf:" + str(self.conf))

# ======================================================
# Rules のうち、P個の属性値が分かれば、クラスを推定できるか
# ======================================================
def getPerIdentifiedClass(rules, p) :

    attribute_values = [rule.getValue() for rule in rules]
    attribute_values = list(chain.from_iterable(attribute_values))
    attribute_values = list(set(attribute_values))

    combi_attribute_values = combinations(attribute_values,p)
    count = 0
    bunbo = 0
    for combi in combi_attribute_values :
        bunbo += 1
        rules_target = []
        for rule in rules :
            matching_count = len(list(set(combi) & set(rule.getValue())))
            if matching_count == len(list(combi)) :
                rules_target.append(rule)
        # rules_target が空なら評価から外す
        if len(rules_target) == 0:
            bunbo -= 1
        #
        else :
            consequents = [rule.getConsequent() for rule in rules_target]
            if len(list(set(consequents))) == 1:
                count += 1
    if bunbo == 0:
        ans = 0
    else:
        ans = (float(count) / float(bunbo))
    return(ans)

# ======================================================
# ルールが対象のクラスを説明するかどうか
# ======================================================
def isExplainRule(obj, rule) :
    matching_count = len(list(set(obj) & set(rule.getValue())))
    if matching_count == len(rule.getValue()) : return(True)
    else : return(False)

# ======================================================
# ルールが対象のクラスを説明するかどうか
# ======================================================
def getMatchingFactor(obj, rule) :
    matching_factor = len(list(set(obj) & set(rule.getValue())))
    matching_factor = matching_factor / len(rule.getValue())
    return(matching_factor)

# ======================================================
# ルールのsupport P を返す
# ======================================================
def getSupportP(obj, rule) :
    matching_factor = getMatchingFactor(obj, rule)
    return(rule.getSupportD() * matching_factor)

# ======================================================
# ルールから対象のクラスを予測
# ======================================================
def estimateClass(obj, rules) :

    list_judge = [isExplainRule(obj, r) for r in rules]

    # 1つ以上マッチするなら
    if any(list_judge) :
      consequents = [rules[i].getConsequent() for i, judge in enumerate(list_judge) if judge]
      print consequents

      # マッチしたルールが推論するクラスの数がただ1つなら
      if len(set(consequents)) == 1 :
          return(consequents[0])
      else :
          rules_match = list(compress(rules,list_judge))
          supportD = [r.getSupportD() for r in rules_match]
          return(rules_match[supportD.index(max(supportD))].getConsequent())

    # rule が objに1つもマッチしない場合は部分一致ルールによる推定
    else :
        supportP = [getSupportP(obj, rule) for rule in rules]
        return(rules[supportP.index(max(supportP))].getConsequent())

# ======================================================
# LERS による精度評価
# ======================================================
def predictByLERS(FILENAME, iter1, iter2, rules) :

    # read test data
    filepath = DIR_UCI+'/'+FILENAME+'/alpha/'+FILENAME+'-test'+str(iter1)+'-'+str(iter2)+'.txt'
    decision_table_test = pd.read_csv(filepath, delimiter=' ', header=None)
    decision_table_test = decision_table_test.dropna()
    decision_class = decision_table_test[decision_table_test.columns[-1]].values.tolist()
    decision_table_test = decision_table_test.drop(decision_table_test.columns[len(decision_table_test.columns)-1], axis=1)
    decision_table_test = decision_table_test.values.tolist()

    # LERS で予測
    predictions = []
    for obj in decision_table_test:
        estimated_class = estimateClass(obj, rules)
        predictions.append(estimated_class)

    # 正答率を求める
    accuracy = accuracy_score(decision_class, predictions)
    print(accuracy)

    return(accuracy)
   
# =====================================
# Main 関数
# =====================================
def getRulesByApriori(FILENAME, classes, iter1, iter2, minsup, minconf) :
    
    # read data
    filepath = DIR_UCI+'/'+FILENAME+'/alpha/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.txt'
    data_pd = pd.read_csv(filepath, delimiter=' ')
    pd.DataFrame.to_csv(data_pd, DIR_UCI+'/'+FILENAME+'/alpha/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.basket', index=False, sep=',')
    filepath = DIR_UCI+'/'+FILENAME+'/alpha/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.basket'
    data_table = Orange.data.Table(filepath)
    #print len(data_table)

    # set parameter
    num_lines = sum(1 for line in open(filepath))
    minsup = float(minsup) / float(num_lines)
    #print minsup

    # induce rules
    #rules_orange = Orange.associate.AssociationRulesSparseInducer(data_table, support=minsup, confidence=minconf)
    rules_orange = Orange.associate.AssociationRulesSparseInducer(data_table, support = minsup)

    # convert Rule Class
    rules = []
    for rule_orange in rules_orange :
        consequent = rule_orange.right.get_metas(str).keys()
        if len(consequent) == 1 and consequent[0] in classes and rule_orange.confidence >= minconf :
            rule = Rule()
            rule.setValue(rule_orange.left.get_metas(str).keys())
            rule.setConsequent(consequent[0])
            rule.setSupport(rule_orange.support)
            rule.setConf(rule_orange.confidence)
            rules.append(rule)
    # END
    return(rules)

# ======================================================
# Apriori_LERS
# ======================================================
def Apriori_LERS(FILENAME, classes, iter1, iter2, min_sup, min_conf):

    # rule 抽出
    rules = getRulesByApriori(FILENAME, classes, iter1, iter2, min_sup, min_conf)

    # predict by LERS
    accuracy = predictByLERS(FILENAME, iter1, iter2, rules)

    # save
    savepath = DIR_UCI+'/'+FILENAME+'/Apriori_LERS.csv'
    with open(savepath, "a") as f :
        f.writelines('Apriori_LERS,{min_sup},{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,iter1=iter1,iter2=iter2,acc=accuracy,min_sup=min_sup)+"\n")

    # END
    return(accuracy)

def wrapper_Apriori_LERS(multi_args):
    multi_args[0](multi_args[1],multi_args[2],multi_args[3],multi_args[4],multi_args[5],multi_args[6])

# ========================================
# listの平均と分散を求める
# ========================================
def getEvalMeanVar(result):
    ans = '{mean}±{std}'.format(mean=('%.3f' % round(np.mean(results),3)), std=('%.3f' % round(np.std(results),3)))
    return(ans)

# ========================================
# multi に実行する
# ========================================
def multi_main(proc, FILENAME, FUN, **kargs):
    pool = Pool(proc)
    results = []
    multiargs = []
    classes = kargs['classes']
    min_sup_range = kargs['min_sup'] if 'min_sup' in kargs else range(2,11)
    min_conf = kargs['min_conf']

    # Apriori_LERS 用
    if FUN == Apriori_LERS :
        WRAPPER_FUN = wrapper_Apriori_LERS
        for iter1, iter2, min_sup in product(range(1,11), range(1,11), min_sup_range):
            multiargs.append((FUN, FILENAME, classes, iter1, iter2, min_sup, min_conf))
        #print(multiargs)
        results = pool.map(WRAPPER_FUN, multiargs)

    else :
        print("I dont' know the function.")

    return(results)

# ========================================
# main
# ========================================
if __name__ == "__main__":

    FILENAME = 'hayes-roth'
    classes = ['D1', 'D2', 'D3']
    iter1 = 10
    iter2 = 3

    # support と confidence の閾値
    min_sup_range = range(2,11,1)
    min_sup = 1
    min_conf = 1.0

    # rule induction
    #rules = getRulesByApriori(FILENAME, classes, iter1, iter2, min_sup, min_conf)

    #print len(rules)
    #for r in rules:
    #    print(r.output())

    # predict by LERS
    #print(predictByLERS(FILENAME, iter1, iter2, rules))

    # 並列実行して全データで評価
    proc=32
    freeze_support()
    FUN = Apriori_LERS
    results = multi_main(proc, FILENAME, FUN, classes = classes, min_sup = min_sup_range, min_conf = min_conf)
