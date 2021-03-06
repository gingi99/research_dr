# coding: utf-8
# python 3.5
import pandas as pd
import numpy as np
import pprint
import json
import sys
from itertools import chain
from itertools import combinations
from itertools import product
from collections import defaultdict
from collections import Counter
from RuleMLEM2 import Rule
from RuleMLEM2 import Rule2
from loadData import getDataNominalLowerNormal
from loadData import getDataNominalLowerMixture
# common
sys.path.append("../common/")
from util import exitEmptyList
from util import intersect
from util import setdiff
from util import isSuperList
# ---------------------------
# Option
# ---------------------------
pp = pprint.PrettyPrinter(indent=4)
pd.set_option('display.max_columns', None)
DIR_UCI = '/mnt/data/uci'

# =====================================
# Rules を見る関数
# =====================================
def showRules(list_rules) :
    for rule in list_rules :
        rule.output()

# =====================================
# Rules を JSON形式でsaveする関数
# =====================================
def saveJsonRules(list_rules, fullpath_filename) :
    #fullpath_filename = '/Users/ooki/git/research_dr/python/Experiment/output.json'
    for rule in list_rules :
        # 初期化         
        rule_save_object = defaultdict(list)
        # support        
        rule_save_object['support'] = list(map(str, rule.getSupport()))
        # 結論部        
        if type(rule.getConsequent()) == list : rule_save_object['consequent'] = list(map(str,rule.getConsequent()))
        else : rule_save_object['consequent'].append(str(rule.getConsequent()))
        # 条件部        
        list_values = [{key : rule.getValue(key)} for key in rule.getKey()]
        rule_save_object['value'] = list_values
        # save
        with open(fullpath_filename, 'a') as outfile:
            json.dump(rule_save_object, outfile)
            outfile.write('\n')
        #print(json.dumps(rule_save_object))

# =====================================
# Rules が推定するクラス
# =====================================    
def getEstimatedClass(list_rules) :
    consequents = list(set(r.getConsequent() for r in list_rules))
    consequents = sorted(consequents)
    return(consequents)
 
# =====================================
# 指定したConsequentを持つ / 持たないRulesを返す
# =====================================    
def getRulesClass(list_rules, consequent, judge=True):
    if judge : rules = [r for r in list_rules if r.getConsequent() == consequent]
    else : rules = [r for r in list_rules if r.getConsequent() != consequent]     
    return(rules)

# =====================================
# Rules のうち、P個の属性値が分かれば、クラスを推定できるか
# =====================================
def getPerIdentifiedClass(rules, p) :         
    #list_conditions = [(k,v) for k,values in ruleAttributeValuePairs.items() for v in values]
    
    ruleAttributeValuePairs = defaultdict(set)            
    for r in rules :
        for key,value in r.value.items() :
            #print(key,value)
            for v in value :
                ruleAttributeValuePairs[key].add(v)

    rule_attributes = [r.getKey() for r in rules]
    attributes = tuple(set(chain.from_iterable(rule_attributes)))
    combi_attributes = list(combinations(attributes,p))
    count = 0
    bunbo = 0
    for combi in combi_attributes :
        list_combi = [list(ruleAttributeValuePairs[c]) for c in combi]
        list_combi_product = list(product(*list_combi))
        bunbo += len(list_combi_product)
        for lc in list_combi_product:
            rules_target = list()
            # combi をもつルールを探す            
            for r in rules :
                match_count = 0
                # combi の条件属性を持つかチェック。なければスキップ
                if not isSuperList(list(combi), r.getKey()) :
                    continue
                for (i, c) in enumerate(combi):
                    if lc[i] in r.getValue(c, onecase = False) :
                        match_count += 1
                else :
                    if match_count == len(combi):
                        rules_target.append(r) 
            # rules_target が空なら評価から外す
            if len(rules_target) == 0:
                bunbo -= 1
            else:
                # rules_target が推定するクラスが１つのみなら、1増やす
                if len(getEstimatedClass(rules_target)) == 1 :
                    count += 1
    if bunbo == 0 :
        ans = 0
    else:
        ans = (count / bunbo)
    return(ans)

# =====================================
# Rule を Simplity にして返す
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
# Rule を idex -> valuesなdefaultdict型にして返す
# =====================================
def convertRule(rule, colnames) :
    rule_new = Rule2()
    # value を setする
    for i, idx in enumerate(rule.getIdx()):
        rule_new.setValue(colnames[idx-1], rule.getValue()[i])
    # consequent と support を setする
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
# ある条件属性 condition の取りうる条件属性値の集合を返す
# =========================================
def getConditionValues(decision_table, condition) :
    list_values = list(pd.Series(decision_table[condition]).unique())
    return(list_values)

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
                avp = AttributeValuePairs(ind, "nom", str(j), support_idx)
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
# rules のrが支持する対象で構成される決定表を作る
# =====================================
def getDecisionTableFromRules(rules, decision_table):
    df_merge = pd.DataFrame(columns = decision_table.columns)
    for r in rules :
        df_r = decision_table.iloc[r.getSupport()]
        df_merge = pd.concat([df_merge, df_r], ignore_index = True, axis=0)
    return(df_merge)

# =====================================
# Main 関数
# =====================================
def getRulesFromData1(decision_table, list_nominal, list_la):

    # AttributeValuePairs
    list_attributeValuePairs = getAttributeValueParis(decision_table, list_nominal)
    #print(list_attributeValuePairs[1].getIdx())

    # Rules の初期設定
    rules = list()

    # 各クラスごとにRuleを求める
    for i in list_la :
        #print("Deicision Class : " + str(i))
        list_concept = list_la[i]
        #print("list_concept : " + str(sorted(list_concept)))
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
                #print("list_cover_num:" + str(list_cover_num))

                list_TG_max = [ avp for avp in list_TG if len(intersect(list_uncoveredConcept, avp.getSupport())) == max(list_cover_num)]
                #print("list_TG_max Number:" + str(len(list_TG_max)))

                if len(list_TG_max) == 1 :
                    bestAttributeValuePair = list_TG_max[0]
                else :
                    minValue = min([len(avp.getSupport()) for avp in list_TG_max ])
                    #print("minValue:" + str(minValue))
                    list_TG_min = [ avp for avp in list_TG_max if len(avp.getSupport()) == minValue]
                    #print("list_TG_min Number:" + str(len(list_TG_min)))
                    bestAttributeValuePair = list_TG_min[0]

                # T : T U {t} のところ
                list_T.append(bestAttributeValuePair)
                #print("list_T : " + str(getAllSupport(list_T)))
                #print("best Attribute Pair : "+str(bestAttributeValuePair.getSupport()))
                
                # G := [t] ∩ G のところ
                list_uncoveredConcept = intersect(bestAttributeValuePair.getSupport(), list_uncoveredConcept)
                #print("list_uncoveredConcept : " + str(list_uncoveredConcept))
 
                # TG の更新 T(G) :=  {t : t ^ G}のところ
                list_TG = list()                
                list_TG = [avp for avp in list_attributeValuePairs if intersect(list_uncoveredConcept, avp.getSupport())]
                #print("list_TG : " + str(list_TG))
                #print("list_TG : " + str(len(list_TG)))
                #print("list_T : " + str(list_T))           
                #print("list_T : " + str(len(list_T)))

                # T(G) := T(G) - T
                list_TG = setdiff(list_TG, list_T)
                #print("list_TG : " + str(len(list_TG)))

       
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
    rules_simple = [simplifyRule(r) for r in rules]
    
    # Rule2型にconvert
    colnames = getColNames(decision_table)
    rules_convert = [convertRule(r,colnames) for r in rules_simple]
        
    # END
    return(rules_convert)

def getRulesByMLEM2(FILENAME, iter1, iter2) :
    # loadData
    decision_table, list_nominal, list_la = getDataNominalLowerNormal(DIR_UCI, FILENAME, iter1, iter2)
    # induce rules
    rules = getRulesFromData1(decision_table, list_nominal, list_la)
    return(rules)

def getRulesByMLEM2_MIXTURE(DIR, dataset, FILENAME, AB, ITER):
    # loadData
    decision_table, list_nominal, list_la = getDataNominalLowerMixture(DIR, dataset, FILENAME, AB, ITER)
    # induce rules
    rules = getRulesFromData1(decision_table, list_nominal, list_la)
    return(rules)

# ========================================
# main
# ========================================
if __name__ == "__main__":

    #FILENAME = 'german_credit_categorical'
    FILENAME = 'adult_cleansing2'
    iter1 = 1
    iter2 = 1
    
    rules = getRulesByMLEM2(FILENAME, iter1, iter2)
    showRules(rules)
