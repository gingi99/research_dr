# coding: utf-8
# python 3.4
# Usage : python mlem2.py --f [data.tsv] --nominal [data.nominal]
import argparse
import pandas as pd
import pprint
import sys
import numpy as np
from itertools import chain
from collections import defaultdict
from collections import Counter

# ---------------------------
# Parameters
# ---------------------------
params = sys.argv
length = len(params)

parser = argparse.ArgumentParser(description = 'argparse MLEM2')
parser.add_argument('--f', dest='F', help = '/data/data.tsv', default = ".*")
args = parser.parse_args()

DECISION_TABLE = args.F

FILENAME = 'hayes-roth'
DECISION_TABLE = 'hayes-roth'
DECISION_NOMINAL = 'hayes-roth.nominal'
LOWER_APPROXIMATION = 'hayes-roth-la'

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
   consequnet = list()
   value = list()   
   support = list()

   def setIdx(self, idxes) :
       self.idx = idxes
   def setValue(self, values) :
       self.value = values
   def setConsequent(self, consequents) :
       self.consequent = consequents
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

# =====================================
# Rules を見る関数
# =====================================
def showRules(list_rules) :
    for rule in list_rules :
        rule.output()

# =====================================
# Rule を Simplity にして返す （未完成）
# =====================================
def simplifyRule(rule) :
    # 重複のidxがあるかチェック。なければruleを返す
    if not [item for item, count in Counter(rule.getIdx()).items() if count > 1]:
        return(rule)
    rule_new = Rule()
    list_idxes_new = list()
    list_values_new = list()
    idxes = rule.getIdx()
    values = np.array(rule.getValue())
    uniq_idxes = list(set(idxes))
    for idx in uniq_idxes :
        indices = [i for i, x in enumerate(idxes) if x == idx]
        list_flat = list(chain.from_iterable(values[indices]))
        min_value = min(list_flat)
        max_value = max(list_flat)
        list_idxes_new.append(idx)
        list_values_new.append((min_value, max_value))
    # 新しいルールにSet
    rule_new.setIdx(list_idxes_new)
    rule_new.setValue(list_values_new)
    rule_new.setConsequent(rule.getConsequent())
    rule_new.setSupport(rule.getSupport())
    return(rule_new)
    
# =====================================
# avpのsupportをunionしたリストを返す
# =====================================
def getAllIdx(list_AttributeValuePairs) :
    all_idx = list()    
    for i in list_AttributeValuePairs :
        all_idx.append(i.getIdx())
    return(all_idx)

# =====================================
# avpのsupportをunionしたリストを返す
# =====================================
def getAllValue(list_AttributeValuePairs) :
    all_value = list()    
    for i in list_AttributeValuePairs :
        all_value.append(i.getValue())
    return(all_value)
   
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
        def getAtype(self) :
            return(self.atype)
        def getValue(self) :
            return(self.value)
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
                #print("nominal : " + str(j))
        else :
             values = sorted(list_descriptors[i])
             min_value = min(values)
             max_value = max(values)
             for j in range(len(values)-1) :
                cut_value = (values[j] + values[j+1]) / 2.0
                ind = list_columns.index(i) + 1
                support_idx = list(decision_table[(decision_table[i] < cut_value) & (decision_table[i] >= min_value)].index)
                avp = AttributeValuePairs(ind, "num", (min_value, cut_value), support_idx)
                list_attributeValuePairs.append(avp)
                support_idx = list(decision_table[(decision_table[i] >= cut_value) & (decision_table[i] <= max_value)].index)
                avp = AttributeValuePairs(ind, "num", (cut_value, max_value), support_idx)
                list_attributeValuePairs.append(avp)
                
                #print("no : " + str(j))
    #print(list_attributeValuePairs[0].value)
    return(list_attributeValuePairs)

# ========================================
# lowerApproximations を返す：未完成
# ========================================
def getApproximations(decision_table) :
    list_lowerApproximations = defaultdict(list)
#    for i in vec_cls.unique() :
#        lowerApproximations[i] = decision_table[decision_table['class']==i].index
    return(list_lowerApproximations)
#print lowerApproximations

# =====================================
# 下近似のリストを返す from R
# =====================================
def getLowerApproximation(lower_table) :
    list_la = defaultdict(list)
    tmp = list(pd.Series(lower_table['class']).unique())
    for i in tmp :
        list_la[i] = lower_table[lower_table['class'] == i]['ind'].values.tolist()
    return(list_la)

# =====================================
# 下近似のリストを返す from R
# =====================================
def getLowerApproximation(lower_table) :
    list_la = defaultdict(list)
    tmp = list(pd.Series(lower_table['class']).unique())
    for i in tmp :
        list_la[i] = lower_table[lower_table['class'] == i]['ind'].values.tolist()
    return(list_la)

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
# list 同士のunionを返す
# =====================================
def union(list_a, list_b) :
    return(list(set(list_a) | set(list_b)))

# =====================================
# list 同士のdiffを返す
# =====================================
def setdiff(list_a, list_b) :
    return(list(set(list_a) - set(list_b)))

# =====================================
# list a が b に包含されているかを判定する
# =====================================
def isSuperList(list_a, list_b) :
    return(set(list_b).issuperset(set(list_a)))

# =====================================
# Main 関数
# =====================================
def getRulesByMLEM2(FILENAME, iter1, iter2) :
    
    # read data
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table = getDecisionTable(filepath)

    # read nominal
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = getNominalList(filepath)


# ========================================
# main
# ========================================
if __name__ == "__main__":

    FILENAME = 'iris'
    iter1 = 1
    iter2 = 10

    # read data -> Lower A
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table = getDecisionTable(filepath)
    decision_table = decision_table.dropna()
    decision_table.index = range(decision_table.shape[0])

    # read nominal
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = getNominalList(filepath)
    
    # Lower Approximation
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-train-la-'+str(iter1)+'-'+str(iter2)+'.tsv'
    df_la = pd.read_csv(filepath, delimiter='\t')
    list_la = getLowerApproximation(df_la)

    # 属性値集合
    list_descriptors = getDescriptors(decision_table)
    #pp.pprint(list_descriptors)

    # AttributeValuePairs
    list_attributeValuePairs = getAttributeValueParis(decision_table, list_nominal)
    #print(list_attributeValuePairs[1].getIdx())

    # Rules の初期設定
    rules = list()

    # 各クラスごとにRuleを求める
    for i in list_la :
        print("Deicision Class : " + str(i))
        list_concept = list_la[i]
        print("list_concept : " + str(sorted(list_concept)))
        # cocept が空ならStop
        exitEmptyList(list_concept)

        # 初期設定( G = B )
        list_uncoveredConcept = list_concept[:] 
        
        ## G が空じゃないならループを続ける
        while list_uncoveredConcept :
   
            # Rule の初期設定
            rule = Rule()
            
            # T := 空集合
            list_T = list()

            # TGの候補集合を求める 
            list_TG = [avp for avp in list_attributeValuePairs if intersect(list_uncoveredConcept, avp.getSupport())]
            
            # ruleを求める
            #count = 0
            while not list_T or not isSuperList(getAllSupport(list_T), list_concept) :

                bestAttributeValuePair = None

                list_cover_num = [ len(intersect(list_uncoveredConcept, avp.getSupport())) for avp in list_TG ] 
                print("list_cover_num:" + str(list_cover_num))

                list_TG_max = [ avp for avp in list_TG if len(intersect(list_uncoveredConcept, avp.getSupport())) == max(list_cover_num)]
                print("list_TG_max Number:" + str(len(list_TG_max)))

                if len(list_TG_max) == 1 :
                    bestAttributeValuePair = list_TG_max[0]
                else :
                    minValue = min([len(avp.getSupport()) for avp in list_TG_max ])
                    print("minValue:" + str(minValue))
                    list_TG_min = [ avp for avp in list_TG_max if len(avp.getSupport()) == minValue]
                    print("list_TG_min Number:" + str(len(list_TG_min)))
                    bestAttributeValuePair = list_TG_min[0]

                # T : T U {t} のところ
                list_T.append(bestAttributeValuePair)
                print("list_T : " + str(getAllSupport(list_T)))
                print("best Attribute Pair : "+str(bestAttributeValuePair.getSupport()))
                
                # G := [t] ∩ G のところ
                list_uncoveredConcept = intersect(bestAttributeValuePair.getSupport(), list_uncoveredConcept)
                print("list_uncoveredConcept : " + str(list_uncoveredConcept))
 
                # TG の更新 T(G) :=  {t : t ^ G}のところ
                list_TG = list()                
                list_TG = [avp for avp in list_attributeValuePairs if intersect(list_uncoveredConcept, avp.getSupport())]
                print("list_TG : " + str(list_TG))
                print("list_TG : " + str(len(list_TG)))
                print("list_T : " + str(list_T))           
                print("list_T : " + str(len(list_T)))

                # T(G) := T(G) - T
                list_TG = setdiff(list_TG, list_T)
                print("list_TG : " + str(len(list_TG)))

       
            # list_T から不要なものを取り除く
            for avp in list_T :
                list_T_back = list_T[:]
                list_T_back.remove(avp)
                if isSuperList(getAllSupport(list_T_back), list_concept) and list_T_back :
                    list_T.remove(avp)
                    
            # list_T から ruleを作成して、rulesに追加
            rule.setIdx(getAllIdx(list_T))
            rule.setValue(getAllValue(list_T))
            rule.setConsequent(i)
            rule.setSupport(getAllSupport(list_T))
            rules.append(rule)

            #  Gの更新（G := B - [T] のところ)
            list_uncoveredConcept = list_concept[:]
            for r in rules :
                list_uncoveredConcept = setdiff(list_uncoveredConcept, r.getSupport())
           
            # test
            #del list_uncoveredConcept[0]
            #print("The Number of uncovered Concept : " + str(len(list_uncoveredConcept)))

        # 最後のスクリーニング
        for r in rules:
            rules_back = rules[:]
            rules_back.remove(r)
            if list_concept == getAllSupport(rules_back) :
                rules.remove(r)
	    
    # simplicity conditions	

    # END
    print(rules)
