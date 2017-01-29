# coding: utf-8
import os
import sys
import joblib
import datetime
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.metrics import roc_curve
from sklearn.metrics import auc
from itertools import product
from mlem2 import getNominalList
from mlem2 import getJudgeNominal
from LERS import predictByLERS
from LERS import predictProbaByLERS
# from mlem2 import showRules
# common
sys.path.append("../common/")
from util import loadPickle

# ----------------------------------------
# Rules をロードする
# ----------------------------------------
def loadRules(DIR, FILENAME, ruleset, method, ITER):
    if method == 'A' or method == 'B' :
        fullpath_rules = DIR+'/'+FILENAME+'/'+ruleset+'/'+ITER+'/rules_'+method+'.pkl'
        rules = loadPickle(fullpath_rules)
    elif method == 'both' :
        fullpath_rules_A = DIR+'/'+FILENAME+'/'+ruleset+'/'+ITER+'/rules_A.pkl'
        fullpath_rules_B = DIR+'/'+FILENAME+'/'+ruleset+'/'+ITER+'/rules_B.pkl'
        rules_A = loadPickle(fullpath_rules_A)
        rules_B = loadPickle(fullpath_rules_B)
        rules = rules_A + rules_B
    else :
        print("no method")
    return(rules)

# ========================================
# main
# ========================================
def main(DIR, FILENAME, CLASSES, ruleset, method, ITER) :
    ITER = str(ITER)
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')+' '+FILENAME+' '+method+' '+ITER+" START")

    # load rules
    rules = loadRules(DIR, FILENAME, ruleset, method, ITER)

    # load test and val data
    filepath_test_A = DIR+'/'+FILENAME+'/MIXTURE/dataset/nobias2/'+ITER+'/test_A.tsv'
    df_test_A = pd.read_csv(filepath_test_A, delimiter='\t')
    filepath_val_A = DIR+'/'+FILENAME+'/MIXTURE/dataset/nobias2/'+ITER+'/val_A.tsv'
    df_val_A = pd.read_csv(filepath_val_A, delimiter='\t')
    decision_class_test = df_test_A[df_test_A.columns[-1]].values.tolist()
    decision_class_val = df_val_A[df_val_A.columns[-1]].values.tolist()
    filepath_nominal = DIR+'/'+FILENAME+'/dataset/'+FILENAME+'.nominal'
    list_nominal = getNominalList(filepath_nominal)
    list_judgeNominal = getJudgeNominal(df_test_A, list_nominal)

    # predict by LERS
    predict_test = predictByLERS(rules, df_test_A, list_judgeNominal)
    predict_proba_test = predictProbaByLERS(rules, df_test_A, list_judgeNominal, classes = CLASSES)
    predict_proba_test = np.array(predict_proba_test)[:,0]
    predict_val = predictByLERS(rules, df_val_A, list_judgeNominal)
    predict_proba_val = predictProbaByLERS(rules, df_val_A, list_judgeNominal, classes = CLASSES)
    predict_proba_val = np.array(predict_proba_val)[:,0]

    # 正答率を求める
    result_acc_test = accuracy_score(decision_class_test, predict_test)
    result_acc_val = accuracy_score(decision_class_val, predict_val)

    # AUCを求める
    fpr, tpr, thresholds = roc_curve(decision_class_test, predict_proba_test, pos_label = CLASSES[0])
    result_auc_test = auc(fpr, tpr)
    fpr, tpr, thresholds = roc_curve(decision_class_val, predict_proba_val, pos_label = CLASSES[0])
    result_auc_val = auc(fpr, tpr)

    # save
    DIR_SAVE = DIR+'/'+FILENAME+'/MIXTURE/'+method+'/nobias2/'+ITER
    if not os.path.isdir(DIR_SAVE) : os.makedirs(DIR_SAVE, exist_ok=True)
    fullpath_test = DIR_SAVE+'/result_test.tsv'
    fullpath_val = DIR_SAVE+'/result_val.tsv'
    df_result_test = pd.DataFrame({'y_true' : decision_class_test, 'y_predict' : predict_test, 'y_predict_proba' : predict_proba_test, 'acc' : result_acc_test, 'auc' : result_auc_test})
    df_result_val = pd.DataFrame({'y_true' : decision_class_val, 'y_predict' : predict_val, 'y_predict_proba' : predict_proba_val, 'acc' : result_acc_val, 'auc' : result_auc_val})
    pd.DataFrame.to_csv(df_result_test, fullpath_test, index=False, sep='\t', header=True)
    pd.DataFrame.to_csv(df_result_val, fullpath_val, index=False, sep='\t', header=True)
    
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')+' '+FILENAME+' '+method+' '+ITER+" END")

# ========================================
# multi に実行する
# ========================================
def multi_main(n_jobs, DIR, FILENAMES, CLASSES, rulesets, methods):
    joblib.Parallel(n_jobs=n_jobs)(joblib.delayed(main)(DIR, FILENAME, CLASSES[FILENAME], ruleset, method, ITER) for (FILENAME, ruleset, method, ITER) in product(FILENAMES, rulesets, methods, range(1,51)))

# -------------------------------------------
# main
# -------------------------------------------
if __name__ == "__main__":

    DIR = '/mnt/data/uci'
    #FILENAMES = ['german_credit_categorical', 'default_cleansing', 'adult_cleansing2']
    FILENAMES = ['adult_cleansing2']
    #FILENAMES = ['default_cleansing']
    #FILENAMES = ['german_credit_categorical']
    CLASSES = {'german_credit_categorical' : [1, 2], 
               'default_cleansing' : [1, 2],
               'adult_cleansing2' : ["<=50K", ">50K"]}

    rulesets = ['MIXTURE/rules/nobias2']
    methods = ['A','B','both']

    #FILENAME = 'adult_cleansing2'
    #FILENAME = 'german_credit_categorical'
    #ruleset = 'MIXTURE/rules/nobias'
    #method = "A"
    #ITER = 1
    
    #main(DIR, FILENAME, CLASSES[FILENAME], ruleset, method, ITER)

    n_jobs = 50
    multi_main(n_jobs, DIR, FILENAMES, CLASSES, rulesets, methods)

