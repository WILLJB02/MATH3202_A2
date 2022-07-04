#Given Data Stubs
IDCost = [177,142,155]

IDtoLVC = [
[14.4,55.2,62.1,57.0,42.4,80.7,63.7,8.8],
[46.6,5.9,58.1,78.2,77.7,55.3,14.4,63.6],
[66.7,68.0,8.9,24.0,39.6,29.2,55.9,61.5]
]

CCDPop = [4465,5912,5883,5588,3880,5093,3846,5408,3900,5720,4893,6215,5733,
          4136,5033,5941,5461,5621,3575,6481,4805,4574,5817,3738,4583]

CCDtoLVC = [
[19.9,0,0,0,0,0,0,18.0],
[7.7,0,0,0,0,0,0,16.9],
[18.4,23.7,0,0,0,0,0,0],
[0,14.8,0,0,0,0,33.5,0],
[0,14.7,0,0,0,0,20.6,0],
[0,0,0,0,28.7,0,0,15.4],
[8.8,0,0,0,0,0,0,15.1],
[27.7,23.5,0,0,0,0,25.9,0],
[0,13.2,0,0,0,0,18.5,0],
[0,25.9,0,0,0,0,14.4,0],
[0,0,0,30.7,14.2,0,0,19.7],
[30.8,0,0,0,20.4,0,0,19.3],
[0,0,21.2,0,0,0,35.2,0],
[0,0,29.2,0,0,27.2,17.9,0],
[0,0,0,0,0,27.7,23.5,0],
[0,0,0,11.4,9.5,0,0,0],
[0,0,24.5,5.9,17.7,0,0,0],
[0,0,10.8,18.8,29.7,0,0,0],
[0,0,20.9,0,0,12.5,31.2,0],
[0,0,0,0,0,14.0,35.2,0],
[0,0,0,18.8,27.5,0,0,0],
[0,0,0,9.4,25.2,0,0,0],
[0,0,16.8,28.5,0,30.0,0,0],
[0,0,24.0,0,0,21.9,0,0],
[0,0,36.6,0,0,14.9,0,0]
]

LVCUCost = [1414000,1246000,1598000,1606000,1967000,1339000,1403000,1365000]
LVCCloseC = [4471000,4211000,3220000,5533000,4362000,3547000,4938000,5339000]

from gurobipy import *

# Creating Model
m = Model("VaccineDistribution")

# Sets
ID = ["ID-A","ID-B","ID-C"] # Set of Import Depots 
LVC = [("LVC" + (str(i))) for i in range(8)] # Set of Local Vaccination Centres (LVC)
CCD = [str(i) for i in range(25)] # Set of Census Collection Districts (CCD)
D = {(ID[IDindex], LVC[LVCindex]) : DistL 
     for IDindex, lenghtList in enumerate(IDtoLVC) 
     for LVCindex, DistL in enumerate(lenghtList)} # Set of Vaccine Delivery Arcs from ID to LVC
R = {(CCD[CCDindex], LVC[LVCindex]) : DriveL
     for CCDindex, lengthList in enumerate(CCDtoLVC)
     for LVCindex, DriveL in enumerate(lengthList)
     if DriveL != 0} # Set of routes a citizen can travel along between CCDs and LVCs


# Data
ImportC = {"ID-A": 177, "ID-B": 142, "ID-C": 155} # Cost to import vaccines to i∈ID 
P = {CCD : CCDPop[index] for index, CCD in enumerate(CCD)} # Population of c∈C
DelC = 0.2 # Cost to deliver vaccines from an ID to an LVC per kilometre per dose
"DelL = D[d] for d element D" # Length in kilometres of d∈D
"o = d[0] for d element D" # Origin ID of vaccine travelling along d∈D
"v = d[1] for d element D" # Destination of vaccine travelling along d∈D
"DriveL = R[r] for r element R" # Length in kilometres of r∈R
DriveC = 1 # Cost per kilometre for a citizen to travel
"t = r[1] for r element R" # LVC that a citizen is travelling too along r∈R
"f = r[0] for r element R" # CCD that a citizen is travelling from along  r∈R
Cap = 51000 # Capacity of Vaccines which can be stored at an ID
AMax = 15000 # Maximum number of vaccine doses which can be administered at an LVC
UpgradeC = {LVC : LVCUCost[index] for index, LVC in enumerate(LVC)} # Cost to upgrade the maximum dosage administered at l∈LVC
Increase = 7500 # How much the capacity of l∈LVC increases if upgraded
CloseC = {LVC : LVCCloseC[index] for index, LVC in enumerate(LVC)} # Cost savings when l∈LVC is closed. 
M = 6481 # The maximum population of all CCD’s


#Variables
X = {d: m.addVar() for d in D} # Number of vaccine doses being delivered along d∈D
Y = {i: m.addVar() for i in ID} # Number of vaccine doses being imported to i∈ID
Z = {r: m.addVar() for r in R} # Number of citizens travelling to get their vaccine along r∈R 
S = {l: m.addVar() for l in LVC} # Number of vaccine doses stored at l∈LVC
U = {l: m.addVar(vtype=GRB.BINARY) for l in LVC} # 1, if the capacity of l∈LVC will be upgraded  :  0, otherwise
C = {l: m.addVar(vtype=GRB.BINARY) for l in LVC} # 1, if l∈LVC has been closed  :  0, otherwise
A = {r: m.addVar(vtype=GRB.BINARY) for r in R} # 1, if citizens are allowed to travel along r∈R to get their vaccines  : 0, otherwise


#Objective
m.setObjective(quicksum(ImportC[i]*Y[i] for i in ID) + 
               quicksum(DelC * D[d] * X[d] for d in D) + 
               quicksum(DriveC * R[r] * Z[r] for r in R) +
               quicksum(UpgradeC[l]*U[l] for l in LVC) -
               quicksum(CloseC[l]*C[l] for l in LVC), 
               GRB.MINIMIZE)

#Constraints
for i in ID:
    m.addConstr(Y[i] <= Cap) # imported doses dosent exceed capacity
    m.addConstr(quicksum(X[d] for d in D if d[0] == i) <= Y[i]) # vaccines leaving ID does not exceed amount imported
    
for l in LVC:
    m.addConstr(S[l] ==  quicksum(X[d] for d in D if d[1] == l) 
                - quicksum(Z[r] for r in R if r[1] == l)) # stored vaccines equals incoming minus outgoing
    m.addConstr(U[l] + C[l] <= 1 ) # LVC cannot be both closed and upgraded
    m.addConstr(quicksum(Z[r] for r in R if r[1] == l) 
                <= AMax*(1-C[l]) + Increase*U[l]) # vaccines leaving is less than LVC capacity 
                                                  # depending on if it's closed or upgraded or unchanged

for c in CCD:
        m.addConstr(quicksum(Z[r] for r in R if r[0] == c) == P[c]) # ensuring entire population is vaccinated
        m.addConstr(quicksum(A[r] for r in R if r[0] == c) == 1) # Citizens can only go to once LVC

for r in R:
    m.addConstr(Z[r] <= M*A[r]) # if a route is closed, no citizens can travel along it
    
    
#Optimizing
m.optimize()



#Showing Results
print("\n\n----------------------------------------------------")
print("Optimized Distribution Cost: " + str(m.objVal))

print("----------------------------------------------------")
print("Number of Vaccines imported to IDs:")
for i in ID:
    print(str(i) + ": " + str((Y[i].x)))
    
print("----------------------------------------------------")   
print("Vaccine Distribution from ID to LVC:")
print('{0:<20} {1}'.format("(ID, LVC)", "Distributed"))
for d in D:
    if X[d].x != 0:
        print('{0:<20} {1}'.format(str(d), str(round((X[d].x),1))))
        
print("----------------------------------------------------")   
print("LVC's Upgraded/Closed")
print('{0:<10} {1:<10} {2}'.format("LVC", "Upgraded", "Closed"))
for l in LVC:
    print('{0:<10} {1:<10} {2}'.format(str(l), str(int(U[l].x)), str(int(C[l].x))))
    
print("----------------------------------------------------")   
print("Vaccine Adminstration:")
print('{0:<10} {1}'.format("LVC", "Administerd"))
for l in LVC:
    a = 0
    for r in R:
        if r[1] == l:
            a = a + Z[r].x
    print('{0:<10} {1}'.format(str(l), str(round(a,1))))
    
print("----------------------------------------------------")   
print("LVC that CCD goes Too")
print('{0:<6} {1:<6} {2}'.format("CCD", "LVC", "Citizens"))
for r in R:
    if A[r].x == 1:
        print('{0:<6} {1:<6} {2}'.format(str(r[0]), str(r[1]), str(round(Z[r].x,1))))
