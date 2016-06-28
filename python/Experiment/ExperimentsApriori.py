# coding: utf-8
# python 3.5
from itertools import product
from sklearn.metrics import accuracy_score
from multiprocessing import Pool
from multiprocessing import freeze_support
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath("__file__"))+'/../MLEM2')
#sys.path.append('/Users/ooki/git/research_dr/python/MLEM2')
sys.path.append(os.path.dirname(os.path.abspath("__file__"))+'/../apriori')
#sys.path.append('/Users/ooki/git/research_dr/python/apriori')
import logging
import importlib
import mlem2
importlib.reload(mlem2)  
import LERS
importlib.reload(LERS) 
import apriori
importlib.reload(apriori) 

# ====================================
# Apriori - LERS による正答率実験
# FILENAME = "hayes-roth"
# iter1 = 1
# iter2 = 1
# minsup = 10
# minconf = 1
# ====================================
def Apriori_LERS(FILENAME, iter1, iter2, minsup, minconf) :
          
    # rule induction
    fullpath_filename = '/data/uci/'+FILENAME+'/apriori/'+'rules_'+str(iter1)+'-'+str(iter2)+'-'+str(minsup)+'-'+str(minconf)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else apriori.getRulesByApriori(FILENAME, iter1, iter2, minsup, minconf) 

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename) 

    # test data setup
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-test'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table_test = mlem2.getDecisionTable(filepath)
    decision_table_test = decision_table_test.dropna()
    decision_class = decision_table_test[decision_table_test.columns[-1]].values.tolist()

    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)
    list_judgeNominal = mlem2.getJudgeNominal(decision_table_test, list_nominal)
    
    # predict by LERS
    predictions = LERS.predictByLERS(rules, decision_table_test, list_judgeNominal)
    
    # 正答率を求める
    accuracy = accuracy_score(list(map(str,decision_class)), predictions)
    
    #print('{FILENAME} : {iter1} {iter2}'.format(FILENAME=FILENAME,iter1=iter1,iter2=iter2))    
    logging.basicConfig(filename=os.path.dirname(os.path.abspath("__file__"))+'/'+FILENAME+'.log',format='%(asctime)s,%(message)s',level=logging.DEBUG)
    logging.info('Apriori_LERS,{FILENAME},{iter1},{iter2},{acc},{minsup},{minconf}'.format(FILENAME=FILENAME,iter1=iter1,iter2=iter2,acc=accuracy,minsup=minsup,minconf=minconf))
    
    return(accuracy)
  
# ========================================
# multi に実行する
# ========================================
def multi_main(proc, FILENAMES, FUN, **kargs):
    pool = Pool(proc)
    results = []
    multiargs = []

    # Apriori_LERS 用
    if FUN == Apriori_LERS :
        minconf = 1
        minsup_range = kargs['minsup'] if 'minsup' in kargs else range(5,10,5)
        for minsup in minsup_range:
            for FILENAME, iter1, iter2 in product(FILENAMES, range(1,11), range(1,11)):            
                multiargs.append((FILENAME,iter1,iter2,minsup,minconf))
            results = pool.starmap(FUN, multiargs)
    # その他
    else :
        print("I dont' know the function.")        
  
    #results = pool.starmap(FUN, multiargs)
    return(results)
  
# ========================================
# listの平均と分散を求める
# ========================================
def getEvalMeanVar(result):
    ans = '{mean}±{std}'.format(mean=('%.3f' % round(np.mean(results),3)), std=('%.3f' % round(np.std(results),3)))
    return(ans)

  
# ========================================
# main
# ========================================
if __name__ == "__main__":

    # set data and k
    FILENAMES = ['hayes-roth']
    minconf = 1
    minsup_range = range(10,15,5)
    
    # シングルプロセスで実行
    #for FILENAME, iter1, iter2 in product(FILENAMES, range(1,11), range(1,11)):    
    #    print('{filename} {i1} {i2}'.format(filename=FILENAME, i1=iter1, i2=iter2))
    #    print(MLEM2_LERS(FILENAME, iter1, iter2))

    # 実行したい実験関数
    FUN = Apriori_LERS

    # 並列実行
    proc=4
    freeze_support()
    
    #for FUN in FUNS :
    results = multi_main(proc, FILENAMES, FUN, minsup = minsup_range)
    # 平均と分散
    print(getEvalMeanVar(results))
    