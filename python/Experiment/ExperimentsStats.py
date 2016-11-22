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
# MLEM2 - STAT による正答率実験
# ====================================
def MLEM2_STAT(FILENAME, iter1, iter2) :

    # rule induction
    fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2)

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename)

    # rules の数を求める
    num = len(rules)
    # 平均の長さを求める
    leng = mlem2.getMeanLength(rules)
    # 平均支持度を求める
    support = mlem2.getMeanSupport(rules) 

    # ファイルにsave
    savepath = DIR_UCI+'/'+FILENAME+'/MLEM2_STAT.csv'
    with open(savepath, "a") as f :
        f.writelines('MLEM2_STAT,1,{FILENAME},{iter1},{iter2},{num},{leng},{support}'.format(FILENAME=FILENAME,iter1=iter1,iter2=iter2,num=num,leng=leng,support=support)+"\n")

    return(0)

# ====================================
# MLEM2 - k以上のルールだけにする - STAT による正答率実験
# ====================================
def MLEM2_OnlyK_STAT(FILENAME, iter1, iter2, k) :

    print("START iter1 iter2 k : " + str(iter1) + "," + str(iter2) + "," + str(k))
    # rule induction
    fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2)

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename)

    # only-k rule filter
    fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules_onlyK/'+'rules-'+str(k)+'_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else [r for r in rules if len(r.getSupport()) >= k]

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename)

    # rules の数を求める
    num = len(rules)
    # 平均の長さを求める
    leng = mlem2.getMeanLength(rules)
    # 平均支持度を求める
    support = mlem2.getMeanSupport(rules) 

    # ファイルにsave
    savepath = DIR_UCI+'/'+FILENAME+'/MLEM2_OnlyK_STAT.csv'
    with open(savepath, "a") as f :
        f.writelines('MLEM2_OnlyK_STAT,{k},{FILENAME},{iter1},{iter2},{num},{leng},{support}'.format(FILENAME=FILENAME,k=k,iter1=iter1,iter2=iter2,num=num,leng=leng,support=support)+"\n")
    
    return(0)

# ====================================
# MLEM2 - RuleClustering by Consistent × Sim Except M Support - STAT による正答率実験
# ====================================
def MLEM2_RuleClusteringByConsistentTimesSimExceptMRule_STAT(FILENAME, iter1, iter2, k, m) :
    # rule induction
    fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2) 

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename) 

    # rule clustering
    filepath = DIR_UCI+'/'+FILENAME+'/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table = mlem2.getDecisionTable(filepath)
    colnames = mlem2.getColNames(decision_table)
    
    filepath = DIR_UCI+'/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)
    list_judgeNominal = mlem2.getJudgeNominal(decision_table, list_nominal)

    fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules_cluster_consistent_times_sim_except_mrule/'+'rules-'+str(k)+'_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else clustering.getRuleClusteringByConsistentTimesSimilarityExceptMRule(rules, colnames, list_judgeNominal, k=k, m=m)

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename) 

    # rules の数を求める
    num = len(rules)
    # 平均の長さを求める
    leng = mlem2.getMeanLength(rules)
    # 平均支持度を求める
    support = mlem2.getMeanSupport(rules)
    
    # ファイルにsave
    savepath = DIR_UCI+'/'+FILENAME+'/MLEM2_RuleClusteringByConsistentTimesSimExceptMRule_STAT.csv'
    with open(savepath, "a") as f :
        f.writelines('MLEM2_RuleClusteringByConsistentTimesSimExceptMRule_STAT,{k},{FILENAME},{iter1},{iter2},{num},{leng},{support}'.format(FILENAME=FILENAME,k=k,iter1=iter1,iter2=iter2,num=num,leng=leng,support=support)+"\n")
    
    return(0)
    
# ====================================
# MLEM2 - RuleClustering by Similarity Except M Support - STAT による正答率実験
# ====================================
def MLEM2_RuleClusteringBySimExceptMRule_STAT(FILENAME, iter1, iter2, k, m) :
    # rule induction
    fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2) 

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename) 

    # rule clustering
    filepath = DIR_UCI+'/'+FILENAME+'/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table = mlem2.getDecisionTable(filepath)
    colnames = mlem2.getColNames(decision_table)
    
    filepath = DIR_UCI+'/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)
    list_judgeNominal = mlem2.getJudgeNominal(decision_table, list_nominal)

    fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules_cluster_sim_except_mrule/'+'rules-'+str(k)+'_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else clustering.getRuleClusteringBySimilarityExceptMRule(rules, colnames, list_judgeNominal, k=k, m=m)

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename) 

    # rules の数を求める
    num = len(rules)
    # 平均の長さを求める
    leng = mlem2.getMeanLength(rules)
    # 平均支持度を求める
    support = mlem2.getMeanSupport(rules)
    
    # ファイルにsave
    savepath = DIR_UCI+'/'+FILENAME+'/MLEM2_RuleClusteringBySimExceptMRule_STAT.csv'
    with open(savepath, "a") as f :
        f.writelines('MLEM2_RuleClusteringBySimExceptMRule_STAT,{k},{FILENAME},{iter1},{iter2},{num},{leng},{support}'.format(FILENAME=FILENAME,k=k,iter1=iter1,iter2=iter2,num=num,leng=leng,support=support)+"\n")
    
    return(0)

# ====================================
# MLEM2 - RuleClustering by Consistent Except M Support - STATによる正答率実験
# ====================================
def MLEM2_RuleClusteringByConsistentExceptMRule_STAT(FILENAME, iter1, iter2, k, m) :
    # rule induction
    fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2) 

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename) 

    # rule clustering
    filepath = DIR_UCI+'/'+FILENAME+'/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table = mlem2.getDecisionTable(filepath)
    colnames = mlem2.getColNames(decision_table)
    
    filepath = DIR_UCI+'/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)
    list_judgeNominal = mlem2.getJudgeNominal(decision_table, list_nominal)

    fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules_cluster_consistent_except_mrule/'+'rules-'+str(k)+'_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else clustering.getRuleClusteringByConsistentExceptMRule(rules, colnames, list_judgeNominal, k=k, m=m)

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename) 

    # rules の数を求める
    num = len(rules)
    # 平均の長さを求める
    leng = mlem2.getMeanLength(rules)
    # 平均支持度を求める
    support = mlem2.getMeanSupport(rules)
    
    # ファイルにsave
    savepath = DIR_UCI+'/'+FILENAME+'/MLEM2_RuleClusteringByConsistentExceptMRule_STAT.csv'
    with open(savepath, "a") as f :
        f.writelines('MLEM2_RuleClusteringByConsistentExceptMRule_STAT,{k},{FILENAME},{iter1},{iter2},{num},{leng},{support}'.format(FILENAME=FILENAME,k=k,iter1=iter1,iter2=iter2,num=num,leng=leng,support=support)+"\n")
    
    return(0)

# ====================================
# MLEM2 - RuleClustering by Random - STAT による正答率実験
# ====================================
def MLEM2_RuleClusteringByRandom_STAT(FILENAME, iter1, iter2, k) :
          
    # rule induction
    fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2) 

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename) 

    # rule clustering
    fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules_cluster_random/'+'rules-'+str(k)+'_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else clustering.getRuleClusteringByRandom(rules, k=k)

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename) 

    # rules の数を求める
    num = len(rules)
    # 平均の長さを求める
    leng = mlem2.getMeanLength(rules)
    # 平均支持度を求める
    support = mlem2.getMeanSupport(rules)
    
    # ファイルにsave
    savepath = DIR_UCI+'/'+FILENAME+'/MLEM2_RuleClusteringByRandom_STAT.csv'
    with open(savepath, "a") as f :
        f.writelines('MLEM2_RuleClusteringByRandom_STAT,{k},{FILENAME},{iter1},{iter2},{num},{leng},{support}'.format(FILENAME=FILENAME,k=k,iter1=iter1,iter2=iter2,num=num,leng=leng,support=support)+"\n")

    return(0)

# ====================================
# MLEM2 - RuleClustering by SameCondition - STAT による正答率実験
# ====================================
def MLEM2_RuleClusteringBySameCondition_STAT(FILENAME, iter1, iter2, k) :
          
    # rule induction
    fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2) 

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename) 

    # rule clustering
    fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules_cluster_same_condition/'+'rules-'+str(k)+'_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else clustering.getRuleClusteringBySameCondition(rules, k=k)

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename) 

    # rules の数を求める
    num = len(rules)
    # 平均の長さを求める
    leng = mlem2.getMeanLength(rules)
    # 平均支持度を求める
    support = mlem2.getMeanSupport(rules)
    
    # ファイルにsave
    savepath = DIR_UCI+'/'+FILENAME+'/MLEM2_RuleClusteringBySameCondition_STAT.csv'
    with open(savepath, "a") as f :
        f.writelines('MLEM2_RuleClusteringBySameCondition_STAT,{k},{FILENAME},{iter1},{iter2},{num},{leng},{support}'.format(FILENAME=FILENAME,k=k,iter1=iter1,iter2=iter2,num=num,leng=leng,support=support)+"\n")

    return(0)

# ========================================
# results を saveする
# ========================================
def saveResults(results, FILENAME):
    filename = FILENAME
    outfile = open(filename, 'w')  
    for x in results:
        outfile.write(str(x) + "\n")
    outfile.close()
    
# ========================================
# multi に実行する
# ========================================
def multi_main(proc, FILENAMES, FUN, **kargs):
    pool = Pool(proc)
    results = []
    multiargs = []

    # MLEM2_STAT 用
    if FUN == MLEM2_STAT :
        for FILENAME, iter1, iter2 in product(FILENAMES, range(1,11), range(1,11)):            
            multiargs.append((FILENAME,iter1,iter2))
        results = pool.starmap(FUN, multiargs)
        
    # MLEM2_RuleClusteringByConsistentTimesSimExceptMRule_STAT 用
    elif FUN == MLEM2_RuleClusteringByConsistentTimesSimExceptMRule_STAT :
        k_range = kargs['k'] if 'k' in kargs else range(2,11)
        #for k in k_range:
        for FILENAME, iter1, iter2, k in product(FILENAMES, range(1,11), range(1,11), k_range):
            multiargs.append((FILENAME,iter1,iter2,k,k))
        results.extend(pool.starmap(FUN, multiargs))

    # MLEM2_RuleClusteringBySimExceptMRule_STAT 用
    elif FUN == MLEM2_RuleClusteringBySimExceptMRule_STAT :
        k_range = kargs['k'] if 'k' in kargs else range(2,11)
        #for k in k_range:
        for FILENAME, iter1, iter2, k in product(FILENAMES, range(1,11), range(1,11), k_range):
            multiargs.append((FILENAME,iter1,iter2,k,k))
        results.extend(pool.starmap(FUN, multiargs))
    
    # MLEM2_RuleClusteringByConsistentExceptMRule_STAT 用
    elif FUN == MLEM2_RuleClusteringByConsistentExceptMRule_STAT :
        k_range = kargs['k'] if 'k' in kargs else range(2,11)
        #for k in k_range:
        for FILENAME, iter1, iter2, k in product(FILENAMES, range(1,11), range(1,11), k_range):
            multiargs.append((FILENAME,iter1,iter2,k,k))
        results.extend(pool.starmap(FUN, multiargs))
    
    # MLEM2_OnlyK_STAT 用
    elif FUN == MLEM2_OnlyK_STAT :
        k_range = kargs['k'] if 'k' in kargs else range(2,11)
        #for k in k_range:
        for FILENAME, iter1, iter2, k in product(FILENAMES, range(1,11), range(1,11), k_range):
            multiargs.append((FILENAME,iter1,iter2,k))
        results.extend(pool.starmap(FUN, multiargs))
            
    # MLEM2_RuleClusteringByRandom_STAT 用
    elif FUN == MLEM2_RuleClusteringByRandom_STAT :
        k_range = kargs['k'] if 'k' in kargs else range(2,11)
        #for k in k_range:
        for FILENAME, iter1, iter2, k in product(FILENAMES, range(1,11), range(1,11), k_range):
            multiargs.append((FILENAME,iter1,iter2,k))
        results.extend(pool.starmap(FUN, multiargs))
            
    # MLEM2_RuleClusteringBySameCondition_STAT 用
    elif FUN == MLEM2_RuleClusteringBySameCondition_STAT :
        k_range = kargs['k'] if 'k' in kargs else range(2,11)
        #for k in k_range:
        for FILENAME, iter1, iter2, k in product(FILENAMES, range(1,11), range(1,11), k_range):
            multiargs.append((FILENAME,iter1,iter2,k))
        results.extend(pool.starmap(FUN, multiargs))
            
    # その他
    else :
        print("I dont' know the function.")        
  
    #results = pool.starmap(FUN, multiargs)
    return(results)
      
# ========================================
# main
# ========================================
if __name__ == "__main__":

    # set data and k
    #FILENAMES = ['adult_cleansing2']
    #FILENAMES = ['default_cleansing']
    FILENAMES = ['hayes-roth']
    #FILENAMES = ['german_credit_categorical']
    #FILENAMES = ['nursery']

    #k_range = range(5,50,5)
    #k_range = range(2,20,2)    
    k_range = range(2,11,1)
    #k_range = range(2,20,2)    
    #k_range = range(3,30,3)
    
    FUNS = [MLEM2_STAT,
            MLEM2_OnlyK_STAT,
            #MLEM2_RuleClusteringBySim_LERS,
            MLEM2_RuleClusteringByRandom_STAT,
            MLEM2_RuleClusteringBySameCondition_STAT,
            #MLEM2_RuleClusteringByConsistentSim_LERS,
            #MLEM2_RuleClusteringByConsistentSimExceptMRule_LERS,
            MLEM2_RuleClusteringByConsistentTimesSimExceptMRule_STAT,
            MLEM2_RuleClusteringBySimExceptMRule_STAT,
            MLEM2_RuleClusteringByConsistentExceptMRule_STAT]

    # 並列実行
    proc=48
    freeze_support()
    
    for FUN in FUNS :
        results = multi_main(proc, FILENAMES, FUN, k = k_range)
    
    print("DONE")
    
    