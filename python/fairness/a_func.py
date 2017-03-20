import numpy as np
from copy import deepcopy

# delta
def getDelataByExclude(a,b,c,d) :
    delta = (a * d - b * c) / (d)
    return(delta)
def getDelataByDel(a,b,c,d) :
    delta = (a * d - b * c) / (c + d)
    return(delta)

# 低サポートのRulesをn個減らす関数
def excludeSmallStrengthRulesRapper(list_rules, n, dict_attribute_value, list_bad_cls):
    tmp_rules = deepcopy(list_rules)
    for attr in dict_attribute_value.keys():
        for v in dict_attribute_value[attr] :
            tmp_rules = excludeSmallStrengthRules(tmp_rules, n, attr, v, list_bad_cls)     
    return(tmp_rules)
def excludeSmallStrengthRules(list_rules, n, attr, v, list_bad_cls):
    rules = deepcopy(list_rules)
    list_index_cls = [i for i,r in enumerate(rules) if r.getValue(attr) == v and r.getConsequent() in list_bad_cls]
    list_index_noncls = [i for i,r in enumerate(rules) if not i in list_index_cls]
    rules_cls = [rules[i] for i in list_index_cls]
    rules_noncls = [rules[i] for i in list_index_noncls]
    list_strength = [len(r.getSupport()) for r in rules_cls]
    if len(list_strength) == n :
        list_del_index = np.arange(n)
    else : 
        list_del_index = np.argpartition(list_strength, n)[:n]
    new_rules_cls = list(np.delete(rules_cls, list_del_index))
    new_rules = rules_noncls + new_rules_cls   
    return(new_rules)

# Rulesのうちある基本条件をn個減らす関数
def delSmallStrengthRulesRapper(list_rules, n, dict_attribute_value, list_bad_cls):
    tmp_rules = deepcopy(list_rules)
    for attr in dict_attribute_value.keys():
        for v in dict_attribute_value[attr] :
            tmp_rules = delSmallStrengthRules(tmp_rules, n, attr, v, list_bad_cls)     
    return(tmp_rules)
def delSmallStrengthRules(list_rules, n, attr, v, list_bad_cls):
    rules = deepcopy(list_rules)
    list_index_cls = [i for i,r in enumerate(rules) if r.getValue(attr) == v and r.getConsequent() in list_bad_cls]
    list_index_noncls = [i for i,r in enumerate(rules) if not i in list_index_cls]
    rules_cls = [rules[i] for i in list_index_cls]
    rules_noncls = [rules[i] for i in list_index_noncls]
    list_strength = [len(r.getSupport()) for r in rules_cls]
    if len(list_strength) == n :
        list_del_index = np.arange(n)
    else : 
        list_del_index = np.argpartition(list_strength, n)[:n]
    for i in list_del_index :
        rules_cls[i].delKey(attr)
    new_rules = rules_noncls + rules_cls
    return(new_rules)
