# coding: utf-8
# only python 3.4
import pandas as pd
import pprint
import json
from collections import defaultdict

# ---------------------------
# Parameters
# ---------------------------
FILENAME = 'hayes-roth'

# ---------------------------
# Option
# ---------------------------
pp = pprint.PrettyPrinter(indent=4)
pd.set_option('display.max_columns', None)

# --------------------------
# Rule Class
# --------------------------
class Rule :
   idx = list()
   consequnets = list()
   values = list()   
   support = list()

   def getIdx(self) :
      return(self.idx)
   def getConsequents(self) :
      return(self.consequents)
   def getValues(self) :
      return(self.values)
   def getSupport(self) :
      return(self.support)
 
# =====================================
# filepathからデータを返す関数
# =====================================
def getDecisionTable(filepath) :
    decision_table = pd.read_csv(filepath, delimiter='\t')
    return(decision_table)

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
def getJudgeNominal(decison_table, list_nominal) :
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

# =========================================
# 各条件属性の取りうる条件属性値の集合を返す
# =========================================
def getDescriptors(decision_table) :
    list_descriptors = defaultdict(list)
    columns = getColNames(decision_table)
    for i in range(len(columns)-1) :
        tmp = list(pd.Series(decision_table.ix[:,i]).unique())
        list_descriptors[columns[i]] = tmp
    return(list_descriptors)
#print list_descriptors

# =========================================
# cutpoint型の各条件属性の取りうる条件属性値候補集合をリスト構造で返す
# =========================================
def getAttributeValueParis(decision_table, list_nominal) :
    class AttributeValuePairs:
        def __init__(self, idx, atype, value, support):
            self.idx = idx
            self.atype = atype
            self.value = value
            self.support = support
        def output(self) :
            print("idx:" + str(self.idx))
            print("atype:" + str(self.atype))
            print("value:" +  str(self.value))
            print("support:" + str(self.support))
        def getIdx(self) :
            return(self.idx) 
        def getSupport(self) :
            return(self.support)

    list_columns = list(decision_table.columns)
    list_descriptors = getDescriptors(decision_table)
    list_attributeValuePairs = list()
    list_judgeNominal = getJudgeNominal(decision_table, list_nominal)
    for i in list_descriptors :
        if list_judgeNominal[i] :
            for j in list_descriptors[i] :
                ind = list_columns.index(i) + 1
                support_idx = list(decision_table[decision_table[i] == j].index)
                avp = AttributeValuePairs(ind, "nom", j, support_idx)
                list_attributeValuePairs.append(avp)
                print("nominal : " + str(j))
        else :
             for j in list_descriptors[i] :
                support_idx = list(decision_table[decision_table[i] == j].index)
                print("no : " + str(j))
    #print(list_attributeValuePairs[0].value)
    return(list_attributeValuePairs)
        #list_attributeValuePairs[cn] = decision_table[cn].value_counts()
        #for value in list_descriptors[cn] :
        #    list_attributeValuePairs2[value] = decision_table[decision_table[cn]==value].index
    #list_attributeValuePairs2[cn] = decision_table[cn].index
    #for value in list_descriptors[cn] :
    #    print value
    #print list_attributeValuePairs
    #print list_attributeValuePairs2
    #del list_descriptors

# ========================================
# lowerApproximations を返す
# ========================================
def getApproximations(decision_table) :
    list_lowerApproximations = defaultdict(list)
    for i in vec_cls.unique() :
        lowerApproximations[i] = decision_table[decision_table['class']==i].index
    return(list_lowerApproximations)
#print lowerApproximations

# =======================================
# list が空ならexit
# ======================================
def exitEmptyList(l) :
   if not l:
       sys.exit("empty list")

# =====================================
# list同士のintersectを返す
# =====================================
def intersect(list_a, list_b) :
    return(list(set(list_a) & set(list_b)))

# =====================================
# list a が b に包含されているかを判定する
# =====================================
def isSuperList(list_a, list_b) :
    return(set(list_b).issuperset(set(list_a)))

# ========================================
# main
# ========================================
if __name__ == "__main__":

    # read data 
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-train3-3.tsv'
    decision_table = getDecisionTable(filepath)

    # read nominal
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = getNominalList(filepath)

    # 属性名
    print(getColNames(decision_table))
  
    # 属性値集合
    list_descriptors = getDescriptors(decision_table)
    pp.pprint(list_descriptors)

    # AttributeValuePairs
    list_attributeValuePairs = getAttributeValueParis(decision_table, list_nominal)
    #print(list_attributeValuePairs[1].getIdx())

    # Lower Approximation
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-train-la-3-3.tsv'
    df_la = pd.read_csv(filepath, delimiter='\t')
    list_la = defaultdict(list)
    tmp = list(pd.Series(df_la['class']).unique())
    for i in tmp :
        list_la[i] = df_la[df_la['class'] == i]['ind'].values.tolist()

    # 各クラスごとにRuleを求める
    for i in list_la :
        list_concept = list_la[i]

        # cocept が空ならStop
        exitEmptyList(list_concept)

        # 初期設定( G = B )
        list_uncoveredConcept = list_concept 
        
        ## G が空じゃないならループを続ける
        while list_uncoveredConcept :
   
            # Rule の初期設定
            rule = Rule()

            # TGの候補集合を求める 
            list_TG = [avp for avp in list_attributeValuePairs if intersect(list_uncoveredConcept, avp.getSupport())]
            
            # ruleを求める
            count = 0
            while not rule.getSupport() or not isSuperList(rule.getSupport(), list_concept) :

                bestAttributeValuePair = None

                list_cover_num = [ len(intersect(list_uncoveredConcept, avp.getSupport())) for avp in list_TG ] 
                print("list_cover_num:" + str(list_cover_num))

                list_TG_max = [ avp for avp in list_TG if len(intersect(list_uncoveredConcept, avp.getSupport())) == max(list_cover_num)]
                print("list_TG_max:" + str(len(list_TG_max)))

                if len(list_TG_max) == 1 :
                    bestAttributeValuePair = list_TG_max[0]
                else :
                    minValue = min([len(avp.getSupport()) for avp in list_TG_max ])
                    print("minValuem:" + str(inValue))
                    list_TG_min = [ avp for avp in list_TG_max if len(avp.getSupport()) == minValue]
                    print("list_TG_min:" + str(list_TG_min))
                    bestAttributeValuePair = list_TG_min[0]

                # T : T U {t} のところから

                count = count + 1
                if count == 2:
                    break
                print(count)
        
            del list_uncoveredConcept[0]
            print("The Number of uncovered Concept : " + str(len(list_uncoveredConcept)))
