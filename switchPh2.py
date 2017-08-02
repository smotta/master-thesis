# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 12:43:42 2017

@author: Sergio

This will be the script to store all the functions necessary for the switching - phase 2
"""

import model as md
#from main import inverters, batlist

#%% 
##### SWITCHING FUNCTION IMPLEMENTED #####
def switchingPhase2(inverters, batlist):
    """Function to implement the switching phase 2 as described in 
    'Schakelschema Herman Fase 2 v0.2.1 (English).pdf"""
    
    
    #creating the possible outcomes
    global outcomes
    outcomes = md.np.zeros((len(inverters), 7, len(inverters[0].timestamp)))
    
    #Creating the arrays to split the energy that is directed towards each apartment into used energy, fed to the grid and to the battery
    #print("Creating the energy received vectors...")
    for i in inverters:
        i.switchtime = []
        for j in i.apartments:
            j.energyreceived = md.np.zeros(len(j.timestamp))
            j.gridfeedin = md.np.zeros(len(j.timestamp))
            j.batcharge = md.np.zeros(len(j.timestamp))
            j.batdischarge = md.np.zeros(len(j.timestamp))
            j.griduse_new = j.consumption[:]
            j.energyreceivedtotal = 0
            j.selfC_new = 0
            j.selfCinst_new = md.np.zeros(len(j.timestamp))
            j.selfS_new = 0
            j.selfSinst_new = md.np.zeros(len(j.timestamp))
     
    for i in batlist:
        i.chargeArray = md.np.zeros(len(i.chargeArray))
        i.chargeStatus = md.np.ones(len(i.chargeStatus))*i.depthDisch
        i.chargeRate = md.np.zeros(len(i.chargeStatus))
    
    
    #Calculating the number of switches that happen in the full switching phase
    global numberswitches
    numberswitches = 0
    #Running the switching based on functions
    for i in range(len(inverters)):
        global selected
        selected = 0
        for j in range(len(inverters[i].timestamp)):
            checkPV(i, j, inverters, batlist)
            
            
    #Recalculating the self-consumption and self-sufficiency of each apartment
    #Change mode to All for calculation of instantaneous self-consumption
    recalculateSelfCselfS(inverters, batlist, mode="All")
    
    return outcomes, numberswitches

#%%%
##### SWITCHING FUNCTIONS #####


#Top function in the hierarchy - checks if there is PV generation at the time:
def checkPV(i, j, inverters, batlist):
        if inverters[i].generation[j] > 0.001:
            #If there is generation at the moment, it checks if the load is higher than the generation
            checkLoadPV(i, j,  inverters, batlist)
        else:
            #If there is not, it goes to the flow without PV
            checkBatDischarge_noPV(i, j, inverters, batlist)

####### PV generation present ##########
#Check if the load of the currently selected apartment is higher than the generation or not:
def checkLoadPV(i, j, inverters, batlist):
    if inverters[i].apartments[selected].consumption[j] > inverters[i].generation[j]:
        #If the load is higher than the PV generation, the battery will be drained
        checkBatDischarge_PV(i, j, inverters, batlist)
    else:
        #If the load is smaller than the generation, we check for higher loads at the time
        switchHighDemand_PV(i, j, inverters, batlist)
        
#Check the battery charge level when there is PV if it can be discharged:
def checkBatDischarge_PV(i, j, inverters, batlist):
    if batlist[i].chargeStatus[j-1] > batlist[i].depthDisch:
        #If the battery can be drained, we have Outcome 1
        outcome(0, i, j, inverters, batlist)
    else:
        #If the battery is "empty", Outcome 2 yields
        outcome(1, i, j, inverters, batlist)
        
#Checks if the selected apartment has the higherst demand at a given time:        
def switchHighDemand_PV(i, j, inverters, batlist):
    global selected; global numberswitches
    if selected != inverters[i].consumption_perAp[j].index(max(inverters[i].consumption_perAp[j])):
        selectedprevious = selected
        numberswitches += 1
        #If the demand is not the highest at the time, the switching occurs to the highest load, and the check if it is higher than the PV happens
        selected = inverters[i].consumption_perAp[j].index(max(inverters[i].consumption_perAp[j]))
        inverters[i].switchtime.append((j, inverters[i].timestamp[j], selectedprevious, selected, "high demand and PV"))  #append the time which the switch happened and the positions before-after
        checkLoadPV(i, j, inverters, batlist)
    else:
        #If the load is already the highest, but still lower than the generation, the battery will be charged
        checkBatCharge(i, j, inverters, batlist)
        
#Check the battery charge level when there is PV if it can still be charged:
def checkBatCharge(i, j, inverters, batlist):
    if batlist[i].chargeStatus[j-1] < batlist[i].capacity:
        #If the battery is not at full capacity, Outcome 3 will happen
        outcome(2, i, j, inverters, batlist)
    else:
        #If the battery is already at full capacity, Outcome 4 follows
        outcome(3, i, j, inverters, batlist)
        
  
    
    
    
####### No PV generation ##########    

#When there is no PV, check if there is battery charge
def checkBatDischarge_noPV(i, j, inverters, batlist):
    if batlist[i].chargeStatus[j-1] > batlist[i].depthDisch:
        #if there is battery charge, checks if the load of the currently selected apartment is higher
        checkLoadBat(i, j,  inverters, batlist)
    else:
        #if there is no charge, setup the switch to the apartment that received the least energy
        switchLowestER_noBat(i, j, inverters, batlist)
        
#Check if the battery charge is enough to cover the load    
def checkLoadBat(i, j, inverters, batlist):
    if (batlist[i].chargeStatus[j-1] - batlist[i].depthDisch) > inverters[i].apartments[selected].consumption[j]:
        #if the battery charge is enough to cover the load, check if the load is the highest
        switchHighDemand_noPV(i, j, inverters, batlist)
    else:
        #if the load is higher than the battery level, search for the apartment that received the least amount of energy
        switchLowestER(i, j, inverters, batlist)
        
#Check if the demand of the selected apartment is the highest
def switchHighDemand_noPV(i, j, inverters, batlist):
    global selected; global numberswitches
    if selected != inverters[i].consumption_perAp[j].index(max(inverters[i].consumption_perAp[j])):
        selectedprevious = selected
        numberswitches += 1
        #If the demand is not the highest at the time, the switching occurs to the highest load, and the battery supplies energy to this apartment
        selected = inverters[i].consumption_perAp[j].index(max(inverters[i].consumption_perAp[j])) 
        inverters[i].switchtime.append((j, inverters[i].timestamp[j], selectedprevious, selected, "high demand no PV"))  #append the time which the switch happened and the positions before-after
        checkBatRate(i, j, inverters, batlist)
    else:
        #If the demand is already the highest, we go directly to the battery supply
        checkBatRate(i, j, inverters, batlist)
        
        
#Check if the battery rate is higher or lower than the demand
def checkBatRate(i, j, inverters, batlist):
    if batlist[i].cRate < inverters[i].apartments[selected].consumption[j]:
        #if the c-Rate is lower than the demand, we need the grid support
        outcome(4, i, j, inverters, batlist)
    else:
        #if c-Rate is higher than the demand - we can supply all the demand from the battery
        outcome(5, i, j, inverters, batlist)
        
        
#Switch to the lowest energy received apartment
def switchLowestER(i, j, inverters, batlist):
    lowest = findLowestER(i, j, inverters)
    global selected; global numberswitches
    if inverters[i].apartments[lowest].consumption[j] > batlist[i].chargeStatus[j-1]:
        #if the lowest receiver can use all the charge in the battery
        inverters[i].switchtime.append((j, inverters[i].timestamp[j], selected, lowest, "lowest ER"))  #append the time which the switch happened and the positions before-after
        selected = lowest
        numberswitches += 1
        checkBatRate(i, j, inverters, batlist)
    else:
        #the lowest receiver does not use the full energy stored in the battery, nothing happens
        checkBatRate(i, j, inverters, batlist)
        
        
#Switch to the apartment that received the lowest amount of energy
def switchLowestER_noBat(i, j,inverters, batlist):
    lowest = findLowestER(i, j, inverters)
    global selected; global numberswitches
    inverters[i].switchtime.append((j, inverters[i].timestamp[j], selected, lowest, "lowest ER no bat"))  #append the time which the switch happened and the positions before-after
    selected = lowest
    numberswitches += 1
    outcome(6, i, j, inverters, batlist)     
        


def findLowestER(i, j, inverters):
    
    ERaparts = list(md.np.zeros(len(inverters[i].apartments)))
    for k in range(len(inverters[i].apartments)):
        ERaparts[k] = inverters[i].apartments[k].energyreceivedtotal
           
    lowest = ERaparts.index(min(ERaparts))
    return lowest        
        
###############################################################################   
#Outcome function to define each situation's ourcome:
def outcome(situation, i, j, inverters, batlist):
    
    #Registering the outcome
    global outcomes
    outcomes[i][situation][j] = 1
    
    if situation == 0:
        """Load > PV; BatLVL > limit
        PV + Battery go to the load, no feed-in, possible griduse"""
      
        #energy supplied by the battery is the lowest between the c-rate, remaining charge and difference between consumption and generation
        batenergy = min(batlist[i].cRate, (batlist[i].chargeStatus[j-1] - batlist[i].depthDisch), 
                        abs(inverters[i].generation[j] - inverters[i].apartments[selected].consumption[j]))
      
        #energy received by the apartment is the sum of the PV + batenergy
        inverters[i].apartments[selected].energyreceived[j] = inverters[i].generation[j] + batenergy
        inverters[i].apartments[selected].energyreceivedtotal += inverters[i].apartments[selected].energyreceived[j]
        #battery is being discharged by batenergy
        inverters[i].apartments[selected].batdischarge[j] = -batenergy
        #energy taken from the grid to supplement the demand
        inverters[i].apartments[selected].griduse_new[j] = (inverters[i].apartments[selected].consumption[j] - \
                                                            inverters[i].apartments[selected].energyreceived[j])
      
        #battery is being affected as
        batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1] - batenergy
        batlist[i].chargeArray[j] = -1 #discharge
        batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1] #should be -batenergy
      
    elif situation == 1:
        """Load > PV; BatLVL < limit
        PV to the load, no feed-in and no battery discharge"""
        
        #energy supplied by the battery is zero, so no batenergy is calculated
        
        #energy received by the apartment is only the PV system and the grid
        inverters[i].apartments[selected].energyreceived[j] = inverters[i].generation[j]
        inverters[i].apartments[selected].energyreceivedtotal += inverters[i].apartments[selected].energyreceived[j]

        #griduse to supplement for the PV generation
        inverters[i].apartments[selected].griduse_new[j] = (inverters[i].apartments[selected].consumption[j] - \
                                                            inverters[i].apartments[selected].energyreceived[j])
    
        #battery is being affected as
        batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1]
        batlist[i].chargeArray[j] = 0   #no action
        batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]

    elif situation == 2:
        """Load < PV; BatLVL < capacity
        PV goes to the load + battery, possible feed-in, no griduse"""
        
        #energy is being supplied TO the battery now, at a rate as the minimum between the c-Rate, remaining capacity and the surplus energy

        #energy received by the apartment is exactly its demand
        inverters[i].apartments[selected].energyreceived[j] = inverters[i].apartments[selected].consumption[j]
        inverters[i].apartments[selected].energyreceivedtotal += inverters[i].apartments[selected].energyreceived[j]

        #griduse is zero as the whole demand is being met by the generation
        inverters[i].apartments[selected].griduse_new[j] = 0
        #the apartment is charging the battery now as the minimum between the c-Rate, the remaining capacity and the surplus energy
        inverters[i].apartments[selected].batcharge[j] =  min(batlist[i].cRate, (batlist[i].capacity - batlist[i].chargeStatus[j-1]), 
                 (inverters[i].generation[j] - inverters[i].apartments[selected].energyreceived[j]))
        #the apartment sends energy to the grid as the generation - used energy - energy that goes to the battery
        inverters[i].apartments[selected].gridfeedin[j] = (inverters[i].generation[j] - inverters[i].apartments[selected].energyreceived[j] - 
                                                             inverters[i].apartments[selected].batcharge[j])
        #battery being affected as
        batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1] + inverters[i].apartments[selected].batcharge[j]
        batlist[i].chargeArray[j] = 1 #charge
        batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
        
    elif situation == 3:
        """Load < PV; BatLVL = capacity
        PV goes to the load, the battery is fully charged; feed-in, no griduse"""
        
        #no energy is supplied or extracted from the battery
        
        #energy received by the apartment is exactly its demand
        inverters[i].apartments[selected].energyreceived[j] = inverters[i].apartments[selected].consumption[j]
        inverters[i].apartments[selected].energyreceivedtotal += inverters[i].apartments[selected].energyreceived[j]

        #griduse is zero as the whole demand is being met by the generation
        inverters[i].apartments[selected].griduse_new[j] = 0
        #the apartment does not charge the battery;
        #the apartment sends energy to the grid as the generation - used energy; no battery charging occurs
        inverters[i].apartments[selected].gridfeedin[j] = (inverters[i].generation[j] - inverters[i].apartments[selected].energyreceived[j])
        
        #battery being affected as
        batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1]
        batlist[i].chargeArray[j] = 0 #no action
        batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
        
        
    elif situation == 4:
        """ No PV; BatLVL> 0; c-Rate < demand
        Battery goes to the load; grid goes to the load"""
        
        #energy is supplied by the battery is the minimum between the remaining charge of the battery and its c-Rate
        batenergy = min(batlist[i].cRate, (batlist[i].chargeStatus[j-1] - batlist[i].depthDisch))
        
        #energy received by the apartment comes from the battery
        inverters[i].apartments[selected].energyreceived[j] = batenergy
        inverters[i].apartments[selected].energyreceivedtotal += inverters[i].apartments[selected].energyreceived[j]

        #the relation with the battery is also the energy supplied by it, but as a discharge (negative)
        inverters[i].apartments[selected].batdischarge[j] = -batenergy
        #the griduse to supplement the battery is given as
        inverters[i].apartments[selected].griduse_new[j] = inverters[i].apartments[selected].consumption[j] - inverters[i].apartments[selected].energyreceived[j]
        #there is no grid feedin
        
        #battery being affected as
        batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1] - batenergy
        batlist[i].chargeArray[j] = -1 #discharge
        batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
        
    elif situation == 5:
        """No PV; BatLVL > 0; c-Rate > demand
        Battery has a c-Rate high enough to supply the demand, but we don't know about the charge. maybe grid support is needed"""
        
        #energy is supplied by the battery is the minimum between the remaining charge and the demand (we already know the c-Rate is higher than the demand)
        batenergy = min((batlist[i].chargeStatus[j-1] - batlist[i].depthDisch), inverters[i].apartments[selected].consumption[j])
        
        #energy received comes from the battery
        inverters[i].apartments[selected].energyreceived[j] = batenergy
        inverters[i].apartments[selected].energyreceivedtotal += inverters[i].apartments[selected].energyreceived[j]

        #the relation with the battery is the energy supplied by it, as a discharge
        inverters[i].apartments[selected].batdischarge[j] = -batenergy
        #Nowe we don't know if there is need for the grid yet, as the demand can be higher than the battery charge.
        #If energy received is smaller than consumption, it was because the remaining charge was smaller than the demand.
        inverters[i].apartments[selected].griduse_new[j] = max(0, 
                 (inverters[i].apartments[selected].consumption[j] - inverters[i].apartments[selected].energyreceived[j]))
        #there is no grid feedin
        
        #battery being affected as
        batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1] - batenergy
        batlist[i].chargeArray[j] = -1 #discharge
        batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
        
        
    elif situation == 6:
        """No PV; No battery charge; 
        Grid directly supplying the apartment that received the lowest amount of energy"""
        
        #There is no energy being supplied by or to the battery
        
        #There is no energy eing received
        #There is just griduse in this case
        inverters[i].apartments[selected].griduse_new[j] = inverters[i].apartments[selected].consumption[j]
        
        #battery being affected as
        batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1]
        batlist[i].chargeArray[j] = 0 #no action
        batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
        
    else:
        print("No situation described")
        return 0
    
    
    
    
    
    
    
    
    
#%%  
#Defining a function to add the batteries to the system    
    
def addBatteries(inverters, capacity, cRate, mode="None"):
    """Function to add the batteries to the system, as it is created without any by default on the main file"""
    
    batlist = []
    for i in inverters:
        batlist.append(md.Battery(i, capacity, cRate))
     
    if mode == "Apt":
        for i in inverters:
            for ap in i.apartments:
                batlist.append(md.Battery(ap, capacity, cRate))
                
    #bypassing the battery model into new null arrays that will be determined by the switching logic
    #TO DO - change the initalization of the batteries so this becomes obsolete
    for i in batlist:
        i.chargeArray = md.np.zeros(len(i.chargeArray))
        i.chargeStatus = md.np.zeros(len(i.chargeStatus))
        i.chargeRate = md.np.zeros(len(i.chargeStatus))
        
    return batlist
    
    
#Defining a function to recalculate self-consumption and self-sufficiency

def recalculateSelfCselfS(inverters, batlist, mode="All"):
        
    for i in range(len(inverters)):
        for j in inverters[i].apartments:
            j.selfC_new = md.selfConsumption(j.consumption, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i])
            j.selfS_new = md.selfSufficiency(j.consumption, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i])
            if mode == "All":
                j.selfCinst_new = md.selfConsumptionInst(j.consumption, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i])
                j.selfSinst_new = md.selfSufficiencyInst(j.consumption, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i])

    
    
    
