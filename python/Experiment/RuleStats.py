# coding: utf-8
# python 3.5
from itertools import product
from sklearn.metrics import accuracy_score
from multiprocessing import Pool
from multiprocessing import freeze_support
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/../MLEM2')
import logging
logging.basicConfig(filename=os.path.dirname(os.path.abspath(__file__))+'/ExperimentsMLEM2.log',format='%(asctime)s,%(message)s',level=logging.DEBUG)
#import importlib
import mlem2
#importlib.reload(mlem2)  
import LERS

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
def multi_main(proc,FILENAMES):
    pool = Pool(proc)
    multiargs = []
    for FILENAME, iter1, iter2 in product(FILENAMES, range(1,11), range(1,11)):    
        multiargs.append((FILENAME,iter1,iter2))
  
    #results = pool.starmap(MLEM2_LERS, multiargs)
    return(results)
      
# ========================================
# main
# ========================================
if __name__ == "__main__":

    #FILENAMES = ['hayes-roth']    
    #rules = 
    rules = mlem2.getRulesByMLEM2('hayes-roth', 2, 2)


    # シングルプロセスで実行
    #for FILENAME, iter1, iter2 in product(FILENAMES, range(1,11), range(1,11)):    
    #    print('{filename} {i1} {i2}'.format(filename=FILENAME, i1=iter1, i2=iter2))
    #    print(MLEM2_LERS(FILENAME, iter1, iter2))

    # 並列実行    
    proc=4
    freeze_support()
    results = multi_main(proc, FILENAMES)
    
    # 平均と分散
    print(getEvalMeanVar(results))
    
    # 保存する
    #saveResults(results, "/data/uci/hayes-roth/accuracy.txt")
