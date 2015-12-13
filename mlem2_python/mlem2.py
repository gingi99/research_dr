# coding: utf-8
import pandas as pd
import pprint
import json
from collections import defaultdict

decision_table = pd.read_csv('/data/uci/adult_cleansing2/adult_cleansing2-train2-6.tsv', delimiter='\t')
#print decision_table.head(n=2)

#decIdx = attr(decision_table, "decision.attr")
vec_cls = pd.Series(decision_table['class'])
#print vec_cls.unique()

columns = decision_table.columns
#print len(columns)

# 各条件属性の取りうる条件属性値を返す
list_descriptors = defaultdict(list)
for i in xrange(len(columns)-1) :
    tmp = pd.Series(decision_table.ix[:,i]).unique()
    list_descriptors[columns[i]] = tmp
#print list_descriptors

# cutpoint型の各条件属性の取りうる条件属性値候補集合をリスト構造で返す
list_attributeValuePairs = defaultdict(list)
list_attributeValuePairs2 = defaultdict(list)
for cn in list_descriptors :
    list_attributeValuePairs[cn] = decision_table[cn].value_counts()
    for value in list_descriptors[cn] :
        list_attributeValuePairs2[value] = decision_table[decision_table[cn]==value].index
    #list_attributeValuePairs2[cn] = decision_table[cn].index
    #for value in list_descriptors[cn] :
    #    print value
#print list_attributeValuePairs
print list_attributeValuePairs2
del list_descriptors

# lowerApproximations
lowerApproximations = defaultdict(list)
for i in vec_cls.unique() :
    lowerApproximations[i] = decision_table[decision_table['class']==i].index
#print lowerApproximations

for i in lowerApproximations :
    concept = lowerApproximations[i]
    if len(concept) == 0 :
        print "Empty lower approximation of a decision class."
        continue
    vec_decisionValues = vec_cls
    #print concept
    conclusion = pd.Series(vec_decisionValues[concept]).unique()
    if len(conclusion) > 1:
        print "error : not right decisionValues"
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
			    		

