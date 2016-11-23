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
# Rules の N Supportを満たす割合
# ====================================
def MLEM2_PerN(FILENAME, n) :

    ans = 0.0
    for iter1, iter2 in product(range(1,11), range(1,11)):
        # rule induction
        fullpath_filename = DIR_UCI+'/'+FILENAME+'/rules/'+'rules_'+str(iter1)+'-'+str(iter2)+'.pkl'
        rules = mlem2.loadPickleRules(fullpath_filename) if os.path.isfile(fullpath_filename) else mlem2.getRulesByMLEM2(FILENAME, iter1, iter2)

        # n per support
        per_n_support = mlem2.getPerNSupport(rules, n)
        ans += per_n_support
        print(per_n_support)
    ans /= 100
    print(ans)

# ========================================
# main
# ========================================
if __name__ == "__main__":

    # set data and k
    #FILENAMES = ['adult_cleansing2']
    FILENAME = 'default_cleansing'
    #FILENAMES = ['hayes-roth']
    #FILENAMES = ['german_credit_categorical']
    #FILENAMES = ['nursery']

    MLEM2_PerN(FILENAME, 1)
