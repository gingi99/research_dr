# coding: utf-8
# python 3.5
from itertools import product
from sklearn.metrics import accuracy_score
import numpy as np
import joblib
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath("__file__"))+'/../MLEM2')
#sys.path.append('/Users/ooki/git/research_dr/python/MLEM2')
sys.path.append(os.path.dirname(os.path.abspath("__file__"))+'/../RuleClustering')
#sys.path.append('/Users/ooki/git/research_dr/python/RuleClustering')
import importlib
import mlem2
importlib.reload(mlem2)  
import LERS
importlib.reload(LERS) 
import clustering
importlib.reload(clustering) 

# Grobal setting
DIR_UCI = '/mnt/data/uci'

# ====================================
# 配慮変数削除　- MLEM2 - LERS による正答率実験
# ====================================
def MLEM2_LERS(FILENAME, iter1, iter2) :
    
    # FileNAM

    # rule induction
    fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2)

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename)

    # test data setup
    filepath = DIR_UCI+'/'+FILENAME+'/'+FILENAME+'-test'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table_test = mlem2.getDecisionTable(filepath)
    decision_table_test = decision_table_test.dropna()
    decision_class = decision_table_test[decision_table_test.columns[-1]].values.tolist()

    filepath = DIR_UCI+'/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)
    list_judgeNominal = mlem2.getJudgeNominal(decision_table_test, list_nominal)

    # predict by LERS
    predictions = LERS.predictByLERS(rules, decision_table_test, list_judgeNominal)

    # 正答率を求める
    accuracy = accuracy_score(decision_class, predictions)

    # ファイルにsave
    #savepath = DIR_UCI+'/'+FILENAME+'/MLEM2_LERS.csv'
    #with open(savepath, "a") as f :
    #    f.writelines('MLEM2_LERS,1,{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,iter1=iter1,iter2=iter2,acc=accuracy)+"\n")

    return(accuracy)

# ========================================
# multi に実行する
# ========================================
def multi_main(n_jobs, FILENAME, FUN, **kargs):
    results = joblib.Parallel(n_jobs=n_jobs)(joblib.delayed(FUN)(FILENAME, iter1, iter2) for (iter1,iter2) in product(range(1,11), range(1,11)))
    return(results)

# ========================================
# main
# ========================================
if __name__ == "__main__":

    # set data
    FILENAME = 'adult_cleansing2'
    FILENAME = 'german_credit_categorical'
    
    # シングルプロセスで実行
    #for FILENAME, iter1, iter2 in product(FILENAMES, range(1,11), range(1,11)):    
    #    print('{filename} {i1} {i2}'.format(filename=FILENAME, i1=iter1, i2=iter2))
    #    print(MLEM2_LERS(FILENAME, iter1, iter2))

    # 実行したい実験関数
    #FUN = MLEM2_LERS
    #FUN = MLEM2_OnlyK_LERS
    #FUN = MLEM2_RuleClusteringBySim_LERS
    #FUN = MLEM2_RuleClusteringByRandom_LERS
    #FUN = MLEM2_RuleClusteringBySameCondition_LERS
    #FUN = MLEM2_RuleClusteringByConsistentSim_LERS
    #FUN = MLEM2_RuleClusteringByConsistentSimExceptMRule_LERS
    #FUN = MLEM2_RuleClusteringByConsistentTimesSimExceptMRule_LERS
    #FUN = MLEM2_RuleClusteringBySimExceptMRule_LERS
    #FUN = MLEM2_RuleClusteringByConsistentExceptMRule_LERS
    
    FUNS = [MLEM2_LERS
    ]

    # 並列実行
    n_jobs = 4
    for FUN in FUNS :
        results = multi_main(n_jobs, FILENAME, FUN) 
    
    # 平均と分散
    ans = '{mean}±{std}'.format(mean=('%.3f' % round(np.mean(results),3)), std=('%.3f' % round(np.std(results),3)))
    print(ans)
    
    # 保存する
    #saveResults(results, "/data/uci/hayes-roth/accuracy.txt")
