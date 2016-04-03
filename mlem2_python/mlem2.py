# coding: utf-8
import pandas as pd
import pprint
import json
from collections import defaultdict

# ---------------------------
# Opetion
# ---------------------------
pp = pprint.PrettyPrinter(indent=4)
pd.set_option('display.max_columns', None)

# =====================================
# filepathからデータを返す関数
# =====================================
def getDecisionTable(filepath) :
    decision_table = pd.read_csv(filepath, delimiter='\t')
    return(decision_table)

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
def getAttributeValueParis(decision_table) :
    class AttributeValuePairs:
        idx = 0
        value = ''
        def __init__(self, idx, atype, value, support):
            self.idx = idx
            self.atype = atype
            self.value = value
            self.support = support
        #def output(self) :
        #    print("value:" +  self.value)

    list_descriptors = getDescriptors(decision_table)
    list_attributeValuePairs = list()
    for i in list_descriptors :
        for j in list_descriptors[i] :
            if type(j) == str :
                avp = AttributeValuePairs(0, "nom", j, 1)
                list_attributeValuePairs.append(avp)
                print("str : " + j)
            elif type(j) == float :
                print("float : " + str(j))
            else :
                print("no : " + str(type(j)))
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


# ========================================
# main
# ========================================
if __name__ == "__main__":

    # read data 
    filepath = '/data/uci/hayes-roth/hayes-roth-train3-3.tsv'
    decision_table = getDecisionTable(filepath)

    # 属性名
    print(getColNames(decision_table))
  
    # 属性値集合
    list_descriptors = getDescriptors(decision_table)
    pp.pprint(list_descriptors)

    # AttributeValuePairs
    list_attributeValuePairs = getAttributeValueParis(decision_table)

    # Lower Approximation
    filepath = '/data/uci/hayes-roth/hayes-roth-train-la-3-3.tsv'
     

# =======================================
def test() :
    for i in lowerApproximations :
        concept = lowerApproximations[i]
    #if len(concept) == 0 :
        #print "Empty lower approximation of a decision class"
    #    continue
    vec_decisionValues = vec_cls
    #print concept
    conclusion = pd.Series(vec_decisionValues[concept]).unique()
    #if len(conclusion) > 1:
    #    print "error : not right decisionValues"
    #print conclusion

    ## 初期設定 G=B のところ
    uncoveredConcept = concept

    ## T := 0 のところ
    tmpRule = defaultdict(list)
	
    ## TG := { t : t ^ G} のところ
    TG = defaultdict(list)
    count = 1
    for key in list_attributeValuePairs2 :
        if len(uncoveredConcept.intersection(list_attributeValuePairs2[key])) > 0 :
            name = "bes"+str(count)
            count += 1
            TG[name] = key
    #print json.dumps(TG,sort_keys=True, indent=4)
    #    tmp = pd.Series(decision_table.ix[uncoveredConcept,i]).unique()
    #    TG[j] = tmp

    totalSupport = 0

    #while(len(tmpRule) == 0 or )
    t_best = list()
    vec_cover_num = defaultdict(list)
    tmpMaxValue = 0
    for key in TG :
       vec_cover_num[key] = len(uncoveredConcept.intersection(list_attributeValuePairs2[TG[key]]))
       if tmpMaxValue < vec_cover_num[key] :
           tmpMaxValue = vec_cover_num[key]
			    		

