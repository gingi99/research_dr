# coding: utf-8
# python 3.5
import pandas as pd
import pprint
from sklearn import tree
from itertools import chain
from collections import defaultdict

# ---------------------------
# Option
# ---------------------------
pp = pprint.PrettyPrinter(indent=4)
pd.set_option('display.max_columns', None)

# --------------------------
# Rule Class
# --------------------------
class Rule :
   def __init__(self):
       self.idx = list()
       self.consequent = list()
       self.value = list()   
       self.support = list()

   def setIdx(self, idxes) :
       self.idx = idxes
   def setValue(self, values) :
       self.value = values
   def setConsequent(self, consequents) :
       if not self.consequent :
           self.consequent = consequents
       else :
           self.support = union(self.consequent, consequents)
   def setSupport(self, supports) :
       if not self.support :
           self.support = supports
       else :
           self.support = intersect(self.support, supports)
   def getIdx(self) :
       return(self.idx)
   def getConsequent(self) :
       return(self.consequent)
   def getValue(self) :
       return(self.value)
   def getSupport(self) :
       return(sorted(self.support))
   def output(self) :
       print("idx:" + str(self.idx))
       print("consequent:" + str(self.consequent))
       print("value:" +  str(self.value))
       print("support:" + str(self.support))

# --------------------------
# Rule Class 2
# --------------------------
class Rule2 :
   def __init__(self):
       self.value = defaultdict(list)  
       self.consequent = list()
       self.support = list()

   def setValue(self, key, val) :
       #if not self.value[key] : self.value[key] = [val]
       #else : self.value[key].append(val)
       if type(val) == str :
           if val in self.value[key] : pass
           else : self.value[key].append(val)
       elif type(val) == list :
           self.value[key] = union(self.value[key],val)
       elif type(val) == tuple :
           print("tuple ha mada")
   def setConsequent(self, consequents) :
       #if not self.consequent :
       #    self.consequent = consequents
       #else :
       #    self.consequent = union(self.consequent, consequents)
       if consequents in self.consequent : pass
       else : self.consequent.append(consequents)
   def setSupport(self, supports) :
       if not self.support :
           self.support = supports
       else :
           self.support = intersect(self.support, supports)
   def getKey(self) :
       return(list(self.value.keys()))
   def getValue(self, idx) :
       if not idx in self.getKey(): 
           return(None)
       else: 
           i = iter(self.value[idx])
           if any(i) and not any(i) : return(self.value[idx][0])
           else : return(self.value[idx])
   def getConsequent(self) :
       i = iter(self.consequent)
       if any(i) and not any(i) : return(self.consequent[0])
       else : return(self.consequent)
   def getSupport(self) :
       return(sorted(self.support))
   def output(self) :
       print("value:" + str(self.value))
       print("consequent:" + str(self.consequent))
       print("support:" + str(self.support))

# =====================================
# filepathからデータを返す関数
# =====================================
def getDecisionTable(filepath) :
    decision_table = pd.read_csv(filepath, delimiter='\t')
    return(decision_table)

# =====================================
# 下近似に属する対象の決定表を返す
# =====================================
def getLowerDecisionTable(decision_table, list_la) :
    values = list(chain.from_iterable(list_la.values()))    
    decision_table_lower = decision_table.ix[sorted(values)]
    return(decision_table_lower)

# =====================================
# filepathからnominal Listを返す
# =====================================
def getNominalList(filepath) :
    f =  open(filepath)
    list_nominal = f.read().rstrip().split(",")
    return(list_nominal)

# ====================================
# 決定属性の値ベクトルを返す 
# ====================================
def getVecDecClass(decision_table) :
    vec_cls = pd.Series(decision_table['class'])
    return(vec_cls)
#print vec_cls.unique()
#decIdx = attr(decision_table, "decision.attr"

# ====================================
# 決定表の列名のベクトルを返す
# ====================================
def getColNames(decision_table) :
    vec_columns = decision_table.columns
    return(vec_columns)
#print len(columns)

# ====================================
# Nominal な属性をTrue / False で返す
# ====================================
def getJudgeNominal(decision_table, list_nominal) :
    list_judge = defaultdict(list)
    list_colnames = list(decision_table.columns)
    index = list(range(1, len(decision_table.columns)+1))
    index = map(str, index)
    for i in index :
        ind = int(i) - 1
        if i in list_nominal:
            list_judge[list_colnames[ind]] = True
        else :
            list_judge[list_colnames[ind]] = False
    return(list_judge)

# ========================================
# Decision Treeをコードで得る関数
# ========================================
def get_code(tree, feature_names):
    left      = tree.tree_.children_left
    right     = tree.tree_.children_right
    threshold = tree.tree_.threshold
    features  = [feature_names[i] for i in tree.tree_.feature]
    value = tree.tree_.value
    def recurse(left, right, threshold, features, node):
        if threshold[node] != -2 :
            print( "if ( " + features[node] + " <= " + str(threshold[node]) + " ) {")
            if left[node] != -1:
                recurse (left, right, threshold, features,left[node])
            print("} else {")
            if right[node] != -1:
                recurse (left, right, threshold, features,right[node])
            print("}")
        else:
            print("return " + str(value[node]))
    recurse(left, right, threshold, features, 0)

# ========================================
# main
# ========================================
def getRulesByDecisionTree(FILENAME, iter1, iter2) :
    
    # read data
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table = getDecisionTable(filepath)
    decision_table = decision_table.dropna()
    decision_table.index = range(decision_table.shape[0])

    # columns
    colnames = getColNames(decision_table)
    condition_attribute = list(colnames[0:(len(colnames)-1)])
    decision_attribute = colnames[-1]
   
    # read nominal
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = getNominalList(filepath)

    for i in list_nominal :
        decision_table[colnames[int(i)-1]] = decision_table[colnames[int(i)-1]].apply(str)

    # 決定木の分類器を作成。各種設定は引数に与える
    classifier = tree.DecisionTreeClassifier(criterion='gini',
                                             splitter='best',
                                             max_depth=None,
                                             min_samples_split=2,
                                             min_samples_leaf=1,
                                             min_weight_fraction_leaf=0.0,
                                             max_features=None,
                                             random_state=None,
                                             max_leaf_nodes=None,
                                             class_weight=None,
                                             presort=False)
    
    # 決定木の分類器にサンプルデータを食わせて学習。目的変数はSpecies
    classifier = classifier.fit(decision_table[condition_attribute], decision_table[decision_attribute])

    get_code(classifier, condition_attribute)
    

# ========================================
# main
# ========================================
if __name__ == "__main__":

    FILENAME = 'hayes-roth'
    iter1 = 4
    iter2 = 5
    
    getRulesByDecisionTree(FILENAME, iter1, iter2)