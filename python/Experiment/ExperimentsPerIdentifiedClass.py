# coding: utf-8
# python 3.5
from itertools import product
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
# MLEM2 による特定化実験
# ====================================
def MLEM2_Identified(FILENAME, iter1, iter2, p) :
          
    # rule induction
    fullpath_filename =DIR_UCI+'/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2) 

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename) 

    # PerIdentifiedClass を求める
    ans = mlem2.getPerIdentifiedClass(rules, p)
        
    # save
    savepath = DIR_UCI+'/'+FILENAME+'/Identify_MLEM2.csv'
    with open(savepath, "a") as f :
        f.writelines('Identify_MLEM2,1,{p},{FILENAME},{iter1},{iter2},{ans}'.format(FILENAME=FILENAME,p=p,iter1=iter1,iter2=iter2,ans=ans)+"\n")
    
    return(ans)

# ====================================
# MLEM2 - k以上のルールだけにする - LERS による特定化実験
# ====================================
def MLEM2_OnlyK_Identified(FILENAME, iter1, iter2, k, p) :
          
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

    # PerIdentifiedClass を求める
    ans = mlem2.getPerIdentifiedClass(rules, p)
        
    # save
    savepath = DIR_UCI+'/'+FILENAME+'/Identify_MLEM2_OnlyK.csv'
    with open(savepath, "a") as f :
        f.writelines('Identify_MLEM2_OnlyK,{k},{p},{FILENAME},{iter1},{iter2},{ans}'.format(FILENAME=FILENAME,k=k,p=p,iter1=iter1,iter2=iter2,ans=ans)+"\n")
    
    return(ans)

# ====================================
# MLEM2 - RuleClustering by ConsistentSim+Except M Support - LERS による正答率実験
# ====================================
def MLEM2_RuleClusteringByConsistentSimExceptMRule_Identified(FILENAME, iter1, iter2, k, m, p) :
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

    fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules_cluster_consistent_sim_except_mrule/'+'rules-'+str(k)+'_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else clustering.getRuleClusteringByConsistentSimilarityExceptMRule(rules, colnames, list_judgeNominal, k=k, m=m)

    # PerIdentifiedClass を求める
    ans = mlem2.getPerIdentifiedClass(rules, p)
        
    # save
    savepath = DIR_UCI+'/'+FILENAME+'/Identify_MLEM2_RuleClusteringByConsistentSimExceptMRule.csv'
    with open(savepath, "a") as f :
        f.writelines('Identify_MLEM2_RuleClusteringByConsistentSimExceptMRule,{k},{p},{FILENAME},{iter1},{iter2},{ans}'.format(FILENAME=FILENAME,k=k,p=p,iter1=iter1,iter2=iter2,ans=ans)+"\n")
    
    return(ans)

# ====================================
# MLEM2 - RuleClustering by Consistent ×　Sim Except M Support - LERS による正答率実験
# ====================================
def MLEM2_RuleClusteringByConsistentTimesSimExceptMRule_Identified(FILENAME, iter1, iter2, k, m, p) :
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

    # PerIdentifiedClass を求める
    ans = mlem2.getPerIdentifiedClass(rules, p)
        
    # save
    savepath = DIR_UCI+'/'+FILENAME+'/Identify_MLEM2_RuleClusteringByConsistentTimesSimExceptMRule.csv'
    with open(savepath, "a") as f :
        f.writelines('Identify_MLEM2_RuleClusteringByConsistentTimesSimExceptMRule,{k},{p},{FILENAME},{iter1},{iter2},{ans}'.format(FILENAME=FILENAME,k=k,p=p,iter1=iter1,iter2=iter2,ans=ans)+"\n")
    
    return(ans)

# ====================================
# MLEM2 - RuleClustering by Sim Except M Support - Identified 実験
# ====================================
def MLEM2_RuleClusteringBySimExceptMRule_Identified(FILENAME, iter1, iter2, k, m, p) :
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

    # PerIdentifiedClass を求める
    ans = mlem2.getPerIdentifiedClass(rules, p)
        
    # save
    savepath = DIR_UCI+'/'+FILENAME+'/Identify_MLEM2_RuleClusteringBySimExceptMRule.csv'
    with open(savepath, "a") as f :
        f.writelines('Identify_MLEM2_RuleClusteringBySimExceptMRule,{k},{p},{FILENAME},{iter1},{iter2},{ans}'.format(FILENAME=FILENAME,k=k,p=p,iter1=iter1,iter2=iter2,ans=ans)+"\n")
    
    return(ans)

# ====================================
# MLEM2 - RuleClustering by Consistency Except M Support - Identified 実験
# ====================================
def MLEM2_RuleClusteringByConsistentExceptMRule_Identified(FILENAME, iter1, iter2, k, m, p) :
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

    # PerIdentifiedClass を求める
    ans = mlem2.getPerIdentifiedClass(rules, p)
        
    # save
    savepath = DIR_UCI+'/'+FILENAME+'/Identify_MLEM2_RuleClusteringByConsistentExceptMRule.csv'
    with open(savepath, "a") as f :
        f.writelines('Identify_MLEM2_RuleClusteringByConsistentExceptMRule,{k},{p},{FILENAME},{iter1},{iter2},{ans}'.format(FILENAME=FILENAME,k=k,p=p,iter1=iter1,iter2=iter2,ans=ans)+"\n")
    
    return(ans)

# ====================================
# MLEM2 - RuleClustering by Consistent+Sim - LERS による正答率実験
# ====================================
def MLEM2_RuleClusteringByConsistentSim_Identified(FILENAME, iter1, iter2, k, p) :
          
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

    fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules_cluster_consistent_sim/'+'rules-'+str(k)+'_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else clustering.getRuleClusteringByConsistentSimilarity(rules, colnames, list_judgeNominal, k=k)

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename) 

    # PerIdentifiedClass を求める
    ans = mlem2.getPerIdentifiedClass(rules, p)
        
    # save
    savepath = DIR_UCI+'/'+FILENAME+'/Identify_MLEM2_RuleClusteringByConsistentSim.csv'
    with open(savepath, "a") as f :
        f.writelines('Identify_MLEM2_RuleClusteringByConsistentSim,{k},{p},{FILENAME},{iter1},{iter2},{ans}'.format(FILENAME=FILENAME,k=k,p=p,iter1=iter1,iter2=iter2,ans=ans)+"\n")
    
    return(ans)


# ====================================
# MLEM2 - RuleClustering by Random による正答率実験
# ====================================
def MLEM2_RuleClusteringByRandom_Identified(FILENAME, iter1, iter2, k, p) :
          
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

    # PerIdentifiedClass を求める
    ans = mlem2.getPerIdentifiedClass(rules, p)
        
    # save
    savepath = DIR_UCI+'/'+FILENAME+'/Identify_MLEM2_Random.csv'
    with open(savepath, "a") as f :
        f.writelines('Identify_MLEM2_Random,{k},{p},{FILENAME},{iter1},{iter2},{ans}'.format(FILENAME=FILENAME,k=k,p=p,iter1=iter1,iter2=iter2,ans=ans)+"\n")
    
    return(ans)

# ====================================
# MLEM2 - RuleClustering by SameCondition - LERS による正答率実験
# ====================================
def MLEM2_RuleClusteringBySameCondition_Identified(FILENAME, iter1, iter2, k, p) :
          
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

    # PerIdentifiedClass を求める
    ans = mlem2.getPerIdentifiedClass(rules, p)
        
    # save
    savepath = DIR_UCI+'/'+FILENAME+'/Identify_MLEM2_SameCondition.csv'
    with open(savepath, "a") as f :
        f.writelines('Identify_MLEM2_SameCondition,{k},{p},{FILENAME},{iter1},{iter2},{ans}'.format(FILENAME=FILENAME,k=k,p=p,iter1=iter1,iter2=iter2,ans=ans)+"\n")
    
    return(ans)
    
# ========================================
# listの平均と分散を求める
# ========================================
def getEvalMeanVar(result):
    ans = '{mean}±{std}'.format(mean=('%.3f' % round(np.mean(results),3)), std=('%.3f' % round(np.std(results),3)))
    return(ans)

#
# ========================================
# multi に実行する
# ========================================
def multi_main(proc, FILENAMES, FUN, **kargs):
    pool = Pool(proc)
    results = []
    multiargs = []
    p_range = range(1,4)

    # MLEM2_LERS 用
    if FUN == MLEM2_Identified :
        for FILENAME, iter1, iter2, p in product(FILENAMES, range(1,11), range(1,11), p_range):            
            multiargs.append((FILENAME,iter1,iter2,p))
        results = pool.starmap(FUN, multiargs)
        
    # MLEM2_RuleClusteringByConsistentSimExceptMRule_Identified 用
    elif FUN == MLEM2_RuleClusteringByConsistentSimExceptMRule_Identified :
        k_range = kargs['k'] if 'k' in kargs else range(2,11)
        for FILENAME, iter1, iter2, k, p in product(FILENAMES, range(1,11), range(1,11), k_range, p_range):
            multiargs.append((FILENAME,iter1,iter2,k,k,p))
        results.extend(pool.starmap(FUN, multiargs))
    
    # MLEM2_RuleClusteringByConsistentTimesSimExceptMRule_Identified 用
    elif FUN == MLEM2_RuleClusteringByConsistentTimesSimExceptMRule_Identified :
        k_range = kargs['k'] if 'k' in kargs else range(2,11)
        for FILENAME, iter1, iter2, k, p in product(FILENAMES, range(1,11), range(1,11), k_range, p_range):
            multiargs.append((FILENAME,iter1,iter2,k,k,p))
        results.extend(pool.starmap(FUN, multiargs))
            
    # MLEM2_RuleClusteringBySimExceptMRule_Identified 用
    elif FUN == MLEM2_RuleClusteringBySimExceptMRule_Identified :
        k_range = kargs['k'] if 'k' in kargs else range(2,11)
        #for k in k_range:
        for FILENAME, iter1, iter2, k, p in product(FILENAMES, range(1,11), range(1,11), k_range, p_range):
            multiargs.append((FILENAME,iter1,iter2,k,k,p))
        results.extend(pool.starmap(FUN, multiargs))
    
    # MLEM2_RuleClusteringByConsistentExceptMRule_Identified 用
    elif FUN == MLEM2_RuleClusteringByConsistentExceptMRule_Identified :
        k_range = kargs['k'] if 'k' in kargs else range(2,11)
        #for k in k_range:
        for FILENAME, iter1, iter2, k, p in product(FILENAMES, range(1,11), range(1,11), k_range, p_range):
            multiargs.append((FILENAME,iter1,iter2,k,k,p))
        results.extend(pool.starmap(FUN, multiargs))
    
    # MLEM2_OnlyK_Identified 用
    elif FUN == MLEM2_OnlyK_Identified :
        k_range = kargs['k'] if 'k' in kargs else range(2,11)
        for FILENAME, iter1, iter2, k, p in product(FILENAMES, range(1,11), range(1,11), k_range, p_range):            
            multiargs.append((FILENAME,iter1,iter2,k,p))
        results = pool.starmap(FUN, multiargs)
        
    # MLEM2_RuleClusteringByConsistentSim_Identified 用
    elif FUN == MLEM2_RuleClusteringByConsistentSim_Identified :
        k_range = kargs['k'] if 'k' in kargs else range(2,11)
        for FILENAME, iter1, iter2, k, p in product(FILENAMES, range(1,11), range(1,11), k_range, p_range):
            multiargs.append((FILENAME,iter1,iter2,k,p))
        results.extend(pool.starmap(FUN, multiargs))

    # MLEM2_RuleClusteringByRandom_Identified 用
    elif FUN == MLEM2_RuleClusteringByRandom_Identified :
        k_range = kargs['k'] if 'k' in kargs else range(2,11)
        for FILENAME, iter1, iter2, k, p in product(FILENAMES, range(1,11), range(1,11), k_range, p_range):
            multiargs.append((FILENAME,iter1,iter2,k,p))
        results.extend(pool.starmap(FUN, multiargs))
            
    # MLEM2_RuleClusteringBySameCondition_Identified  用
    elif FUN == MLEM2_RuleClusteringBySameCondition_Identified :
        k_range = kargs['k'] if 'k' in kargs else range(2,11)
        for FILENAME, iter1, iter2, k, p in product(FILENAMES, range(1,11), range(1,11), k_range, p_range):
            multiargs.append((FILENAME,iter1,iter2,k,p))
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
    FILENAMES = ['default_cleansing']
    #FILENAMES = ['hayes-roth']
    #FILENAMES = ['german_credit_categorical']
    #FILENAMES = ['nursery']

    #k_range = range(5,45,5)
    k_range = range(5,50,5)    
    #k_range = range(2,11,1)
    #k_range = range(2,20,2)
    #k_range = range(3,30,3)
    
    # シングルプロセスで実行
    #for FILENAME, iter1, iter2 in product(FILENAMES, range(1,11), range(1,11)):    
    #    print('{filename} {i1} {i2}'.format(filename=FILENAME, i1=iter1, i2=iter2))
    #    print(MLEM2_LERS(FILENAME, iter1, iter2))

    # 実行したい実験関数
    #FUN = MLEM2_Identified
    #FUN = MLEM2_OnlyK_Identified
    #FUN = MLEM2_RuleClusteringByRandom_Identified
    #FUN = MLEM2_RuleClusteringBySameCondition_Identified
    #FUN = MLEM2_RuleClusteringByConsistentSim_Identified
    #FUN = MLEM2_RuleClusteringByConsistentSimExceptMRule_Identified
    #FUN = MLEM2_RuleClusteringByConsistentTimesSimExceptMRule_Identified
    #FUN = MLEM2_RuleClusteringBySimExceptMRule_Identified
    #FUN = MLEM2_RuleClusteringByConsistentExceptMRule_Identified

    FUNS = [#MLEM2_Identified,
            MLEM2_OnlyK_Identified,
            MLEM2_RuleClusteringByRandom_Identified,
            MLEM2_RuleClusteringBySameCondition_Identified,
            MLEM2_RuleClusteringByConsistentSim_Identified,
            MLEM2_RuleClusteringByConsistentTimesSimExceptMRule_Identified,
            MLEM2_RuleClusteringBySimExceptMRule_Identified,
            MLEM2_RuleClusteringByConsistentExceptMRule_Identified]

    # 並列実行
    proc=48
    freeze_support()
    
    for FUN in FUNS :
        results = multi_main(proc, FILENAMES, FUN, k = k_range)

    # 平均と分散
    print(getEvalMeanVar(results))  
