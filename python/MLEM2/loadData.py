# coding: utf-8
# python 3.5
import pandas as pd
import mlem2
#from mlem2 import getNominalList
#from mlem2 import getLowerApproximation

def getDataNominalLowerNormal(DIR, FILENAME, iter1, iter2) :

    # read data
    filepath = DIR+'/'+FILENAME+'/dataset/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table = pd.read_csv(filepath, delimiter='\t')
    decision_table = decision_table.dropna()
    decision_table.index = range(decision_table.shape[0])

    # read nominal
    filepath = DIR+'/'+FILENAME+'/dataset/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)

    # Lower Approximation
    filepath = DIR+'/'+FILENAME+'/dataset/'+FILENAME+'-train-la-'+str(iter1)+'-'+str(iter2)+'.tsv'
    df_la = pd.read_csv(filepath, delimiter='\t')
    list_la = mlem2.getLowerApproximation(df_la)

    return(decision_table, list_nominal, list_la)

def getDataNominalLowerMixture(DIR, FILENAME, dataset, AB, ITER) :
    ITER = str(ITER)
    # read data
    filepath = DIR+'/'+FILENAME+'/'+dataset+'/'+ITER+'/train_'+AB+'.tsv'
    decision_table = pd.read_csv(filepath, delimiter='\t')
    decision_table.index = range(decision_table.shape[0])

    # read nominal
    filepath = DIR+'/'+FILENAME+'/dataset/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)

    # Lower Approximation
    filepath = DIR+'/'+FILENAME+'/'+dataset+'/'+ITER+'/train_'+AB+'_la.tsv'
    df_la = pd.read_csv(filepath, delimiter='\t')
    list_la = mlem2.getLowerApproximation(df_la)

    return(decision_table, list_nominal, list_la)


