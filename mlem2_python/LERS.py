# coding: utf-8
# python 3.5
from itertools import compress
from sklearn.metrics import accuracy_score
import mlem2

# =====================================
# list a が b に包含されているかを判定する
# =====================================
def isSuperList(list_a, list_b) :
    return(set(list_b).issuperset(set(list_a)))


# ====================================
# Ruleの1つの条件部が対象を説明するかどうか
# ====================================
def isExplainNominalCondition(obj, rule, attr):
    if isSuperList(obj[attr], rule.getValue(attr)):
        return(True)
    else :
        return(False)

# ====================================
# Ruleの1つの条件部が対象を説明するかどうか
# ====================================
def isExplainNumericalCondition(obj, rule, attr):
    if rule.getValue(attr)[0] <= obj[attr] <= rule.getValue(attr)[1] :
        return(True)
    else :
        return(False)

# ====================================
# Ruleが対象を説明するかどうか
# ====================================
def isExplainRule(obj, rule, list_judgeNominal) :
    attributes = rule.getKey()
    for attr in attributes :
        # nominal なら
        if list_judgeNominal[attr] :
            isExplain = isExplainNominalCondition(obj, rule, attr)  
        # numerical なら
        else :
            isExplain = isExplainNumericalCondition(obj, rule, attr)  
        # 説明できないならFalse        
        if not isExplain :
            return(False)
    return(True)

# ====================================
# Ruleが対象の条件にマッチする割合(matching_factor)
# ====================================
def getMatchingFactor(obj, rule, list_judgeNominal) :
    matching_factor = 0
    attributes = rule.getKey()
    for attr in attributes :
        # nominal なら
        if list_judgeNominal[attr] :
            isExplain = isExplainNominalCondition(obj, rule, attr)  
        # numerical なら
        else :
            isExplain = isExplainNumericalCondition(obj, rule, attr)  
        # 説明できたら+1        
        if isExplain :
            matching_factor += 1
    matching_factor = matching_factor / len(attributes)      
    return(matching_factor)


# ====================================
# rulesからsupportDを求める
# ====================================
def getSupportD(rule) :
    return(len(rule.getSupport()) * len(rule.getKey()))
    
# ====================================
# rulesからsupportPを求める
# ====================================
def getSupportP(obj, rule, list_judgeNominal) :
    matching_factor = getMatchingFactor(obj, rule, list_judgeNominal)
    return(len(rule.getSupport()) * len(rule.getKey()) * matching_factor)
            
# ====================================
# 1 対象のクラスを予測する
# ====================================
def predictClass(obj, rules, list_judgeNominal) :
    list_judge = [isExplainRule(obj, r, list_judgeNominal) for r in rules]
    # 1つ以上マッチするなら
    if any(list_judge) :  
      consequents = [rules[i].getConsequent() for i, judge in enumerate(list_judge) if judge] 
      # マッチしたルールが推論するクラスの数がただ1つなら
      if len(set(consequents)) == 1 :
          return(consequents[0])
      else :
          rules_match = list(compress(rules,list_judge))
          supportD = [getSupportD(r) for r in rules_match]
          return(rules_match[supportD.index(max(supportD))].getConsequent())
    # rule が objに1つもマッチしない場合は部分一致ルールによる推定
    else : 
        supportP = [getSupportP(obj, rule, list_judgeNominal) for rule in rules]
        return(rules[supportP.index(max(supportP))].getConsequent())
        
# ====================================
# LERSによるクラス推定
# ====================================
def predictByLERS(rules, decision_table_test, list_judgeNominal) :
      
    # decision_table_testの型を正しくする
    nominals = list(compress(decision_table_test.columns.tolist(),list_judgeNominal))
    decision_table_test[nominals] = decision_table_test[nominals].astype(str)
      
    # 各行に対して予
    predictions = decision_table_test.apply(lambda obj: predictClass(obj, rules, list_judgeNominal), axis=1)    
        
    # predictionsの型を正しくする
    predictions = predictions.tolist()    
        
    return(predictions)
    
# ========================================
# main
# ========================================
if __name__ == "__main__":

    FILENAME = 'hayes-roth'
    iter1 = 7
    iter2 = 5
    
    # rule induction
    rules = mlem2.getRulesByMLEM2(FILENAME, iter1, iter2)

    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-test'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table_test = mlem2.getDecisionTable(filepath)
    decision_table_test = decision_table_test.dropna()
    decision_class = decision_table_test[decision_table_test.columns[-1]].values.tolist()

    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)
    list_judgeNominal = mlem2.getJudgeNominal(decision_table_test, list_nominal)
    
    # predict by LERS
    predictions = predictByLERS(rules, decision_table_test, list_judgeNominal)
    
    # 正答率を求める
    accuracy_score(decision_class, predictions)    
