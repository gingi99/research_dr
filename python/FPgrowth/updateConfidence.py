# -*- coding:utf-8 -*-
# Usage : python ~~.py
import sys
import os
import pickle
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

# Global Setting
DIR_UCI = '/mnt/data/uci'

# ------------------------------------------------------
# Rule Class
# ------------------------------------------------------
class Rule :
   def __init__(self):
       self.value = list()
       self.consequent = list()
       self.strength = float()
       self.support = list()
       self.support_v = float()
       self.conf = float()
   def setValue(self, values) :
       self.value = values
   def setConsequent(self, consequents) :
       self.consequent = consequents
   def setStrength(self, strength) :
       self.strength = strength
   def setSupport(self, supports) :
       self.support = supports
   def setSupportV(self, support_v):
       self.support_v = support_v
   def setConf(self, confidence) :
       self.conf = confidence
   def getValue(self) :
       return(self.value)
   def getConsequent(self) :
       return(self.consequent)
   def getStrength(self):
       return(self.strength)
   def getSupport(self) :
       return(self.support)
   def getSupportV(self) :
       return(self.support_v)
   def getSupportD(self) :
       return(self.support * len(self.value))
   def getConf(self) :
       return(self.conf)
   def output(self) :
       print("value:" + str(self.value))
       print("consequent:" + str(self.consequent))
       print("strength:" + str(self.strength))
       print("support:" + str(self.support))
       print("support_v:" + str(self.support_v))
       print("conf:" + str(self.conf))

# ======================================================
# rules load and save
# ======================================================
def loadPickleRules(fullpath_filename) :
    with open(fullpath_filename, mode='rb') as inputfile:
        rules = pickle.load(inputfile)
    return(rules)

def savePickleRules(rules, fullpath_filename) :
    with open(fullpath_filename, mode='wb') as outfile:
        pickle.dump(rules, outfile,  pickle.HIGHEST_PROTOCOL)

# ========================================
# rules をロードしてconfidence と ruleを満たす対象を出す
# ========================================
def updateConfidenceSupport(FILENAME, iter1, iter2, min_sup):
    # rules load
    fullpath_rulename = DIR_UCI+'/'+FILENAME+'/FPGrowth/rules/rules-'+str(min_sup)+'_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = loadPickleRules(fullpath_rulename)

    # train data load
    fullpath_train = DIR_UCI+'/'+FILENAME+'/alpha/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.txt'
    data = []
    with open(fullpath_train) as inputfile:
        for line in inputfile:
            data.append(line.strip().split(' '))

    # confidence and support and support_v
    for rule in rules: 
        bunshi = [rule.getConsequent() in record and all(x in record for x in rule.getValue()) for record in data]
        bunbo = [all(x in record for x in rule.getValue()) for record in data]
        confidence = sum(bunshi) / sum(bunbo)
        rule.setConf(confidence)
        
        support = [i for i, x in enumerate(bunshi) if x]
        rule.setSupport(support)

        support_v = len(support) / len(data)
        rule.setSupportV(support_v)

    # update save
    savePickleRules(rules, fullpath_rulename)

# ========================================
# multi に実行する
# ========================================
def multi_main(proc, FILENAME, FUN, **kargs):
    pool = Pool(proc)
    multiargs = []

    # FPGrowth_LERS 用
    if FUN == updateConfidenceSupport :
        min_sup_range = kargs['min_sup_range']
        for iter1, iter2, min_sup in product(range(1,2), range(1,11), min_sup_range):
            multiargs.append((FILENAME, iter1, iter2, min_sup))
        print(multiargs)
        pool.starmap(FUN, multiargs)

    else :
        print("I dont' know the function.")        
  
# ======================================================
# main
# ======================================================
if __name__ == "__main__":

    # データ準備
    FILENAME = "adult_cleansing2" 
    #FILENAME = "default_cleansing" 
    #FILENAME = "german_credit_categorical" 

    # クラスの数を設定
    #classes = ['D1', 'D2']

    # support range
    min_sup_range = [0.05, 0.10, 0.15, 0.20, 0.25]

    # 並列実行して全データで評価
    proc = 32
    freeze_support()
    FUN = updateConfidenceSupport
    multi_main(proc, FILENAME, FUN, min_sup_range = min_sup_range)
    
