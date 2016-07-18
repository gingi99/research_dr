# -*- coding:utf-8 -*-
# Usage : spark-submit ~~.py
from pyspark.context import SparkContext
from pyspark.mllib.fpm import FPGrowth
from pyspark import StorageLevel
import sys
import collections
import pandas as pd
import numpy as np
from itertools import chain
from itertools import combinations
from itertools import compress
from itertools import product
from sklearn.metrics import accuracy_score
from multiprocessing import Pool
from multiprocessing import freeze_support

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
# FP-growth によるルール抽出
# ======================================================
def getRulesByFPGrowth(FILENAME, iter1, iter2, classes, min_sup=3, min_conf=1.0, numPartitions=10) :
    
    # read data
    filepath = '/data/uci/'+FILENAME+'/alpha/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.txt'
    data = sc.textFile(filepath)
    transactions = data.map(lambda line: line.strip().split(' '))

    # 最小支持度を定める
    nrow = sum(1 for line in open(filepath))
    minSupport = float(min_sup) / float(nrow)

    # model 定義
    model = FPGrowth.train(transactions, minSupport=minSupport, numPartitions=numPartitions)
    
    # 実行
    result = model.freqItemsets().collect()

    # class 
    rules = []
    for cls in classes:
        for fi1 in result:
            if cls in fi1.items:
                target = [x for x in fi1.items if x != cls]
                for fi2 in result:
                    if collections.Counter(target) == collections.Counter(fi2.items):
                        conf = float(fi1.freq) / float(fi2.freq)
                        if conf >= min_conf:
                            rule = Rule()
                            rule.setValue(fi2.items)
                            rule.setConsequent(cls)
                            rule.setSupport(fi1.freq)
                            rule.setConf(conf)
                            rules.append(rule)

    return(rules)

# ======================================================
# LERS による精度評価
# ======================================================
def predictByLERS(FILENAME, iter1, iter2, rules) :
    
    # read test data
    filepath = '/data/uci/'+FILENAME+'/alpha/'+FILENAME+'-test'+str(iter1)+'-'+str(iter2)+'.txt'
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

# ======================================================
# FP-growth_LERS
# ======================================================
def FPGrowth_LERS(FILENAME, iter1, iter2, min_sup):
    classes = ['D1', 'D2', 'D3']
    min_conf = 1.0
 
    # rule 抽出
    rules = getRulesByFPGrowth(FILENAME, iter1, iter2, classes, min_sup, min_conf)

    # predict by LERS
    accuracy = predictByLERS(FILENAME, iter1, iter2, rules)
    
    # save
    savepath = '/data/uci/'+FILENAME+'/FPGrowth_LERS.csv'
    with open(savepath, "a") as f :
        f.writelines('FPGrowth_LERS,{min_sup},{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,iter1=iter1,iter2=iter2,acc=accuracy,min_sup=min_sup)+"\n")

    return(accuracy)

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

    # FPGrowth_LERS 用
    if FUN == FPGrowth_LERS :
        min_sup_range = kargs['min_sup'] if 'min_sup' in kargs else range(2,11)
        for iter1, iter2, min_sup in product(range(1,11), range(1,11), min_sup_range):            
            multiargs.append((FILENAME, iter1, iter2, min_sup))
        print(multiargs)
        results = pool.starmap(FUN, multiargs)

    else :
        print("I dont' know the function.")        
  
    return(results)

# ======================================================
# main
# ======================================================
if __name__ == "__main__":

    SparkContext.setSystemProperty('spark.executor.memory', '64g')
    sc = SparkContext("local[2]", appName="Sample FP-growth")
    sc.setLogLevel("ERROR")

    # データ準備
    #FILEPATH = "/usr/local/share/spark/data/mllib/sample_fpgrowth.txt"
    #"/data/uci/hayes-roth/alpha/hayes-roth-train2-10.txt"
    #FILENAME = "hayes-roth" 
    FILENAME = "nursery" 
    iter1 = 6 
    iter2 = 9 
    #classes = ['D1', 'D2', 'D3']
    classes = ['D1', 'D2', 'D3', 'D4', 'D5']
    min_sup = 2
    #min_sup_range = range(3,11,1)
    min_sup_range = range(3,30,3)
    min_conf = 1.0
    savepath = '/data/uci/'+FILENAME+'/FPGrowth_LERS.csv'
 
    # rule 抽出
    #rules = getRulesByFPGrowth(FILENAME, iter1, iter2, classes, min_sup, min_conf)
    #for rule in rules :
    #    print(rule.output())

    # predict by LERS
    #print(predictByLERS(FILENAME, iter1, iter2, rules))
    
    # identify
    #p = 2
    #print(getPerIdentifiedClass(rules, 2))

    # 並列実行して全データで評価
    #proc=4
    #freeze_support()
    #FUN = FPGrowth_LERS
    #results = multi_main(proc, FILENAME, FUN, min_sup = min_sup_range)

    # 直列実行して全データで評価
    for min_sup in min_sup_range:
        results = []
        for iter1 in range(1,11,1):
            for iter2 in range(1,11,1):
                print(str(min_sup),",",str(iter1),",",str(iter2))
                rules = getRulesByFPGrowth(FILENAME, iter1, iter2, classes, min_sup, min_conf)
                accuracy = predictByLERS(FILENAME, iter1, iter2, rules)
                # save
                with open(savepath, "a") as f :
                    f.writelines('FPGrowth_LERS,{min_sup},{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,iter1=iter1,iter2=iter2,acc=accuracy,min_sup=min_sup)+"\n")
                results.append(accuracy)
        # 平均と分散
        print(getEvalMeanVar(results))
    
