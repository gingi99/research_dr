# coding: utf-8
import os
import sys
import joblib
import datetime
from itertools import product
from mlem2 import getRulesByMLEM2_MIXTURE
#from mlem2 import showRules
# common
sys.path.append("../common/")
from util import savePickle

# ========================================
# main
# ========================================
def main(DIR, FILENAME, dataset, AB, ITER) :
    ITER = str(ITER)
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')+' '+FILENAME+' '+AB+' '+ITER+" START")
    rules = getRulesByMLEM2_MIXTURE(DIR, FILENAME, dataset, AB, ITER)
    DIR_SAVE = DIR+'/'+FILENAME+'/MIXTURE/rules/nobias2/'+ITER
    if not os.path.isdir(DIR_SAVE) : os.makedirs(DIR_SAVE, exist_ok=True)
    fullpath = DIR_SAVE+'/rules_'+AB+'.pkl'
    savePickle(rules, fullpath)
    print("rules save : ", fullpath)
    print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')+' '+FILENAME+' '+AB+' '+ITER+" END")

# ========================================
# multi に実行する
# ========================================
def multi_main(n_jobs, DIR, FILENAMES, datasets):
    joblib.Parallel(n_jobs=n_jobs)(joblib.delayed(main)(DIR, FILENAME, dataset, AB, ITER) for (FILENAME, dataset, AB, ITER) in product(FILENAMES, datasets, ['A', 'B'], range(1,51)))

# -------------------------------------------
# main
# -------------------------------------------
if __name__ == "__main__":

    DIR = '/mnt/data/uci'
    FILENAMES = ['german_credit_categorical', 'default_cleansing', 'adult_cleansing2']
    datasets = ['MIXTURE/dataset/nobias2']

    #DIR = '/mnt/data/uci'
    #FILENAME = 'adult_cleansing2'
    #FILENAME = 'german_credit_categorical'
    #dataset = 'MIXTURE/dataset/nobias'
    #AB = 'A'
    #ITER = 1
    
    #main(DIR, FILENAME, dataset, AB, ITER)

    n_jobs = 50
    multi_main(n_jobs, DIR, FILENAMES, datasets)

    #rules = getRulesByMLEM2_MIXTURE(DIR, FILENAME, dataset, AB, ITER)
    #showRules(rules)
