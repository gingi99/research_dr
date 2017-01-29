# coding: utf-8
from collections import defaultdict

# =====================================
# Rules のうち 指定したConsequentを持つ / 持たないRuleの数
# =====================================
def getNumRulesClass(list_rules, consequent, judge=True):
    if judge : rules = [r for r in list_rules if r.getConsequent() == consequent]
    else : rules = [r for r in list_rules if r.getConsequent() != consequent]
    return(len(rules))

# =====================================
# Rules の Supportの平均数
# =====================================
def getMeanSupport(list_rules, only_avg = True) :
    supports = [len(r.getSupport()) for r in list_rules]
    if only_avg :
        ans = np.mean(supports)
    else :
        ans = '{mean}±{std}'.format(mean=('%.3f' % round(np.mean(supports),3)), std=('%.3f' % round(np.std(supports),3)))
    return(ans)

# =====================================
# Rules の Supportの最小値
# =====================================
def getMinSupport(list_rules) :
    supports = [len(r.getSupport()) for r in list_rules]
    ans = np.min(supports)
    return(ans)

# =====================================
# Rules の Ruleの長さの平均数
# =====================================
def getMeanLength(list_rules, only_avg = True) :
    lengths = [len(r.getKey()) for r in list_rules]
    if only_avg :
        ans = np.mean(lengths)
    else :
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
# Rules のうち Suppprt = n の割合
# =====================================
def getPerNSupport(list_rules, n) :
    n_rules = [r for r in list_rules if len(r.getSupport()) == n]
    ans = len(n_rules) / len(list_rules)
    return(ans)

# =====================================
# Rules を構成する基本条件の頻度
# =====================================
def getRulesValueCount(list_rules) :
    rules_stat_value_count = defaultdict(dict)
    for r in list_rules:
        attrs = r.getKey()
        for attr in attrs:
            value = r.getValue(attr)
            if not attr in rules_stat_value_count or not value in rules_stat_value_count[attr]:
                rules_stat_value_count[attr].update({value : 1})
            else :
                rules_stat_value_count[attr][value] += 1
    return(rules_stat_value_count)
