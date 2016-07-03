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
import logging
import importlib
import mlem2
importlib.reload(mlem2)  
import LERS
importlib.reload(LERS) 
import clustering
importlib.reload(clustering) 

# ====================================
# MLEM2 - LERS による正答率実験
# ====================================
def MLEM2_LERS(FILENAME, iter1, iter2) :

    # rule induction
    fullpath_filename = '/data/uci/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2)

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
    accuracy = accuracy_score(decision_class, predictions)

    #print('{FILENAME} : {iter1} {iter2}'.format(FILENAME=FILENAME,iter1=iter1,iter2=iter2))
    #logging.info('MLEM2_LERS,1,{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,iter1=iter1,iter2=iter2,acc=accuracy))
    savepath = '/data/uci/'+FILENAME+'/MLEM2_LERS.csv'
    with open(savepath, "a") as f :
        f.writelines('MLEM2_LERS,1,{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,iter1=iter1,iter2=iter2,acc=accuracy)+"\n")

    return(accuracy)

# ====================================
# MLEM2 - k以上のルールだけにする - LERS による正答率実験
# ====================================
def MLEM2_OnlyK_LERS(FILENAME, iter1, iter2, k) :

    print("START iter1 iter2 k : " + str(iter1) + "," + str(iter2) + "," + str(k))
    # rule induction
    fullpath_filename = '/data/uci/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2)

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename)

    # only-k rule filter
    fullpath_filename = '/data/uci/'+FILENAME+'/rules_onlyK/'+'rules-'+str(k)+'_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else [r for r in rules if len(r.getSupport()) >= k]

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
    accuracy = accuracy_score(decision_class, predictions)

    #print('{FILENAME} : {iter1} {iter2}'.format(FILENAME=FILENAME,iter1=iter1,iter2=iter2))
    #logging.info('MLEM2_OnlyK_LERS,{k},{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,k=k,iter1=iter1,iter2=iter2,acc=accuracy))
    savepath = '/data/uci/'+FILENAME+'/MLEM2_OnlyK_LERS.csv'
    with open(savepath, "a") as f :
        f.writelines('MLEM2_OnlyK_LERS,{k},{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,k=k,iter1=iter1,iter2=iter2,acc=accuracy)+"\n")

    #print("END iter1 iter2 k : " + str(iter1) + "," + str(iter2) + "," + str(k))
    return(accuracy)

# ====================================
# MLEM2 - RuleClustering by SameCondition+Except M Support - LERS による正答率実験
# ====================================
def MLEM2_RuleClusteringByConsistentSimExceptMRule_LERS(FILENAME, iter1, iter2, k, m) :
    # rule induction
    fullpath_filename = '/data/uci/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2) 

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename) 

    # rule clustering
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table = mlem2.getDecisionTable(filepath)
    colnames = mlem2.getColNames(decision_table)
    
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)
    list_judgeNominal = mlem2.getJudgeNominal(decision_table, list_nominal)

    fullpath_filename = '/data/uci/'+FILENAME+'/rules_cluster_consistent_sim_except_mrule/'+'rules-'+str(k)+'_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else clustering.getRuleClusteringByConsistentSimilarityExceptMRule(rules, colnames, list_judgeNominal, k=k, m=m)

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
    accuracy = accuracy_score(decision_class, predictions)
    
    #print('{FILENAME} : {iter1} {iter2}'.format(FILENAME=FILENAME,iter1=iter1,iter2=iter2))    
    #logging.info('MLEM2_RuleClusteringByConsistentSimExceptMRule_LERS,{k},{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,k=k,iter1=iter1,iter2=iter2,acc=accuracy))
    savepath = '/data/uci/'+FILENAME+'/MLEM2_RuleClusteringByConsistentSimExceptMRule_LERS.csv'
    with open(savepath, "a") as f :
        f.writelines('MLEM2_RuleClusteringByConsistentSimExceptMRule_LERS,{k},{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,k=k,iter1=iter1,iter2=iter2,acc=accuracy)+"\n")
    
    return(accuracy)

# ====================================
# MLEM2 - RuleClustering by Consistent+Sim - LERS による正答率実験
# ====================================
def MLEM2_RuleClusteringByConsistentSim_LERS(FILENAME, iter1, iter2, k) :
          
    # rule induction
    fullpath_filename = '/data/uci/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2) 

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename) 

    # rule clustering
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table = mlem2.getDecisionTable(filepath)
    colnames = mlem2.getColNames(decision_table)
    
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)
    list_judgeNominal = mlem2.getJudgeNominal(decision_table, list_nominal)

    fullpath_filename = '/data/uci/'+FILENAME+'/rules_cluster_consistent_sim/'+'rules-'+str(k)+'_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else clustering.getRuleClusteringByConsistentSimilarity(rules, colnames, list_judgeNominal, k=k)

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
    accuracy = accuracy_score(decision_class, predictions)
    
    #print('{FILENAME} : {iter1} {iter2}'.format(FILENAME=FILENAME,iter1=iter1,iter2=iter2))    
    #logging.info('MLEM2_RuleClusteringByConsistentSim_LERS,{k},{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,k=k,iter1=iter1,iter2=iter2,acc=accuracy))
    savepath = '/data/uci/'+FILENAME+'/MLEM2_RuleClusteringByConsistentSim_LERS.csv'
    with open(savepath, "a") as f :
        f.writelines('MLEM2_RuleClusteringByConsistentSim_LERS,{k},{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,k=k,iter1=iter1,iter2=iter2,acc=accuracy)+"\n")
      
    return(accuracy)

# ====================================
# MLEM2 - RuleClustering by Sim - LERS による正答率実験
# ====================================
def MLEM2_RuleClusteringBySim_LERS(FILENAME, iter1, iter2, k) :
          
    # rule induction
    fullpath_filename = '/data/uci/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2) 

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename) 

    # rule clustering
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table = mlem2.getDecisionTable(filepath)
    colnames = mlem2.getColNames(decision_table)
    
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)
    list_judgeNominal = mlem2.getJudgeNominal(decision_table, list_nominal)

    fullpath_filename = '/data/uci/'+FILENAME+'/rules_cluster_sim/'+'rules-'+str(k)+'_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else clustering.getRuleClusteringBySimilarity(rules, colnames, list_judgeNominal, k=k)

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
    accuracy = accuracy_score(decision_class, predictions)
    
    #print('{FILENAME} : {iter1} {iter2}'.format(FILENAME=FILENAME,iter1=iter1,iter2=iter2))    
    #logging.info('MLEM2_RuleClusteringBySim_LERS,{k},{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,k=k,iter1=iter1,iter2=iter2,acc=accuracy))
    savepath = '/data/uci/'+FILENAME+'/MLEM2_RuleClusteringBySim_LERS.csv'
    with open(savepath, "a") as f :
        f.writelines('MLEM2_RuleClusteringBySim_LERS,{k},{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,k=k,iter1=iter1,iter2=iter2,acc=accuracy)+"\n")

    return(accuracy)

# ====================================
# MLEM2 - RuleClustering by Random - LERS による正答率実験
# ====================================
def MLEM2_RuleClusteringByRandom_LERS(FILENAME, iter1, iter2, k) :
          
    # rule induction
    fullpath_filename = '/data/uci/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2) 

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename) 

    # rule clustering
    fullpath_filename = '/data/uci/'+FILENAME+'/rules_cluster_random/'+'rules-'+str(k)+'_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else clustering.getRuleClusteringByRandom(rules, k=k)

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
    accuracy = accuracy_score(decision_class, predictions)
    
    #logging.info('MLEM2_RuleClusteringByRandom_LERS,{k},{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,k=k,iter1=iter1,iter2=iter2,acc=accuracy))
    savepath = '/data/uci/'+FILENAME+'/MLEM2_RuleClusteringByRandom_LERS.csv'
    with open(savepath, "a") as f :
        f.writelines('MLEM2_RuleClusteringByRandom_LERS,{k},{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,k=k,iter1=iter1,iter2=iter2,acc=accuracy)+"\n")

    return(accuracy)

# ====================================
# MLEM2 - RuleClustering by SameCondition - LERS による正答率実験
# ====================================
def MLEM2_RuleClusteringBySameCondition_LERS(FILENAME, iter1, iter2, k) :
          
    # rule induction
    fullpath_filename = '/data/uci/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2) 

    # rule save
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename) 

    # rule clustering
    fullpath_filename = '/data/uci/'+FILENAME+'/rules_cluster_same_condition/'+'rules-'+str(k)+'_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else clustering.getRuleClusteringBySameCondition(rules, k=k)

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
    accuracy = accuracy_score(decision_class, predictions)
    
    #logging.info('MLEM2_RuleClusteringBySameCondition_LERS,{k},{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,k=k,iter1=iter1,iter2=iter2,acc=accuracy))
    savepath = '/data/uci/'+FILENAME+'/MLEM2_RuleClusteringBySameCondition_LERS.csv'
    with open(savepath, "a") as f :
        f.writelines('MLEM2_RuleClusteringBySameCondition_LERS,{k},{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,k=k,iter1=iter1,iter2=iter2,acc=accuracy)+"\n")
    
    return(accuracy)

# ========================================
# listの平均と分散を求める
# ========================================
def getEvalMeanVar(result):
    ans = '{mean}±{std}'.format(mean=('%.3f' % round(np.mean(results),3)), std=('%.3f' % round(np.std(results),3)))
    return(ans)

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

    # MLEM2_LERS 用
    if FUN == MLEM2_LERS :
        for FILENAME, iter1, iter2 in product(FILENAMES, range(1,11), range(1,11)):            
            multiargs.append((FILENAME,iter1,iter2))
        results = pool.starmap(FUN, multiargs)
        
    # MLEM2_RuleClusteringByConsistentSimExceptMRule_LERS 用
    elif FUN == MLEM2_RuleClusteringByConsistentSimExceptMRule_LERS :
        k_range = kargs['k'] if 'k' in kargs else range(2,11)
        #for k in k_range:
        for FILENAME, iter1, iter2, k in product(FILENAMES, range(1,11), range(1,11), k_range):
            multiargs.append((FILENAME,iter1,iter2,k,k))
        results.extend(pool.starmap(FUN, multiargs))
    
    # MLEM2_OnlyK_LERS 用
    elif FUN == MLEM2_OnlyK_LERS :
        k_range = kargs['k'] if 'k' in kargs else range(2,11)
        #for k in k_range:
        for FILENAME, iter1, iter2, k in product(FILENAMES, range(1,11), range(1,11), k_range):
            multiargs.append((FILENAME,iter1,iter2,k))
        results.extend(pool.starmap(FUN, multiargs))
            
    # MLEM2_RuleClusteringByConsistentSim_LERS 用
    elif FUN == MLEM2_RuleClusteringByConsistentSim_LERS :
        k_range = kargs['k'] if 'k' in kargs else range(2,11)
        #for k in k_range:
        for FILENAME, iter1, iter2, k in product(FILENAMES, range(1,11), range(1,11), k_range):
            multiargs.append((FILENAME,iter1,iter2,k))
        results.extend(pool.starmap(FUN, multiargs))
            
    # MLEM2_RuleClusteringBySim_LERS 用
    elif FUN == MLEM2_RuleClusteringBySim_LERS :
        k_range = kargs['k'] if 'k' in kargs else range(2,11)
        #for k in k_range:
        for FILENAME, iter1, iter2, k in product(FILENAMES, range(1,11), range(1,11), k_range):
            multiargs.append((FILENAME,iter1,iter2,k))
        results.extend(pool.starmap(FUN, multiargs))
            
    # MLEM2_RuleClusteringByRandom_LERS 用
    elif FUN == MLEM2_RuleClusteringByRandom_LERS :
        k_range = kargs['k'] if 'k' in kargs else range(2,11)
        #for k in k_range:
        for FILENAME, iter1, iter2, k in product(FILENAMES, range(1,11), range(1,11), k_range):
            multiargs.append((FILENAME,iter1,iter2,k))
        results.extend(pool.starmap(FUN, multiargs))
            
    # MLEM2_RuleClusteringBySameCondition_LERS 用
    elif FUN == MLEM2_RuleClusteringBySameCondition_LERS :
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
    FILENAMES = ['nursery']
    k_range = range(3,30,3)
    
    # シングルプロセスで実行
    #for FILENAME, iter1, iter2 in product(FILENAMES, range(1,11), range(1,11)):    
    #    print('{filename} {i1} {i2}'.format(filename=FILENAME, i1=iter1, i2=iter2))
    #    print(MLEM2_LERS(FILENAME, iter1, iter2))

    # 実行したい実験関数
    #FUN = MLEM2_LERS
    #FUN = MLEM2_OnlyK_LERS
    #FUN = MLEM2_RuleClusteringBySim_LERS
    FUN = MLEM2_RuleClusteringByRandom_LERS
    #FUN = MLEM2_RuleClusteringBySameCondition_LERS
    #FUN = MLEM2_RuleClusteringByConsistentSim_LERS
    #FUN = MLEM2_RuleClusteringByConsistentSimExceptMRule_LERS

    #FUNS = [MLEM2_LERS,
    #        MLEM2_OnlyK_LERS,
    #        MLEM2_RuleClusteringBySim_LERS,
    #        MLEM2_RuleClusteringByRandom_LERS,
    #        MLEM2_RuleClusteringBySameCondition_LERS,
    #        MLEM2_RuleClusteringByConsistentSim_LERS,
    #        MLEM2_RuleClusteringByConsistentSimExceptMRule_LERS]

    # 並列実行
    proc=48
    freeze_support()
    
    #for FUN in FUNS :
    results = multi_main(proc, FILENAMES, FUN, k = k_range)
    # 平均と分散
    print(getEvalMeanVar(results))
    
    # 保存する
    #saveResults(results, "/data/uci/hayes-roth/accuracy.txt")
