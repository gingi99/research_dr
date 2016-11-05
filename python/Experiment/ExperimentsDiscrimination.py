# coding: utf-8
# python 3.5
from itertools import product
from sklearn.metrics import accuracy_score
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
import discrimination
importlib.reload(discrimination) 

# Grobal setting
DIR_UCI = '/mnt/data/uci'

# ====================================
# test data を返す
# ====================================
def getData(FILENAME, iter1, iter2, T = "test") :
    filepath = DIR_UCI+'/'+FILENAME+'/'+FILENAME+'-'+T+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table = mlem2.getDecisionTable(filepath)
    decision_table = decision_table.dropna()
    decision_class = decision_table[decision_table.columns[-1]].values.tolist()
    return(decision_table, decision_class)

# ====================================
# list_judgeNominal を返す
# ====================================
def getJudgeNominal(decision_table, FILENAME) :
    filepath = DIR_UCI+'/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)
    list_judgeNominal = mlem2.getJudgeNominal(decision_table, list_nominal)
    return(list_judgeNominal)

# ====================================
# Attribute Value dict を stringにして返す
# ====================================
def strAttributeValue(ATTRIBUTE_VALUE) :
    list_string = []
    for i in ATTRIBUTE_VALUE :
        list_string.append(i+"-".join(ATTRIBUTE_VALUE[i]))
    return("+".join(list_string))

# ====================================
# MLEM2 - 配慮変数の属性削除 - LERS による正答率実験
# ====================================
def MLEM2_delAttrRule_LERS(FILENAME, iter1, iter2, DELFUN, ATTRIBUTES) :
    
    # rule induction and rule save
    fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2)
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename)

    # test data setup
    decision_table_test, decision_class = getData(FILENAME, iter1, iter2, T = "test")
    list_judgeNominal = getJudgeNominal(decision_table_test, FILENAME)

    # 属性削除
    for attr in ATTRIBUTES:
        rules = DELFUN(rules, attr)

    # predict by LERS
    predictions = LERS.predictByLERS(rules, decision_table_test, list_judgeNominal)

    # 正答率を求める
    accuracy = accuracy_score(decision_class, predictions)
    # rules の数を求める
    num = len(rules)
    # 平均の長さを求める
    mean_length = mlem2.getMeanLength(rules)
    # 平均支持度と平均確信度を求める
    decision_table_train, decision_class = getData(FILENAME, iter1, iter2, T = "train")
    list_judgeNominal = getJudgeNominal(decision_table_train, FILENAME)
    mean_support, mean_conf = LERS.getSupportConfidenceRules(rules, decision_table_train, list_judgeNominal)

    # ファイルにsave
    savepath = DIR_UCI+'/'+FILENAME+'/fairness/01_suppression/MLEM2_delAttrRule_LERS.csv'
    with open(savepath, "a") as f :
        f.writelines('MLEM2_delAttrRule_LERS,{DELFUN},{FILENAME},{ATTRIBUTES},{iter1},{iter2},{acc},{num},{mean_length},{mean_support},{mean_conf}'.format(DELFUN=DELFUN.__name__,FILENAME=FILENAME,ATTRIBUTES='-'.join(ATTRIBUTES),iter1=iter1,iter2=iter2,acc=accuracy,num=num,mean_length=mean_length,mean_support=mean_support,mean_conf=mean_conf)+"\n")

    return(0)

# ====================================
# MLEM2 - 基本条件の削除 - LERS による正答率実験
# ====================================
def MLEM2_delERule_LERS(FILENAME, iter1, iter2, DELFUN, ATTRIBUTE_VALUE) :
    
    # rule induction and rule save
    fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2)
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename)

    # test data setup
    decision_table_test, decision_class = getData(FILENAME, iter1, iter2, T = "test")
    list_judgeNominal = getJudgeNominal(decision_table_test, FILENAME)

    # 基本条件削除
    for attr in ATTRIBUTE_VALUE:
        for e in ATTRIBUTE_VALUE[attr]:
            rules = DELFUN(rules, attr, e)

    # predict by LERS
    predictions = LERS.predictByLERS(rules, decision_table_test, list_judgeNominal)

    # 正答率を求める
    accuracy = accuracy_score(decision_class, predictions)
    # rules の数を求める
    num = len(rules)
    # 平均の長さを求める
    mean_length = mlem2.getMeanLength(rules)
    # 平均支持度と平均確信度を求める
    decision_table_train, decision_class = getData(FILENAME, iter1, iter2, T = "train")
    list_judgeNominal = getJudgeNominal(decision_table_train, FILENAME)
    mean_support, mean_conf = LERS.getSupportConfidenceRules(rules, decision_table_train, list_judgeNominal)
    
    # ファイルにsave
    savepath = DIR_UCI+'/'+FILENAME+'/fairness/01_suppression/MLEM2_delERule_LERS.csv'
    with open(savepath, "a") as f :
        print('MLEM2_delAttrRule_LERS,{DELFUN},{FILENAME},{ATTRIBUTES},{iter1},{iter2},{acc},{num},{mean_length},{mean_support},{mean_conf}'.format(DELFUN=DELFUN.__name__,FILENAME=FILENAME,ATTRIBUTES='-'.join(ATTRIBUTES),iter1=iter1,iter2=iter2,acc=accuracy,num=num,mean_length=mean_length,mean_support=mean_support,mean_conf=mean_conf))
        f.writelines('MLEM2_delAttrRule_LERS,{DELFUN},{FILENAME},{ATTRIBUTES},{iter1},{iter2},{acc},{num},{mean_length},{mean_support},{mean_conf}'.format(DELFUN=DELFUN.__name__,FILENAME=FILENAME,ATTRIBUTES='-'.join(ATTRIBUTES),iter1=iter1,iter2=iter2,acc=accuracy,num=num,mean_length=mean_length,mean_support=mean_support,mean_conf=mean_conf)+"\n")

    return(0)

# ========================================
# multi に実行する
# ========================================
def multi_main(n_jobs, FILENAME, FUN, **kargs):
    if FUN == MLEM2_delAttrRule_LERS :
        joblib.Parallel(n_jobs=n_jobs)(joblib.delayed(FUN)(FILENAME, iter1, iter2, delfun, attributes) for (iter1,iter2,delfun,attributes) in product(range(1,11), range(1,11), kargs["DELFUNS"], kargs['ATTRIBUTES']))
    elif FUN == MLEM2_delERule_LERS :
        joblib.Parallel(n_jobs=n_jobs)(joblib.delayed(FUN)(FILENAME, iter1, iter2, delfun, attribute_value) for (iter1,iter2,delfun,attribute_value) in product(range(1,11), range(1,11), kargs["DELFUNS"], kargs['ATTRIBUTE_VALUE']))
    else :
        print("unknown function")
    return(0)

# ========================================
# main
# ========================================
if __name__ == "__main__":

    # set data and protected attributes
    FILENAME = 'adult_cleansing2'
    FILENAME = 'german_credit_categorical'   
    
    # set function    
    DELFUNS = [discrimination.getRulesExcludeAttr, discrimination.getRulesDelAttr]
    #DELFUNS = [discrimination.getRulesExcludeE, discrimination.getRulesDelE]
    
    # set attribute adult    
    
    # set attribute german
    ATTRIBUTES = [["Foreign_Worker"],
                  ["Age_years", "Foreign_Worker", "Sex_Marital_Status"]]
    ATTRIBUTE_VALUE = [{"Age_years" : ["[0,25]"], "Foreigh_Worker" : ["2"], "Sex_Marital_Status" : ["4"]},
                       {"Age_years" : ["[0,25]"]},
                       {"Foreigh_Worker" : ["2"]},
                       {"Sex_Marital_Status" : ["1"]},
                       {"Sex_Marital_Status" : ["4"]}
                      ]
    #ATTRIBUTES = [list(j) for j in set(tuple(i.keys()) for i in ATTRIBUTE_VALUE)]
    
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
    
    FUNS = [MLEM2_delAttrRule_LERS#,
            #MLEM2_delERule_LERS
    ]

    # 並列実行
    n_jobs = 4
    for FUN in FUNS :
        multi_main(n_jobs, FILENAME, FUN, 
                   DELFUNS = DELFUNS, 
                   ATTRIBUTES = ATTRIBUTES,
                   ATTRIBUTE_VALUE = ATTRIBUTE_VALUE) 
    print("DONE")
    