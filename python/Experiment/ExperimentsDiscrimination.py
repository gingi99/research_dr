# coding: utf-8
# python 3.5
from itertools import product
from sklearn.metrics import accuracy_score
from datetime import datetime
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
    print(datetime.now().strftime('%Y/%m/%d %H:%M:%S')+' '+FILENAME+' '+str(iter1)+' '+str(iter2)+' '+DELFUN.__name__+' '+'-'.join(ATTRIBUTES)+' '+"START")    
    
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
    print(datetime.now().strftime('%Y/%m/%d %H:%M:%S')+' '+FILENAME+' '+str(iter1)+' '+str(iter2)+' '+DELFUN.__name__+' '+'-'.join(ATTRIBUTES)+' '+"RULES")    
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
    print(datetime.now().strftime('%Y/%m/%d %H:%M:%S')+' '+FILENAME+' '+str(iter1)+' '+str(iter2)+' '+DELFUN.__name__+' '+'-'.join(ATTRIBUTES)+' '+"END")    
    return(0)

# ====================================
# MLEM2 - 基本条件の削除 - LERS による正答率実験
# ====================================
def MLEM2_delERule_LERS(FILENAME, iter1, iter2, DELFUN, ATTRIBUTE_VALUE) :
    print(datetime.now().strftime('%Y/%m/%d %H:%M:%S')+' '+FILENAME+' '+str(iter1)+' '+str(iter2)+' '+DELFUN.__name__+' '+strAttributeValue(ATTRIBUTE_VALUE)+' '+"START")    
    
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
    print(datetime.now().strftime('%Y/%m/%d %H:%M:%S')+' '+FILENAME+' '+str(iter1)+' '+str(iter2)+' '+DELFUN.__name__+' '+strAttributeValue(ATTRIBUTE_VALUE)+' '+"RULES")    
    
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
        f.writelines('MLEM2_delERule_LERS,{DELFUN},{FILENAME},{ATTRIBUTE_VALUE},{iter1},{iter2},{acc},{num},{mean_length},{mean_support},{mean_conf}'.format(DELFUN=DELFUN.__name__,FILENAME=FILENAME,ATTRIBUTE_VALUE=strAttributeValue(ATTRIBUTE_VALUE),iter1=iter1,iter2=iter2,acc=accuracy,num=num,mean_length=mean_length,mean_support=mean_support,mean_conf=mean_conf)+"\n")

    print(datetime.now().strftime('%Y/%m/%d %H:%M:%S')+' '+FILENAME+' '+str(iter1)+' '+str(iter2)+' '+DELFUN.__name__+' '+strAttributeValue(ATTRIBUTE_VALUE)+' '+"END")    
    return(0)

# ====================================
# MLEM2 - Alpha差別ルールの処理 - LERS による正答率実験
# ====================================
def MLEM2_delEAlphaRule_LERS(FILENAME, iter1, iter2, DELFUN, ATTRIBUTE_VALUE, alpha) :
    print(datetime.now().strftime('%Y/%m/%d %H:%M:%S')+' '+FILENAME+' '+str(iter1)+' '+str(iter2)+' '+DELFUN.__name__+' '+strAttributeValue(ATTRIBUTE_VALUE)+' '+str(alpha)+' '+"START")    
    
    # rule induction and rule save
    fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
    rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2)
    if not os.path.isfile(fullpath_filename): mlem2.savePickleRules(rules, fullpath_filename)

    # train data setup
    decision_table_train, decision_class = getData(FILENAME, iter1, iter2, T = "train")
    list_judgeNominal = getJudgeNominal(decision_table_train, FILENAME)
    
    # alpha差別的なルールの基本条件削除 or ルールを削除
    for attr in ATTRIBUTE_VALUE:
        for e in ATTRIBUTE_VALUE[attr]:
            rules = DELFUN(rules, attr, e, decision_table_train, list_judgeNominal, alpha)
    print(datetime.now().strftime('%Y/%m/%d %H:%M:%S')+' '+FILENAME+' '+str(iter1)+' '+str(iter2)+' '+DELFUN.__name__+' '+strAttributeValue(ATTRIBUTE_VALUE)+' '+str(alpha)+' '+"RULES")    
    
    # test data setup
    decision_table_test, decision_class = getData(FILENAME, iter1, iter2, T = "test")
    list_judgeNominal = getJudgeNominal(decision_table_test, FILENAME)

    # predict by LERS
    predictions = LERS.predictByLERS(rules, decision_table_test, list_judgeNominal)

    # 正答率を求める
    accuracy = accuracy_score(decision_class, predictions)
    # rules の数を求める
    num = len(rules)
    # 平均の長さを求める
    mean_length = mlem2.getMeanLength(rules)
    # 平均支持度と平均確信度を求める
    list_judgeNominal = getJudgeNominal(decision_table_train, FILENAME)
    mean_support, mean_conf = LERS.getSupportConfidenceRules(rules, decision_table_train, list_judgeNominal)
    
    # ファイルにsave
    savepath = DIR_UCI+'/'+FILENAME+'/fairness/02_alpha_preserve/MLEM2_delEAlphaRule_LERS.csv'
    with open(savepath, "a") as f :
        f.writelines('MLEM2_delEAlphaRule_LERS,{DELFUN},{FILENAME},{ATTRIBUTE_VALUE},{alpha},{iter1},{iter2},{acc},{num},{mean_length},{mean_support},{mean_conf}'.format(DELFUN=DELFUN.__name__,FILENAME=FILENAME,ATTRIBUTE_VALUE=strAttributeValue(ATTRIBUTE_VALUE),alpha=alpha,iter1=iter1,iter2=iter2,acc=accuracy,num=num,mean_length=mean_length,mean_support=mean_support,mean_conf=mean_conf)+"\n")
    print(datetime.now().strftime('%Y/%m/%d %H:%M:%S')+' '+FILENAME+' '+str(iter1)+' '+str(iter2)+' '+DELFUN.__name__+' '+strAttributeValue(ATTRIBUTE_VALUE)+' '+str(alpha)+' '+"END")    

    return(0)

# ========================================
# multi に実行する
# ========================================
def multi_main(n_jobs, FILENAME, FUN, **kargs):
    if FUN == MLEM2_delAttrRule_LERS :
        joblib.Parallel(n_jobs=n_jobs)(joblib.delayed(FUN)(FILENAME, iter1, iter2, delfun, attributes) for (iter1,iter2,delfun,attributes) in product(range(1,11), range(1,11), kargs["DELFUNS"], kargs["ATTRIBUTES"]))
    elif FUN == MLEM2_delERule_LERS :
        joblib.Parallel(n_jobs=n_jobs)(joblib.delayed(FUN)(FILENAME, iter1, iter2, delfun, attribute_value) for (iter1,iter2,delfun,attribute_value) in product(range(1,11), range(1,11), kargs["DELFUNS"], kargs["ATTRIBUTE_VALUE"]))
    elif FUN == MLEM2_delEAlphaRule_LERS :
        joblib.Parallel(n_jobs=n_jobs)(joblib.delayed(FUN)(FILENAME, iter1, iter2, delfun, attribute_value, alpha) for (iter1,iter2,delfun,attribute_value,alpha) in product(range(1,11), range(1,11), kargs["DELFUNS"], kargs["ATTRIBUTE_VALUE"], kargs["ALPHA"]))
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
    #DELFUNS = [discrimination.getRulesExcludeAttr, discrimination.getRulesDelAttr]
    #DELFUNS = [discrimination.getRulesExcludeE, discrimination.getRulesDelE]
    #DELFUNS = [discrimination.getAlphaRulesExcludeE, discrimination.getAlphaRulesDelE]
    DELFUNS = {'MLEM2_delAttrRule_LERS' : [discrimination.getRulesExcludeAttr, discrimination.getRulesDelAttr],
               'MLEM2_delERule_LERS' : [discrimination.getRulesExcludeE, discrimination.getRulesDelE],
               'MLEM2_delEAlphaRule_LERS' : [discrimination.getAlphaRulesExcludeE, discrimination.getAlphaRulesDelE],
              }    
    
    # set attribute adult    
    
    # set attribute german
    ATTRIBUTES = {'adult_cleansing2' :
                  [["age"],
                   ["marital_status"],
                   ["race"],
                   ["sex"],
                   ["age", "marital_status", "race", "sex"]
                  ],
                  'german_credit_categorical' :
                  [["Age_years"],
                   ["Foreign_Worker"],
                   ["Sex_Marital_Status"],
                   ["Age_years", "Foreign_Worker", "Sex_Marital_Status"]
                  ]
                 }
                  
    ATTRIBUTE_VALUE = {'adult_cleansing2' : 
                       [{"age" : ["10s", "20s"]},
                        {"marital_status" : ["Divorced"]},
                        {"race" : ["Black"]},
                        {"sex" : ["female"]}
                       ]
                       ,
                       'german_credit_categorical' : 
                       [{"Age_years" : ["[0,25]"], "Foreigh_Worker" : ["2"], "Sex_Marital_Status" : ["4"]},
                        {"Age_years" : ["[0,25]"]},
                        {"Foreigh_Worker" : ["2"]},
                        {"Sex_Marital_Status" : ["1"]},
                        {"Sex_Marital_Status" : ["4"]}
                       ]
                      }

    # set alpha
    ALPHA = [1.2, 1.5, 2.0]

    FUNS = [MLEM2_delAttrRule_LERS,
            MLEM2_delERule_LERS,
            MLEM2_delEAlphaRule_LERS
    ]

    # 並列実行
    n_jobs = 4
    for FUN in FUNS :
        multi_main(n_jobs, FILENAME, FUN, 
                   DELFUNS = DELFUNS[FUN.__name__], 
                   ATTRIBUTES = ATTRIBUTES[FILENAME],
                   ATTRIBUTE_VALUE = ATTRIBUTE_VALUE[FILENAME],
                   ALPHA = ALPHA) 
    print("DONE")
    