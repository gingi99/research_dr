# coding: utf-8
# python 3.5
import pandas as pd
import sys
from sklearn.metrics import accuracy_score
from itertools import chain
from itertools import combinations
from collections import defaultdict
import os
#sys.path.append('/Users/ooki/git/research_dr/python/MLEM2')
sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/../MLEM2')
import mlem2
import LERS
   
# =====================================
# avpのsupportをintersectしたリストを返す
# =====================================
def getAllSupport(list_AttributeValuePairs) :
    all_supports = list() 
    for i in list_AttributeValuePairs :
        if not all_supports :
            all_supports = i.getSupport()
        else :
            all_supports = intersect(all_supports, i.getSupport())
    return(all_supports)

# =========================================
# 各条件属性・決定属性の取りうる条件属性値の集合を返す
# =========================================
def getDescriptors(decision_table) :
    list_descriptors = defaultdict(list)
    columns = mlem2.getColNames(decision_table)
    for i in range(len(columns)) :
        tmp = list(pd.Series(decision_table.ix[:,i]).unique())
        list_descriptors[columns[i]] = tmp
    return(list_descriptors)

# =========================================
# cutpoint型の各条件属性の取りうる条件属性値候補集合をリスト構造で返す
# =========================================
def getAttributeValuePairs(decision_table) :
    class AttributeValuePairs:
        def __init__(self, idx, key, atype, value, support):
            self.idx = idx
            self.key = key
            self.atype = atype
            self.value = value
            self.support = support
        def output(self) :
            print("idx:" + str(self.idx))
            print("key:" + str(self.key))
            print("atype:" + str(self.atype))
            print("value:" +  str(self.value))
            print("support:" + str(self.support))
        def getIdx(self) :
            return(self.idx)
        def getKey(self) :
            return(self.key)
        def getAtype(self) :
            return(self.atype)
        def getValue(self) :
            return(self.value)
        def getSupport(self) :
            return(self.support)
    list_columns = list(decision_table.columns)
    list_descriptors = getDescriptors(decision_table)
    list_attributeValuePairs = list()
    for i in list_descriptors :
        for j in list_descriptors[i] :
                ind = list_columns.index(i) + 1
                key = i
                support_idx = list(decision_table[decision_table[i] == j].index)
                avp = AttributeValuePairs(ind, key, "nom", str(j), support_idx)
                list_attributeValuePairs.append(avp)
    return(list_attributeValuePairs)

# =====================================
# list同士のintersectを返す
# =====================================
def intersect(list_a, list_b) :
    return(list(set(list_a) & set(list_b)))

# =====================================
# listからべき集合を取り出す
# =====================================
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

# =====================================
# 候補アイテム集合のうち、１つ前の頻出アイテム集合にあるもので構成されているかを判定する
# =====================================
def isExistFrequentItemSet(candidate_item, frequent_itemset):  
    # candidate_itemの冪集合を求める
    #candidate_item_powerset = list(powerset(candidate_item))
    # 長さがcandidate_itemより1つ小さい要素を取り出す
    #list_candidate_item = [item for item in candidate_item_powerset if len(item) == len(candidate_item)-1]
    # list_candidate_item の全てがfrequent_itemsetに含まれているかチェック
    for lci in candidate_item:
        print(lci)
        if not lci in frequent_itemset:
            print(lci)
            return(False)
    return(True)

# =====================================
# 頻出パターンのconfを返す
# =====================================
def getConfidence(items, decision_table):
    supports_all = set.intersection(*map(set,[item.getSupport() for item in items]))
    supports_except_class = set.intersection(*map(set,[item.getSupport() for item in items if item.getIdx() != decision_table.shape[1]]))
    
    # なぜかsupports_except_class = 0 が出るので、それはスキップ
    if len(supports_except_class) == 0:
        return(0)
        
    # cofidence 
    conf = len(supports_all) / len(supports_except_class)
    return(conf)

# =====================================
# 頻出パターンからルールを作成する
# =====================================
def createRuleFromItems(items, decision_table):
    rule = mlem2.Rule2()
    supports_all = list(set.intersection(*map(set,[item.getSupport() for item in items])))
    rule.setSupport(supports_all)    
    for item in items:
        if item.getIdx() == decision_table.shape[1]:
            rule.setConsequent(item.getValue())
        else:
            rule.setValue(item.getKey(), item.getValue())
    return(rule)

# =====================================
# Main 関数
# =====================================
def getRulesByApriori(FILENAME, iter1, iter2, minsup, minconf) :
    
    # read data
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table = mlem2.getDecisionTable(filepath)
    decision_table = decision_table.dropna()
    decision_table.index = range(decision_table.shape[0])

    # AttributeValuePair
    attributeValuePair = getAttributeValuePairs(decision_table)

    # 頻出アイテム集合初期化
    dict_frequent_itemset = defaultdict(list)

    # 1 frequent itemset
    frequent_itemset = list()
    frequent_itemset = [{avp} for avp in attributeValuePair if len(avp.getSupport()) >= minsup]
    dict_frequent_itemset[1] = frequent_itemset
   
    # 2 ~ frequent itemset
    for c in range(2,decision_table.shape[1]+1) :
        #print(c)
        # 頻出アイテム集合から c組み合わせしたものを候補アイテム集合とする
        #candidate_itemset = list(combinations(frequent_itemset, c)) 
        list_candidate_item = []        
        for fi1 in range(len(dict_frequent_itemset[c-1])) :
            for fi2 in range(fi1+1, len(dict_frequent_itemset[c-1])):
                candidate_item = dict_frequent_itemset[c-1][fi1].union(dict_frequent_itemset[c-1][fi2])
                list_candidate_item.append(candidate_item)
                #print(fi1,fi2)
        list_candidate_item = [item for item in list_candidate_item if len(item) == c]        
        
        # 候補アイテム集合から、１つ前の頻出アイテム集合にあったもので構成されているかをチェックする -> 不要       
        #list_candidate_item = [ci for ci in list_candidate_item if isExistFrequentItemSet(ci, dict_frequent_itemset[c-1])]     

        # 候補アイテム集合からminsupを満たすものを次の頻出アイテム集合とする        
        tmp_frequent_itemset = [ci for ci in list_candidate_item if len(getAllSupport(ci)) >= minsup]
        
        # 頻出アイテム集合に追加する        
        dict_frequent_itemset[c] = tmp_frequent_itemset
    
    print('{iter1},{iter2},frequent item done'.format(iter1=iter1, iter2=iter2))
    
    # classのアイテムがある頻出パターンだけ取り出す
    list_target = []
    for c in range(2,decision_table.shape[1]+1) :
        for items in dict_frequent_itemset[c] :
            list_items = list(items)
            list_idx = [item.getIdx() for item in list_items]
            if decision_table.shape[1] in list_idx:
                list_target.append(list_items)
            else:
                pass
        print(c)
    
    # ルールの数
    print(len(list_target))
    
    # minconf より大きな頻出パターンだけ取り出す
    list_target = [items for items in list_target if getConfidence(items, decision_table) >= minconf]

    # rulesを作成する
    rules = [createRuleFromItems(items, decision_table) for items in list_target]

    # END
    return(rules)


# ========================================
# main
# ========================================
if __name__ == "__main__":

    FILENAME = 'hayes-roth'
    iter1 = 4
    iter2 = 5
    minsup = 10
    minconf = 1.0
        
    rules = getRulesByApriori(FILENAME, iter1, iter2, minsup, minconf)

    # test data setup
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-test'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table_test = mlem2.getDecisionTable(filepath)
    decision_table_test = decision_table_test.dropna()
    decision_class = decision_table_test[decision_table_test.columns[-1]].values.tolist()

    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)
    list_judgeNominal = mlem2.getJudgeNominal(decision_table_test, list_nominal)
    
    # predict by LERS
    predictions = LERS.predictByLERS(rules, decision_table_test, list_judgeNominal)
    
    # 正答率を求める
    accuracy = accuracy_score(list(map(str,decision_class)), predictions)
    print(accuracy)
