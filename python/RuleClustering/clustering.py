# coding: utf-8
# python 3.5
import pandas as pd
import numpy as np
import pprint
import sys
from itertools import chain
from itertools import combinations
from itertools import product
from collections import defaultdict
from collections import Counter

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
       self.value[key] = val
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
   def getKey(self) :
       return(list(self.value.keys()))
   def getValue(self, idx) :
       return(self.value[idx])
   def getConsequent(self) :
       return(self.consequent)
   def getSupport(self) :
       return(sorted(self.support))
   def output(self) :
       print("value:" + str(self.value))
       print("consequent:" + str(self.consequent))
       print("support:" + str(self.support))


# =====================================
# Rules を見る関数
# =====================================
def showRules(list_rules) :
    for rule in list_rules :
        rule.output()

# =====================================
# Rules の Supportの平均数
# =====================================
def getMeanSupport(list_rules) :
    supports = [len(r.getSupport()) for r in list_rules]
    ans = '{mean}±{std}'.format(mean=('%.3f' % round(np.mean(supports),3)), std=('%.3f' % round(np.std(supports),3)))
    return(ans)

# =====================================
# Rules の Ruleの長さの平均数
# =====================================
def getMeanLength(list_rules) :
    lengths = [len(r.getKey()) for r in list_rules]
    ans = '{mean}±{std}'.format(mean=('%.3f' % round(np.mean(lengths),3)), std=('%.3f' % round(np.std(lengths),3)))
    return(ans)

# =====================================
# Rules のうち k-Supportを満たす割合
# =====================================
def getPerKRules(list_rules, k) :
    k_rules = [r for r in list_rules if len(r.getSupport()) >= k]
    ans = len(k_rules) / len(rules)
    return(ans)

# =====================================
# Rules が推定するクラス
# =====================================    
def getEstimatedClass(list_rules) :
    consequents = list(set(r.getConsequent() for r in list_rules))
    return(consequents)
    
# =====================================
# Rules のうち、P個の属性値が分かれば、クラスを推定できるか：たぶんできたけどテストしていない
# =====================================
def getPerIdentifiedClass(list_rules, p) :         
    #list_conditions = [(k,v) for k,values in ruleAttributeValuePairs.items() for v in values]
    
    ruleAttributeValuePairs = defaultdict(set)            
    for r in list_rules :
        for k,v in r.value.items() :
            print(k,v)
            ruleAttributeValuePairs[k].add(v)

    rule_attributes = [r.getKey() for r in list_rules]
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
            for (i, c) in enumerate(combi):
                for r in list_rules :
                    if r.getValue(c) == lc[i] :
                        rules_target.append(r) 
            if len(getEstimatedClass(rules_target)) == 1 :
                count += 1
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
# list a が b に または、b が a に包含されているかを判定する
# =====================================
def isEitherSuperList(list_a, list_b) :
    return(set(list_b).issuperset(set(list_a)) or set(list_a).issuperset(set(list_b)))

# =====================================
# Rule 間の類似度を返す関数
# =====================================
def getSimilarity(rule1, rule2, colnames, list_judgeNominal) :
    similarity = 0
    for col in colnames :
        # 両要素ともNAなら、0.5
        if (not rule1.getValue(col)) and (not rule2.getValue(col)) :       
            similarity += 0.5 
            print("0.5")
            continue
        # どちらかがNAなら、0
        if (not rule1.getValue(col)) or (not rule2.getValue(col)) :
            similarity += 0
            print("0")
            continue
        # 名義属性なら
        if list_judgeNominal[col] :
            # 包含関係があるなら
            if isEitherSuperList(rule1.getValue(col), rule2.getValue(col)):
                similarity += 1.0
                print("1")
            else :
                similarity += 1/3
                print("1/3")
        # 数値属性なら
        else :
            print("suuchi ha mada")
            #v <- 1.0 - (x[[i]] - y[[i]])/(3.0 * sd)
            #if(v < 0.0){
                #v <- 0
            #}
            similarity += 0
    similarity /= len(colnames)
    return(similarity)

# =====================================
# 2つのRuleを併合する関数：数値属性のときのsetValueはまだ実装できていない
# =====================================
def mergeRule(rule1, rule2):
    
    merge_rule = mlem2.Rule2()    
    
    # 2つのルールに両方持つ条件属性集合を抽出
    common_keys = intersect(rule1.getKey(), rule2.getKey())
    
    # 共通の条件属性がないなら
    if not common_keys :
        union_keys = union(rule1.getKey(), rule2.getKey())
        for key in union_keys :
            if rule1.getValue(key) != None : merge_rule.setValue(key, rule1.getValue(key))
            if rule2.getValue(key) != None : merge_rule.setValue(key, rule2.getValue(key))
    
    # 1つ以上共通の条件属性があるなら
    else :
        for key in common_keys :
            if rule1.getValue(key) != None : merge_rule.setValue(key, rule1.getValue(key))
            if rule2.getValue(key) != None : merge_rule.setValue(key, rule2.getValue(key))
    
    # consequent 
    merge_rule.setConsequent(rule1.getConsequent())
    merge_rule.setConsequent(rule2.getConsequent())
    
    # support数の計算
    merge_rule.setSupport(union(rule1.getSupport(), rule2.getSupport()))
      
    return(merge_rule)    

# =====================================
# Main 関数
# =====================================
def getRuleClusteringBySimilarity(rules, colnames, list_judgeNominal, k=3) :
    
    rules_neww = list()    
    
    # 結論部別
    for cls in mlem2.getEstimatedClass(rules) :
        target_rules = [r for r in rules if r.getConsequent() == cls]

        # ルール群のサポート値の最小値がk以下のルールがある内は繰り返す
        min_support = mlem2.getMinSupport(rules) 
        while min_support >= k :

            # target_rules が 1つなら
            if len(target_rules) == 1 :
                # 処理をかく

            # rulesの各組み合わせに対する類似度を求める
            combi_rule = list(combinations(tuple(target_rules),2))
            list_similarities = [getSimilarity(combi[0], combi[1], colnames, list_judgeNominal) for combi in combi_rule]

        
        rules_new.extend(target_rules)
        
    return(rules_new)
    
    
# =============

## ルール間の距離から、ルールを併合して新しいルールを作る
recreate_rules_by_dist <- function(rules, k=3){
  # 初期化
  rules.new <- rules
  
  # ルール群のサポート値の最小値を求める
  vec.supportsize <- sapply(rules, function(rule){
    return(length(rule$support))
  })
  minSupportValue <- min(vec.supportsize)
  
  # support sizeがk以下のルールがある内は繰り返す
  while(minSupportValue < k){
    ind.minValue <- which(vec.supportsize == minSupportValue)
    if(length(ind.minValue) == 1){
      ind.merge.target.rule <- ind.minValue
    }else{
      ind.merge.target.rule <- ind.minValue[1]
    }
    
    # 同じ結論部のルールを求める
    vec.same.consequents <- sapply(rules.new, function(rule){
      return(rule$consequent == rules.new[[ind.merge.target.rule]]$consequent)
    })
    
    # ルール間の類似度を求める
    mat.df.dist <- cal_dist_rules(convert_df_from_rules(rules.new))
    for(di in 1:length(rules.new)){
      mat.df.dist[di, di] <- 0
    }
    # merge target ルールとの類似度を求める
    vec.dist <- mat.df.dist[ind.merge.target.rule,] 
    
    # 異なる結論部のルールは除外
    vec.dist[!vec.same.consequents] <- -1
    
    # vec.distがすべて -1 = 異なる結論部のルールが無い場合は、そのind.merge.target.ruleは削除する
    if(all(vec.dist == -1)){
      rules.new <- rules.new[-c(ind.merge.target.rule)]
      vec.supportsize <- sapply(rules.new, function(rule){
        return(length(rule$support))
      })
      print("各ルールのsupport値:")
      print(vec.supportsize)
      minSupportValue <- min(vec.supportsize)
      
      # attributeをつける
      attr(rules.new, "uniqueCls") <- attributes(rules)$uniqueCls
      attr(rules.new, "clsProbs") <- attributes(rules)$clsProbs
      attr(rules.new, "majorityCls") <- attributes(rules)$majorityCls
      attr(rules.new, "method") <- "MLEM2Rules"
      attr(rules.new, "dec.attr") <- attributes(rules)$dec.attr
      attr(rules.new, "colnames") <- attributes(rules)$colnames
      
      # RuleSetRSTクラスを付与し、rulesの記述を指定フォーマットに変える
      rules.new <- My.ObjectFactory(rules.new, classname = "RuleSetRST")
      next
    }
    
    # merge target ルールと同じ条件属性のあるものを判定
    vec.judge.condition <- sapply(rules.new, function(rule){
      return(length(intersect(rule$idx, rules.new[[ind.merge.target.rule]]$idx)) > 0)
    })
    
    # vec.distを同じ条件属性のあるルールだけに限定して最大類似度を求める。しかし、同じ条件属性がない場合は、気にせずにマージする
    maxDistValue <- max(vec.dist[vec.judge.condition])
    if(maxDistValue == 0){
      maxDistValue <- max(vec.dist)
    }
    
    # 最も類似度が大きいルールを求める
    ind.maxDistValue <- which(vec.dist == maxDistValue)
    if(length(ind.maxDistValue) == 1){
      ind.merge.target.rule2 <- ind.maxDistValue
      rule.new <- mergeRules(rules.new[[ind.merge.target.rule]], rules.new[[ind.merge.target.rule2]])
    }else{
      # 結論部が同じルールかどうか
      vec.consequent <- sapply(ind.maxDistValue, function(x){
        return(rules.new[[x]]$consequent)
      })
      ind.maxConsequentValue <- ind.maxDistValue[vec.consequent == rules.new[[ind.merge.target.rule]]$consequent]
      # 結論部が同じルールが1つ
      if(length(ind.maxConsequentValue) == 1){
        ind.merge.target.rule2 <- ind.maxConsequentValue
        rule.new <- mergeRules(rules.new[[ind.merge.target.rule]], rules.new[[ind.merge.target.rule2]])
      # 結論部が同じルールが2つ以上 or ない
      }else{
        # ないなら、類似度が大きいルールを再度入れなおす
        if(length(ind.maxConsequentValue) == 0){
          ind.maxConsequentValue <- ind.maxDistValue
        }
        # 条件部を構成する属性名がなるべく同じであるか
        vec.match.length.idx <- sapply(ind.maxConsequentValue, function(x){
          return(length(intersect(rules.new[[x]]$idx, rules.new[[ind.merge.target.rule]]$idx)))
        })
        maxConditionValue <- max(vec.match.length.idx)
        ind.maxConditionValue <- ind.maxConsequentValue[vec.match.length.idx == maxConditionValue]
        if(length(ind.maxConditionValue) == 1){
          ind.merge.target.rule2 <- ind.maxConditionValue
          rule.new <- mergeRules(rules.new[[ind.merge.target.rule]], rules.new[[ind.merge.target.rule2]])
        }else{
          # support sizeが小さいルールとマージする
          vec.supportsize <- sapply(rules.new[ind.maxConditionValue], function(rule){
            return(length(rule$support))
          })
          minSupportValue <- min(vec.supportsize)
          ind.minSupportValue <- ind.maxConditionValue[which(vec.supportsize == minSupportValue)]
          if(length(ind.minSupportValue) == 1){
            ind.merge.target.rule2 <- ind.minSupportValue
            rule.new <- mergeRules(rules.new[[ind.merge.target.rule]], rules.new[[ind.merge.target.rule2]])
          }else{
            # なければ、候補ルールの中の最初のルールとマージする
            ind.merge.target.rule2 <- ind.minSupportValue[1]
            rule.new <- mergeRules(rules.new[[ind.merge.target.rule]], rules.new[[ind.merge.target.rule2]])
          }
        }
      }
    }
    rules.new <- rules.new[-c(ind.merge.target.rule, ind.merge.target.rule2)]
    rules.new <- list.append(rules.new, rule.new)
    vec.supportsize <- sapply(rules.new, function(rule){
      return(length(rule$support))
    })
    print("各ルールのsupport値:")
    print(vec.supportsize)
    minSupportValue <- min(vec.supportsize)
    
    # attributeをつける
    attr(rules.new, "uniqueCls") <- attributes(rules)$uniqueCls
    attr(rules.new, "clsProbs") <- attributes(rules)$clsProbs
    attr(rules.new, "majorityCls") <- attributes(rules)$majorityCls
    attr(rules.new, "method") <- "MLEM2Rules"
    attr(rules.new, "dec.attr") <- attributes(rules)$dec.attr
    attr(rules.new, "colnames") <- attributes(rules)$colnames
    
    # RuleSetRSTクラスを付与し、rulesの記述を指定フォーマットに変える
    rules.new <- My.ObjectFactory(rules.new, classname = "RuleSetRST")
  }
  return(rules.new)
}

   
   
        
# ========================================
# main
# ========================================
if __name__ == "__main__":

    FILENAME = 'hayes-roth'
    iter1 = 4
    iter2 = 5
    
    rules = mlem2.getRulesByMLEM2(FILENAME, iter1, iter2)
    
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table = getDecisionTable(filepath)
    colnames = mlem2.getColNames(decision_table)
    
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)
    list_judgeNominal = mlem2.getJudgeNominal(decision_table, list_nominal)
    
    rules_new = getRuleClusteringBySimilarity(rules, colnames, list_judgeNominal, k=3)




