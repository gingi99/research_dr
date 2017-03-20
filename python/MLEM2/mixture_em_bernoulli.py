# coding: utf-8
import os
import sys
import joblib
import datetime
import numpy as np
import pandas as pd
from scipy.stats import bernoulli
from sklearn.metrics import roc_curve
from sklearn.metrics import auc
from itertools import product
# common
sys.path.append("../common/")
from util import loadPickle

# ----------------------------------------
# Rules をロードする
# ----------------------------------------
def loadRules(DIR, FILENAME, ruleset, method, ITER):
    fullpath_rules_A = DIR+'/'+FILENAME+'/'+ruleset+'/'+ITER+'/rules_A.pkl'
    fullpath_rules_B = DIR+'/'+FILENAME+'/'+ruleset+'/'+ITER+'/rules_B.pkl'
    rules_A = loadPickle(fullpath_rules_A)
    rules_B = loadPickle(fullpath_rules_B)
    return(rules_A, rules_B)

# ----------------------------------------
# Data and Scoreをロードする
# ----------------------------------------
def getq(DIR, FILENAME, ITER, target):
    df_A = pd.read_csv(DIR+"/"+FILENAME+"/MIXTURE/A/nobias2/"+ITER+"/result_"+target+".tsv", sep="\t")
    df_B = pd.read_csv(DIR+"/"+FILENAME+"/MIXTURE/B/nobias2/"+ITER+"/result_"+target+".tsv", sep="\t")
    key = "y_predict_proba"
    q_A = pd.DataFrame.as_matrix(df_A[key])
    q_B = pd.DataFrame.as_matrix(df_B[key])
    return(q_A, q_B)

def gety(DIR, FILENAME, ITER, target):
    df_A = pd.read_csv(DIR+"/"+FILENAME+"/MIXTURE/dataset/nobias2/"+ITER+"/"+target+"_A.tsv", sep="\t")
    y = pd.DataFrame.as_matrix(df_A["class"])
    return(y)

def getp(DIR, FILENAME, ITER, target, q_val_A, q_val_B):
    y = gety(DIR, FILENAME, ITER, target = target)
    p_val_A = np.array(bernoulli(q_val_A).pmf(y))
    p_val_B = np.array(bernoulli(q_val_B).pmf(y))
    p = np.array([p_val_A, p_val_B])
    return(p)

# ----------------------------------------
# AUC
# ----------------------------------------
def getAUC(y, score, pos_label):
    fpr, tpr, thresholds = roc_curve(y, score, pos_label=pos_label)
    roc_auc = auc(fpr, tpr)
    return(roc_auc)

# ----------------------------------------
# EM
# ----------------------------------------
def Q(p, alpha, qtk):
    return(np.nansum(qtk * np.log((np.array([alpha, 1.0 - alpha])[:,np.newaxis] * p) / qtk)))

def EStep(alpha, p) :
    qtk = np.array([alpha, 1.0 - alpha])[:,np.newaxis] * p
    return(qtk / np.nansum(qtk, axis=0))

def MStep(qtk) :
    return(np.nansum(qtk, axis=1) / qtk.shape[1])

def mainEM(p):
    alpha = 0.5
    n_iter = 100
    for i in range(n_iter):
        qtk = EStep(alpha, p)
        alpha = MStep(qtk)[0]
        #print("Q : ", Q(p, alpha, qtk))
        #print("alpha :", alpha)
    return(alpha)

def getScore(alpha, q_A, q_B) :
    score = alpha * q_A + (1.0 - alpha) * q_B
    return(score)

# ========================================
# main
# ========================================
def main(DIR, FILENAME, CLASSES, ITER) :
    ITER = str(ITER)
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')+' '+FILENAME+' '+ITER+" START")

    # load score
    q_val_A, q_val_B = getq(DIR, FILENAME, ITER, "val")
    p = getp(DIR, FILENAME, ITER, "val", q_val_A, q_val_B)

    alpha = mainEM(p)
    print("alpha : ", alpha)

    # test evaluation
    q_test_A, q_test_B = getq(DIR, FILENAME, ITER, "test")
    y_test = gety(DIR, FILENAME, ITER, "test")
    score_test = getScore(alpha, q_test_A, q_test_B)
    result_auc_test = getAUC(y_test, score_test, CLASSES[0])
    print("result_auc_test : ", result_auc_test)

    # save
    DIR_SAVE = DIR+'/'+FILENAME+'/MIXTURE/em/nobias2/'+ITER
    if not os.path.isdir(DIR_SAVE) : os.makedirs(DIR_SAVE, exist_ok=True)
    fullpath_test = DIR_SAVE+'/result_test.tsv'
    df_result_test = pd.DataFrame({'y_true' : y_test, 'y_predict_proba' : score_test, 'auc' : result_auc_test})
    pd.DataFrame.to_csv(df_result_test, fullpath_test, index=False, sep='\t', header=True)
    
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')+' '+FILENAME+' '+ITER+" END")

# ========================================
# multi に実行する
# ========================================
def multi_main(n_jobs, DIR, FILENAMES, CLASSES):
    joblib.Parallel(n_jobs=n_jobs)(joblib.delayed(main)(DIR, FILENAME, CLASSES[FILENAME], ITER) for (FILENAME, ITER) in product(FILENAMES, range(1,51)))

# -------------------------------------------
# main
# -------------------------------------------
if __name__ == "__main__":

    DIR = '/mnt/data/uci'
    #FILENAMES = ['german_credit_categorical', 'default_cleansing', 'adult_cleansing2']
    #FILENAMES = ['adult_cleansing2']
    FILENAMES = ['default_cleansing']
    #FILENAMES = ['german_credit_categorical']
    CLASSES = {'german_credit_categorical' : [1, 2], 
               'default_cleansing' : [1, 2],
               'adult_cleansing2' : ["<=50K", ">50K"]}

    #FILENAME = 'adult_cleansing2'
    #FILENAME = 'german_credit_categorical'
    #ITER = 1
    
    #main(DIR, FILENAME, CLASSES[FILENAME], ITER)

    n_jobs = 8
    multi_main(n_jobs, DIR, FILENAMES, CLASSES)

