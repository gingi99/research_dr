# coding: utf-8
# Confirmation Measure

# ----------------------------
# P(H|E) - P(H)
# ----------------------------
def D(a,b,c,d):
    if a+c == 0 :
       return(-1 * (a+b)/(a+b+c+d))
    else :
       return(a/(a+c) - (a+b)/(a+b+c+d))

# ----------------------------
# P(H|E) - P(H|not E)
# ----------------------------
def S(a,b,c,d):
    if a+c == 0 and b+d == 0:
       return(0)
    if a+c == 0 :
       return(-1 *  b / (b+d))
    elif b+d == 0 :
       return(a/(a+c))
    else :
       return(a/(a+c) - b/(b+d))

# ----------------------------
# P(E|H) - P(E)
# ----------------------------
def M(a,b,c,d):
    if a+b == 0 :
       return(-1 * (a+c)/(a+b+c+d))
    else :
       return(a/(a+b) - (a+c)/(a+b+c+d))

# ----------------------------
# P(EH) - P(E)P(H)
# ----------------------------
def C(a,b,c,d):
    return(a/(a+b+c+d) - (a+c)*(a+b)/((a+b+c+d)*(a+b+c+d)))


