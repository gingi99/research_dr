# coding: utf-8
from collections import defaultdict
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
       #if not self.value[key] : self.value[key] = [val]
       #else : self.value[key].append(val)
       if type(val) == str :
           if val in self.value[key] : pass
           else : self.value[key].append(val)
       elif type(val) == list :
           self.value[key] = union(self.value[key],val)
       elif type(val) == tuple :
           print("tuple ha mada")
   def setConsequent(self, consequents) :
       #if not self.consequent :
       #    self.consequent = consequents
       #else :
       #    self.consequent = union(self.consequent, consequents)
       if consequents in self.consequent : pass
       else : self.consequent.append(consequents)
   def setSupport(self, supports) :
       if not self.support :
           self.support = supports
       else :
           self.support = intersect(self.support, supports)
   def getKey(self) :
       return(list(self.value.keys()))
   def getValue(self, idx, onecase=True) :
       if not idx in self.getKey():
           return(None)
       else:
           i = iter(self.value[idx])
           if any(i) and not any(i) and onecase : return(self.value[idx][0])
           else : return(self.value[idx])
   # consequent = 0 のときうまくいかない
   def getConsequent(self) :
       i = iter(self.consequent)
       if any(i) and not any(i) : return(self.consequent[0])
       else : return(self.consequent)
   def getSupport(self) :
       return(sorted(self.support))
   def getSupportD(self) :
       return(len(self.support) * len(self.getKey()))
   def delKey(self, key) :
       self.value.pop(key, None)
   def output(self) :
       print("value:" + str(self.value))
       print("consequent:" + str(self.consequent))
       print("support:" + str(self.support))
