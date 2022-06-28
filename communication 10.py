from gurobipy import *

from math import *

import matplotlib.pyplot as plt


#Given data stubs
ECost = [
[53000,122000,242000,400000],
[69000,110000,248000,435000],
[62000,135000,205000,449000],
[70000,136000,205000,454000],
[54000,140000,237000,431000],
[69000,129000,219000,441000],
[65000,114000,250000,435000],
[57000,122000,239000,469000],
[61000,105000,212000,455000],
[67000,116000,245000,472000],
[62000,111000,258000,416000],
[50000,118000,245000,445000],
[55000,120000,202000,435000],
[61000,120000,231000,440000],
[51000,130000,201000,470000],
[59000,115000,218000,404000],
[63000,125000,222000,462000],
[67000,120000,256000,418000],
[67000,120000,221000,443000],
[61000,119000,250000,456000],
[66000,125000,222000,465000],
[70000,109000,200000,433000],
[69000,117000,203000,448000],
[69000,125000,218000,424000],
[66000,140000,255000,428000]
]

#supressing gurobi's output
env = Env(empty=True)
env.setParam("OutputFlag",0)
env.start()

#set of different budgets
Budgets = []
for i in range(300):
    Budgets.append(1700000+25000*i)
    
#corresponding maximum erradicaiton probability
EradicationProb = []

#specific budget examples
Budgets_Example = []
for i in range(10):
    Budgets_Example.append(6500000-500000*i)


#looping over each budget
for Budget in Budgets:
    
    #Creating Model
    m = Model("VaccineDistribution", env=env)
    
    #Sets
    CCD = [i for i in range(25)] # Set of Census Collection Districts (CCD)
    H = range(4) # Set of all Public Health Options to try and eradicate the virus 
    
    #Data
    "Budget = Budget from for loop" # Budget that can be used on public health options to try and eradicate the virus
    "ECost_(c,h) = ECost[c][h]" # Cost of using option h∈H in c∈CCD
    EProb = [0.95, 0.975, 0.99, 0.995] # Probability of option h∈H eradicating a virus in a given CCD
    
    #Variables
    X = {(c, h): m.addVar(vtype=GRB.BINARY) for c in CCD for h in H} # 1, if option h∈H should be used in c∈CCD  :  0, otherwise 
    LogP = m.addVar(lb=-GRB.INFINITY, ub=0) # The logarithm of the probability of eradication in Pacific Paradise
    
    #Objective
    m.setObjective(LogP, GRB.MAXIMIZE)
    
    #Contraints
    for c in CCD:
        m.addConstr(quicksum(X[c,h] for h in H) == 1) # only 1 health option is used in each CCD
    
    m.addConstr(quicksum(log(EProb[h]) * X[c,h] for c in CCD for h in H) == LogP) # log of total probablity is the 
                                                                                  # sum of indiviual probabilty logs
    
    m.addConstr(quicksum(ECost[c][h]*X[c,h] for c in CCD for h in H) <= Budget) # the implementation cost is less than the budget
    
    # Optimizing
    m.optimize()
    
    # Adding probability to Eradication List
    EradicationProb.append(exp(m.objVal))
    
    #Prinitng examples
    """
    if Budget in Budgets_Example:
        A  = [c for c in CCD if X[c, 0].x == 1]
        B  = [c for c in CCD if X[c, 1].x == 1]
        C  = [c for c in CCD if X[c, 2].x == 1]
        D  = [c for c in CCD if X[c, 3].x == 1]
        #print(Budget)
        #print('{0:<100} {1:<100} {2:<100} {3:<100} {54'.format(str(A), str(B), str(C), str(D)))
        #print(str(round(exp(m.objVal)*100,1)))
        cost = 0
        for c in CCD:
            for h in H:
                cost = cost + ECost[c][h]*X[c,h].x
        print(round(cost))
    """           
    
    
# plotting graph
plt.plot(Budgets, EradicationProb) 
plt.xlabel("Budget ($)")
plt.ylabel("Maximum Eradication Probability")
plt.title("Budget vs Maximum Eradication Probability")
    
        
        
        
        