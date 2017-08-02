# -*- coding: utf-8 -*-
"""
Created on Wed Aug  2 09:51:44 2017

@author: Sergio

Script to implement Switching Phase III
"""

import model as md

import sysanalysis as sa
#%%
##### IMPLEMENTING SWITCHING PHASE III #####

def switchingPhase3(inverters, batlist, batteryplace, applianceID):
    """Function to implement the switching phase 3 as described in 
    'Schakelschema Herman Fase 3 v0.2.1 (English).pdf"""
    
    
    #creating the possible outcomes for each inverter
    global outcomes
    outcomes = md.np.zeros((len(inverters), 7, len(inverters[0].timestamp)))
    
    #deciding if the batteries are installed in the inverters or in the apartments
    global mode
    mode = batteryplace
    
    #getting the days in which the simulation is being run
    global indexes; global daylist
    indexes, daylist = sa.splitDays(inverters[0].timestamp)
    
    
    #setting the time-shifting intervals
    settingItemIntervals(inverters, applianceID)
    
    #Creating the arrays to split the energy that is directed towards each apartment into used energy, fed to the grid and to the battery
    for i in inverters:
        i.switchtime = []
        i.receivedgen = md.np.zeros_like(i.generation)
        for j in i.apartments:
            j.energyreceived = md.np.zeros(len(j.timestamp))
            j.gridfeedin = md.np.zeros(len(j.timestamp))
            j.batcharge = md.np.zeros(len(j.timestamp))
            j.batdischarge = md.np.zeros(len(j.timestamp))
            j.griduse_new = j.griduse[:]
            j.energyreceivedtotal = 0
            j.selfC_new = 0
            j.selfCinst_new = md.np.zeros(len(j.timestamp))
            j.selfS_new = 0
            j.selfSinst_new = md.np.zeros(len(j.timestamp))
            
            
            j.consumption_new = j.consumption[:]
            
    #The batteries are updated and receive the arrays on losses and charge rate
    for item in batlist:
        if mode == "ap":
            for i in item:
                i.chargeArray = md.np.zeros(len(i.chargeArray))
                i.chargeStatus = md.np.ones(len(i.chargeStatus))*i.depthDisch
                i.chargeRate = md.np.zeros(len(i.chargeStatus))
                i.batlosses = md.np.zeros(len(i.chargeStatus))
        else:
            item.chargeArray = md.np.zeros(len(item.chargeArray))
            item.chargeStatus = md.np.ones(len(item.chargeStatus))*item.depthDisch
            item.chargeRate = md.np.zeros(len(item.chargeStatus))
            item.batlosses = md.np.zeros(len(item.chargeStatus))
            
      
    #Calculating the number of switches that happen in the full switching phase
    global numberswitches
    numberswitches = md.np.zeros((len(inverters), len(inverters[0].timestamp)))
    #Running the switching based on functions
    for i in range(len(inverters)):
        global selected
        selected = 0
        for j in range(len(inverters[i].timestamp)):
            checkPV(i, j, inverters, batlist)
            
            
    #Recalculating the self-consumption and self-sufficiency of each apartment
    #Change mode to All for calculation of instantaneous self-consumption
    recalculateSelfCselfS(inverters, batlist, how="All")
    
    return outcomes, numberswitches



#%%
##### SWITCHING FUNCTIONS #####
#Each function represents a stage in the switching scheme

#Top functon in the hierarchy - checks if there is PV generation at all times

def checkPV(i, j, inverters, batlist):
    if inverters[i].generation[j] >= 0.0005:
        #if there is generation, we chack if the load is higher than it
        checkLoadPV(i, j, inverters, batlist)
    else:
        #if there is no generation, we check if the battery can be discharged
        checkBatDischarge_noPV(i, j, inverters, batlist)


#%% PV GENERATION

#Check if the load of the currently selected apartment is higher than the generation
def checkLoadPV(i, j, inverters, batlist):
    global selected
    if inverters[i].apartments[selected].consumption[j] > inverters[i].generation[j]:
        #if the load is higher than the generation, we go check if the battery can be discharged
        checkBatDischarge_PV(i, j, inverters, batlist)
    else:
        #the load is not higher than the generation, so we check if it can be increased
        checkLoadIncrease_PV(i, j, inverters, batlist)
        

#Check if the battery can be discharged when there is PV
def checkBatDischarge_PV(i, j, inverters, batlist):
    global mode; global selected
    if mode == "inv":
        if batlist[i].chargeStatus[j-1] > batlist[i].depthDisch:
            #the battery has enough charge, we will have outcome 0
            outcome(0, i, j, inverters, batlist)
        else:
            #the battery cannot be discharged and we depend on the grid
            outcome(1, i, j, inverters, batlist)
    elif mode == "ap":
        #batteries connected to each apartment
        if batlist[i][selected].chargeStatus[j-1] > batlist[i][selected].depthDisch:
            #the battery has enough charge, we will have outcome 0
            outcome(0, i, j, inverters, batlist)
        else:
            #the battery cannot be discharged and we depend on the grid
            outcome(1, i, j, inverters, batlist)



######### THIS IS THE CRUCIAL FUNCTION IN PHASE 3 ##############
#check if we can increase the current load with smart appliances
def checkLoadIncrease_PV(i, j, inverters, batlist):
    global daylist; global selected
    
    ap = inverters[i].apartments[selected]
    appliance = ap.appliances[ap.applianceindex]

    dayindex = daylist.index(ap.timestamp[j].date())
    
    #checking if there is an appliance able to be shifted (and if we already shifted)
    if False in ap.comp[dayindex] and ap.shifted[j] == 0:
        which = ap.comp[dayindex].index(False)
        length = ap.icons[dayindex][which][2]
                
        #checking if the time of generation that we have is enough for shifting and if it wont overlap with other use of the same appliance
        if (ap.rem[dayindex] > length and (all(v==0 for v in ap.shifted[j:j+length+1])) == True):
            #we CAN shift; SHOULD we?
            start = ap.icons[dayindex][which][0]
            end = ap.icons[dayindex][which][1]
            
            #the consumption at this time would be this if we shifted
            temp = ap.consumption[j] + appliance.consumption[start]
            #would it be the highest consumption at that time?
            if temp > max(inverters[i].consumption_perAp[j]):
                #we shift!
                #changing the apartment's consumption
                ap.consumption_new[j:j+length+1] = list(ap.consumption_new[j:j+length+1] + appliance.consumption[start:end+1])
                ap.consumption_new[start:end+1] = list(ap.consumption_new[start:end+1] - appliance.consumption[start:end+1])
                #changing the appliance's consumption
                consshifted = list(appliance.consumption[j:j+length+1])
                appliance.consumption_new[j:j+length+1] = appliance.consumption[start:end+1]
                appliance.consumption_new[start:end+1] = consshifted
                                
                #changing the auxiliary arrays
                ap.shifted[j:j+length+1] = md.np.ones(length+1)
                ap.rem[dayindex] = ap.rem[dayindex] - length
                ap.comp[dayindex][which] = True
                
                #rechecking if the load is higher than the PV
                checkLoadPV(i, j, inverters, batlist)
            else:
                #if not, we shift to the highest load at that time
                switchHighDemand_PV(i, j, inverters, batlist)
        else:
            #if we can't time-shift any appliance, we check for the highest load
            switchHighDemand_PV(i, j, inverters, batlist)
    else:
        #if we can't time-shift any appliance, we check for the highest load
        switchHighDemand_PV(i, j, inverters, batlist)
#################################################################################################################################################


#Switching to the highest demand at that time
def switchHighDemand_PV(i, j, inverters, batlist):
    global selected; global numberswitches
    if selected != inverters[i].consumption_perAp[j].index(max(inverters[i].consumption_perAp[j])):
        selectedprevious = selected
        numberswitches[i][j] = 1
        #If the demand is not the highest at the time, the switching occurs to the highest load, and the check if it is higher than the PV happens
        selected = inverters[i].consumption_perAp[j].index(max(inverters[i].consumption_perAp[j]))
        inverters[i].switchtime.append((j, inverters[i].timestamp[j], selectedprevious, selected, "high demand and PV"))  #append the time which the switch happened and the positions before-after
        checkLoadPV(i, j, inverters, batlist)
    else:
        #If the load is already the highest, but still lower than the generation, the battery will be charged
        checkBatCharge(i, j, inverters, batlist)


#Check the battery charge level when there is PV if it can still be charged:
def checkBatCharge(i, j, inverters, batlist):
    global mode; global selected
    if mode == "inv":
        if (batlist[i].capacity - batlist[i].chargeStatus[j-1]) > 0.011: #batlist[i].capacity:
            #If the battery is not at full capacity, Outcome 2 will happen
            outcome(2, i, j, inverters, batlist)
        else:
            #If the battery is already at full capacity, Outcome 3 follows
            outcome(3, i, j, inverters, batlist)
    elif mode == "ap":
        if (batlist[i][selected].capacity - batlist[i][selected].chargeStatus[j-1]) > 0.011:
            #If the battery is not at full capacity, Outcome 2 will happen
            outcome(2, i, j, inverters, batlist)
        else:
            #If the battery is already at full capacity, Outcome 3 follows
            outcome(3, i, j, inverters, batlist)
        

#%% NO PV GENERATION


#when there is no PV, check if there is battery charge
def checkBatDischarge_noPV(i, j, inverters, batlist):
    global mode
    if mode == "inv":
        if batlist[i].chargeStatus[j-1] > batlist[i].depthDisch:
            #if there is battery charge, checks if the load of the currently selected apartment is higher
            checkLoadBat(i, j,  inverters, batlist)
        else:
            #if there is no charge, setup the switch to the apartment that received the least energy
            switchLowestER_noBat(i, j, inverters, batlist)
    elif mode == "ap":
        #All apartments are the same now, with connected batteries in each one of them. So we just check the battery for each one
        checkAllBats(i, j, inverters, batlist)



#Check if the battery charge is enough to cover the load    
def checkLoadBat(i, j, inverters, batlist):
    global mode; global selected
    if mode == "inv":
        if (batlist[i].chargeStatus[j-1] - batlist[i].depthDisch) > inverters[i].apartments[selected].consumption_new[j]:
            #if the battery charge is enough to cover the load, check if the load is the highest
            switchHighDemand_noPV(i, j, inverters, batlist)
        else:
            #if the load is higher than the battery level, search for the apartment that received the least amount of energy
            switchLowestER(i, j, inverters, batlist)
    elif mode == "ap":
        if (batlist[i][selected].chargeStatus[j-1] - batlist[i][selected].depthDisch) > inverters[i].apartments[selected].consumption_new[j]:
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
        numberswitches[i][j] = 1
        #If the demand is not the highest at the time, the switching occurs to the highest load, and the battery supplies energy to this apartment
        selected = inverters[i].consumption_perAp[j].index(max(inverters[i].consumption_perAp[j])) 
        inverters[i].switchtime.append((j, inverters[i].timestamp[j], selectedprevious, selected, "high demand no PV"))  #append the time which the switch happened and the positions before-after
        checkBatRate(i, j, inverters, batlist)
    else:
        #If the demand is already the highest, we go directly to the battery supply
        checkBatRate(i, j, inverters, batlist)            
            

    

#Switch to the lowest energy received apartment
def switchLowestER(i, j, inverters, batlist):
    lowest = findLowestER(i, j, inverters)
    global selected; global numberswitches; global mode
    if mode == "inv":
        if inverters[i].apartments[lowest].consumption_new[j] > batlist[i].chargeStatus[j-1]:
            #if the lowest receiver can use all the charge in the battery
            inverters[i].switchtime.append((j, inverters[i].timestamp[j], selected, lowest, "lowest ER"))  #append the time which the switch happened and the positions before-after
            if lowest == selected:
                selected = lowest
            else:
                selected = lowest
                numberswitches[i][j] = 1
            checkBatRate(i, j, inverters, batlist)
        else:
            #the lowest receiver does not use the full energy stored in the battery, nothing happens
            checkBatRate(i, j, inverters, batlist)
    elif mode == "ap":
        if inverters[i].apartments[lowest].consumption_new[j] > batlist[i][selected].chargeStatus[j-1]:
            #if the lowest receiver can use all the charge in the battery
            inverters[i].switchtime.append((j, inverters[i].timestamp[j], selected, lowest, "lowest ER"))  #append the time which the switch happened and the positions before-after
            if lowest == selected:
                selected = lowest
            else:
                selected = lowest
                numberswitches[i][j] = 1
            checkBatRate(i, j, inverters, batlist)
        else:
            #the lowest receiver does not use the full energy stored in the battery, nothing happens
            checkBatRate(i, j, inverters, batlist)
        
        
#Switch to the apartment that received the lowest amount of energy
def switchLowestER_noBat(i, j,inverters, batlist):
    lowest = findLowestER(i, j, inverters)
    global selected; global numberswitches
    inverters[i].switchtime.append((j, inverters[i].timestamp[j], selected, lowest, "lowest ER no bat"))  #append the time which the switch happened and the positions before-after
    if lowest == selected:
        selected = lowest
    else:
        selected = lowest
        numberswitches[i][j] = 1
    outcome(6, i, j, inverters, batlist)     
        

#Finding the apartment with the lowest energy received
def findLowestER(i, j, inverters):
    ERaparts = list(md.np.zeros(len(inverters[i].apartments)))
    for k in range(len(inverters[i].apartments)):
        ERaparts[k] = inverters[i].apartments[k].energyreceivedtotal
           
    lowest = ERaparts.index(min(ERaparts))
    return lowest        
        
    
#Check if the battery rate is higher or lower than the demand
def checkBatRate(i, j, inverters, batlist, apartment="void"):
    global mode; global selected
    if mode == "inv":
        if batlist[i].cRate < inverters[i].apartments[selected].consumption_new[j]:
            #if the c-Rate is lower than the demand, we need the grid support
            outcome(4, i, j, inverters, batlist)
        else:
            #if c-Rate is higher than the demand - we can supply all the demand from the battery
            outcome(5, i, j, inverters, batlist)
    elif mode == "ap":
        if batlist[i][apartment].cRate < inverters[i].apartments[apartment].consumption_new[j]:
            #if the c-Rate is lower than the demand, we need the grid support
            outcome(4, i, j, inverters, batlist, apartment)
        else:
            #if c-Rate is higher than the demand - we can supply all the demand from the battery
            outcome(5, i, j, inverters, batlist, apartment)

            
#All apartments are the same, there is no PV and they all have batteries. Deciding the outcome of each one
def checkAllBats(i, j, inverters, batlist):
    
    #Run through all apartments and decide if they will get energy from the battery + grid(outcome 4),  only battery (outcome 5)
    #or only grid (outcome 6)
    for k in range(len(inverters[i].apartments)):
        if batlist[i][k].chargeStatus[j-1] > batlist[i][k].depthDisch:
            #There is enough battery charge, how is the c-Rate?
            checkBatRate(i, j, inverters, batlist, k)
        else:
            outcome(6, i, j, inverters, batlist, k)

#For outcomes 0-3, the selected gets the PV and the other ones energy only from the battery
def checkRemainingBats(i, j, inverters, batlist):
    global selected
    #For the remaining apartments (not the selected ones), how their battery behaves
    for k in range(len(inverters[i].apartments)):
        if k != selected:
            if batlist[i][k].chargeStatus[j-1] > batlist[i][k].depthDisch:
                checkBatRate(i, j, inverters, batlist, apartment = k)
            else:
                outcome(6, i, j, inverters, batlist, apartment = k)


















#%% OUTCOMES

def outcome(situation, i, j, inverters, batlist, apartment = "void"):
    
    #registering the ourcome
    global outcomes
    outcomes[i][situation][j] = 1
    global mode; global selected


    if mode == "inv":
        
        if situation == 0:
            """Load >PV, BatLVL > limit
            PV + Battery go to the load, no grid feed-in, possible griduse"""
            
            #considering the switching losses os 71 seconds every 15 minutes (7.889%), we check if there was a switch
            if outcomes[i][situation][j] == numberswitches[i][j] and numberswitches[i][j] == 1:
                inverters[i].receivedgen[j] = inverters[i].generation[j] - 0.07889*inverters[i].generation[j]
            else:
                inverters[i].receivedgen[j] = inverters[i].generation[j]
        
            #the battery supply energy to the selected apartment but it is limited between its c-Rate, charge status or the amount of energy required:
            batenergy = min(batlist[i].cRate, (batlist[i].chargeStatus[j-1] - batlist[i].depthDisch), 
                            abs(inverters[i].receivedgen[j] - inverters[i].apartments[selected].consumption_new[j]))
        
            #computing the battery losses
            batlist[i].batlosses[j] = batenergy - batenergy*batlist[i].efficiency
            batenergy = batenergy*batlist[i].efficiency
            
            #energy received by the apartment is the sum of the PV + batenergy
            inverters[i].apartments[selected].energyreceived[j] = inverters[i].receivedgen[j] + batenergy
            inverters[i].apartments[selected].energyreceivedtotal += inverters[i].apartments[selected].energyreceived[j]
            
            #battery is being discharged by batenergy
            inverters[i].apartments[selected].batdischarge[j] = -batenergy
            
            #energy taken from the grid to supplement the demand
            inverters[i].apartments[selected].griduse_new[j] = (inverters[i].apartments[selected].consumption_new[j] - \
                                                                inverters[i].apartments[selected].energyreceived[j])
          
            #battery is being affected as
            batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1] - batenergy*(1/batlist[i].efficiency)
            batlist[i].chargeArray[j] = -1 #discharge
            batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1] #should be -batenergy
        
        
        elif situation == 1:
            """Load > PV, BatLVL < limit
            PV to the load, no feed-in, no discharge, griduse"""
        
            #considering the switching losses os 71 seconds every 15 minutes (7.889%), we check if there was a switch
            if outcomes[i][situation][j] == numberswitches[i][j] and numberswitches[i][j] == 1:
            #meaning that there was a switching towards this outcome
                inverters[i].receivedgen[j] = inverters[i].generation[j] - 0.07889*inverters[i].generation[j]
                #the new energy from the solar panels is reduced in 6.7%
            else:
                inverters[i].receivedgen[j] = inverters[i].generation[j]
                #if there was no switching, the generated energy flows through as a whole
                
            #energy supplied by the battery is zero, so no batenergy is calculated
            
            #energy received by the apartment is only the PV system and the grid
            inverters[i].apartments[selected].energyreceived[j] = inverters[i].receivedgen[j]
            inverters[i].apartments[selected].energyreceivedtotal += inverters[i].apartments[selected].energyreceived[j]
    
            #griduse to supplement for the PV generation
            inverters[i].apartments[selected].griduse_new[j] = (inverters[i].apartments[selected].consumption_new[j] - \
                                                                inverters[i].apartments[selected].energyreceived[j])
        
            #battery is being affected as
            batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1]
            batlist[i].chargeArray[j] = 0   #no action
            batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
        
        
        
        elif situation == 2:
            """Load < PV; BatLVL < capacity
            PV goes to the load + battery, possible feed-in, no griduse"""
            
            #considering the switching losses os 71 seconds every 15 minutes (7.889%), we check if there was a switch
            if outcomes[i][situation][j] == numberswitches[i][j] and numberswitches[i][j] == 1:
            #meaning that there was a switching towards this outcome
                inverters[i].receivedgen[j] = inverters[i].generation[j] - 0.07889*inverters[i].generation[j]
                #the new energy from the solar panels is reduced in 6.7%
            else:
                inverters[i].receivedgen[j] = inverters[i].generation[j]
                #if there was no switching, the generated energy flows through as a whole

    
            #energy received by the apartment is exactly its demand
            inverters[i].apartments[selected].energyreceived[j] = inverters[i].apartments[selected].consumption_new[j]
            inverters[i].apartments[selected].energyreceivedtotal += inverters[i].apartments[selected].energyreceived[j]
    
            #griduse is zero as the whole demand is being met by the generation
            inverters[i].apartments[selected].griduse_new[j] = 0
            
            #the apartment is charging the battery now as the minimum between the c-Rate, the remaining capacity and the surplus energy
            inverters[i].apartments[selected].batcharge[j] =  min(batlist[i].cRate, (batlist[i].capacity - batlist[i].chargeStatus[j-1]), 
                     (inverters[i].receivedgen[j] - inverters[i].apartments[selected].energyreceived[j]))
            
            #computing the battery losses
            batlist[i].batlosses[j] = inverters[i].apartments[selected].batcharge[j] - inverters[i].apartments[selected].batcharge[j] * batlist[i].efficiency
            
            #the apartment sends energy to the grid as the generation - used energy - energy that goes to the battery
            inverters[i].apartments[selected].gridfeedin[j] = (inverters[i].receivedgen[j]- inverters[i].apartments[selected].energyreceived[j] - 
                                                                 inverters[i].apartments[selected].batcharge[j])
            
            #battery being affected as
            batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1] + (inverters[i].apartments[selected].batcharge[j] - batlist[i].batlosses[j])
            batlist[i].chargeArray[j] = 1 #charge
            batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
        
        
        
        elif situation == 3:
            """Load < PV; BatLVL = capacity
            PV goes to the load, the battery is fully charged; feed-in, no griduse"""
            
            #considering the switching losses os 71 seconds every 15 minutes (7.889%), we check if there was a switch
            if outcomes[i][situation][j] == numberswitches[i][j] and numberswitches[i][j] == 1:
            #meaning that there was a switching towards this outcome
                inverters[i].receivedgen[j] = inverters[i].generation[j] - 0.07889*inverters[i].generation[j]
                #the new energy from the solar panels is reduced in 6.7%
            else:
                inverters[i].receivedgen[j] = inverters[i].generation[j]
                #if there was no switching, the generated energy flows through as a whole
                
            
            #energy received by the apartment is exactly its demand
            inverters[i].apartments[selected].energyreceived[j] = inverters[i].apartments[selected].consumption_new[j]
            inverters[i].apartments[selected].energyreceivedtotal += inverters[i].apartments[selected].energyreceived[j]
    
            #griduse is zero as the whole demand is being met by the generation
            inverters[i].apartments[selected].griduse_new[j] = 0
            
            #the apartment does not charge the battery;
            #the apartment sends energy to the grid as the generation - used energy; no battery charging occurs
            inverters[i].apartments[selected].gridfeedin[j] = (inverters[i].receivedgen[j] - inverters[i].apartments[selected].energyreceived[j])
            
            #battery being affected as
            batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1]
            batlist[i].chargeArray[j] = 0 #no action
            batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]

    
        elif situation == 4:
            """ No PV; BatLVL> 0; c-Rate < demand
            Battery goes to the load; grid goes to the load"""
            
            #There are no generation losses in this case, as there is no generation
            inverters[i].receivedgen[j] = inverters[i].generation[j]
            
            #energy is supplied by the battery is the minimum between the remaining charge of the battery and its c-Rate
            batenergy = min(batlist[i].cRate, (batlist[i].chargeStatus[j-1] - batlist[i].depthDisch))       #this is the energy being sent
            
            #computing the battery losses
            batlist[i].batlosses[j] = batenergy - batenergy * batlist[i].efficiency
            batenergy = batenergy * batlist[i].efficiency                                                   #this is the energy being received, with losses
            
            #energy received by the apartment comes from the battery
            inverters[i].apartments[selected].energyreceived[j] = batenergy
            inverters[i].apartments[selected].energyreceivedtotal += inverters[i].apartments[selected].energyreceived[j]
    
            #the relation with the battery is also the energy supplied by it, but as a discharge (negative)
            inverters[i].apartments[selected].batdischarge[j] = -batenergy
            #the griduse to supplement the battery is given as
            inverters[i].apartments[selected].griduse_new[j] = inverters[i].apartments[selected].consumption_new[j] - inverters[i].apartments[selected].energyreceived[j]
            #there is no grid feedin
            
            #battery being affected as
            batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1] - batenergy/batlist[i].efficiency
            batlist[i].chargeArray[j] = -1 #discharge
            batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
           
            
        elif situation == 5:
            """No PV; BatLVL > 0; c-Rate > demand
            Battery has a c-Rate high enough to supply the demand, but we don't know about the charge. maybe grid support is needed"""
            
            #There are no generation losses in this case
            inverters[i].receivedgen[j] = inverters[i].generation[j]
            
            #energy is supplied by the battery is the minimum between the remaining charge and the demand (we already know the c-Rate is higher than the demand)
            batenergy = min((batlist[i].chargeStatus[j-1] - batlist[i].depthDisch), inverters[i].apartments[selected].consumption_new[j])       #this is the energy being sent
            
            #computing the battery losses
            batlist[i].batlosses[j] = batenergy - batenergy * batlist[i].efficiency
            batenergy = batenergy * batlist[i].efficiency                                                   #this is the energy being received, with losses
            
            #energy received comes from the battery
            inverters[i].apartments[selected].energyreceived[j] = batenergy
            inverters[i].apartments[selected].energyreceivedtotal += inverters[i].apartments[selected].energyreceived[j]
    
            #the relation with the battery is the energy supplied by it, as a discharge
            inverters[i].apartments[selected].batdischarge[j] = -batenergy
            #Nowe we don't know if there is need for the grid yet, as the demand can be higher than the battery charge.
            #If energy received is smaller than consumption, it was because the remaining charge was smaller than the demand.
            inverters[i].apartments[selected].griduse_new[j] = max(0, 
                     (inverters[i].apartments[selected].consumption_new[j] - inverters[i].apartments[selected].energyreceived[j]))
            #there is no grid feedin
            
            #battery being affected as
            batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1] - batenergy/batlist[i].efficiency
            batlist[i].chargeArray[j] = -1 #discharge
            batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
            
        elif situation == 6:
            """No PV; No battery charge; 
            Grid directly supplying the apartment that received the lowest amount of energy"""
            
            #There are no generation losses in this case
            inverters[i].receivedgen[j] = inverters[i].generation[j]
            
            #There is no energy being supplied by or to the battery
            
            #There is no energy eing received
            #There is just griduse in this case
            inverters[i].apartments[selected].griduse_new[j] = inverters[i].apartments[selected].consumption_new[j]
            
            #battery being affected as
            batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1]
            batlist[i].chargeArray[j] = 0 #no action
            batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
            
        else:
            print("No situation described")
            return 0








#%%
##### AUXILIARY FUNCTIONS #####

#Defining a function to add the batteries to the system; same as in phase 2      
def addBatteries(inverters, capacity, cRate, mode="None"):
    """Function to add the batteries to the system, as it is created without any by default on the main file"""
    
    batlist = []
    if mode == "ap":
        for i in inverters:
            batbundle = []
            for ap in i.apartments:
                batbundle.append(md.Battery(ap, capacity, cRate))
            batlist.append(batbundle)
    else:
        for i in inverters:
            batlist.append(md.Battery(i, capacity, cRate))  
            
    #bypassing the battery model into new null arrays that will be determined by the switching logic
    #TO DO - change the initalization of the batteries so this becomes obsolete
    for item in batlist:
        if mode == "ap":
            for i in item:
                i.chargeArray = md.np.zeros(len(i.chargeArray))
                i.chargeStatus = md.np.zeros(len(i.chargeStatus))
                i.chargeRate = md.np.zeros(len(i.chargeStatus))
        else:
            item.chargeArray = md.np.zeros(len(item.chargeArray))
            item.chargeStatus = md.np.zeros(len(item.chargeStatus))
            item.chargeRate = md.np.zeros(len(item.chargeStatus))
        
    return batlist
    
    
#Defining a function to recalculate self-consumption and self-sufficiency
def recalculateSelfCselfS(inverters, batlist, how="All"):
    """Calculating self-consumption and self-sufficiency for the new system configuration, keeping the previous values registered"""
    global mode
    if mode == "inv":
        for i in range(len(inverters)):
            for j in inverters[i].apartments:
                j.selfC_new = md.selfConsumption(j.consumption_new, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i])
                j.selfS_new = md.selfSufficiency(j.consumption_new, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i])
                if how == "All":
                    j.selfCinst_new = md.selfConsumptionInst(j.consumption_new, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i])
                    j.selfSinst_new = md.selfSufficiencyInst(j.consumption_new, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i])
    elif mode == "ap":
        for i in range(len(inverters)):
            apartment = 0
            for j in inverters[i].apartments:
                j.selfC_new = md.selfConsumption(j.consumption_new, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i][apartment])
                j.selfS_new = md.selfSufficiency(j.consumption_new, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i][apartment])
                if how == "All":
                    j.selfCinst_new = md.selfConsumptionInst(j.consumption_new, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i][apartment])
                    j.selfSinst_new = md.selfSufficiencyInst(j.consumption_new, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i][apartment])
                apartment += 1
    
    

#Defining setup functions for the phase 3

#For consumption of each appliance in an apartment
def getConsumptionIntervals(applicons, indexes, dayindex, daylist):
    """Function to get the intervals on appliance's consumption for each apartment"""   
    rise = -1; fall = -1; risenew = -1; fallnew=-1;
    interval = []
    
    #we need to make up for the 1h loss on the daylight saving time
    dstday = md.datetime(2017, 3, 26)
    if dayindex > daylist.index(dstday.date()):   #the 26th of march
        dstcorr = 1
    else:
        dstcorr = 0
    #checking the times in which the appliance was turned on during that day
    for i in range(indexes[1]-indexes[0]):
        if applicons[i] >= 0.002 and applicons[i-1] < 0.002:              #there was a rise
            risenew = i + 96*dayindex - dstcorr*4
        if applicons[i] < 0.002 and applicons[i-1] >= 0.002:              #there was a fall 
            fallnew = i + 96*dayindex - dstcorr*4
        #for the cases in which appliance starts/ends the day being used
        if i == 0 and applicons[i]>0.002:
            risenew = i + 96*dayindex - dstcorr*4
        if i == 95 and applicons[i]>0.002:
            fallnew = i + 96*dayindex - dstcorr*4
        #appending the intervals    
        if (risenew != rise and fallnew != fall and fallnew > risenew):
            interval.append((risenew, fallnew, (fallnew-risenew)))
            rise = risenew
            fall = fallnew
            
    return interval


#For the generation of each inverter
def getGenerationIntervals(genday, indexes, dayindex, daylist):
    """Function to get the generation interval in a day for an inverter"""
    rise = -1; fall = -1; risenew = -1; fallnew=-1;
    interval = []
    #we need to make up for the 1h loss on the daylight saving time
    dstday = md.datetime(2017, 3, 26)
    if dayindex > daylist.index(dstday.date()):   #the 26th of march
        dstcorr = 1
    else:
        dstcorr = 0    
    #checking the times in which the appliance was turned on during that day
    for i in range(indexes[1]-indexes[0]):
        if genday[i] >= 0.0005 and genday[i-1] < 0.0005:              #there was a rise
            risenew = i + 96*dayindex - dstcorr*4
        if genday[i] < 0.0005 and genday[i-1] >= 0.0005:              #there was a fall 
            fallnew = i + 96*dayindex - dstcorr*4
        if (risenew != rise and fallnew != fall and fallnew > risenew):
            interval.append((risenew, fallnew, (fallnew-risenew)))
            rise = risenew
            fall = fallnew
            
    return interval    
    

#Unifying generation intervals to make up for small periods when the inverters are tripped/panels are shaded
def unifyGenIntervals(igen):
    """Function to unify generation intervals in a day to make up for small non-generation periods"""
    #unifying generation intervals
    for i in range(len(igen)):
        if len(igen[i]) == 1:
            igen[i] = igen[i][0]
        elif len(igen[i]) > 1:
            temp = (igen[i][0][0], igen[i][-1][-2], (igen[i][-1][-2] - igen[i][0][0]))
            igen[i] = temp
        else:
            #if there was no generation that day, we set an empty tuple
            igen[i] = ()
    return igen

#Comparing intervals of consumption and generation and returning which intervals can be shifted to periods with sun
def getShiftableIntervals(icons, igen):
    """Function to detect which intervals can be shifted and which cannot"""
    comp = []; rem = []
    for i in range(len(icons)):
        within = []
        if len(igen[i]) > 0:
            strt = igen[i][0]; end = igen[i][1]
            remaining = end-strt                                                #how much generation we still have available to shift
            for j in icons[i]:
                if strt <= j[0] < end:# and strt < j[1] <= end:                #should we also consider the end of the cycle?
                    remaining = remaining - j[2]
                    within.append(True)
                else:
                    within.append(False)                    
        else:
            #if there was no generation that day we append an empty list
            within.append([])
        
        comp.append(within)
        rem.append(remaining)

    return comp, rem
    

#main function for setting the intervals and setting up the time-shift per apartment
def settingItemIntervals(inverters, applianceID):
    """Function to set the intervals for each apartment and inverter in the pilot and their comparison"""
    indexlist, daylist = sa.splitDays(inverters[0].timestamp)
    #setting up the interval lists
    for inv in inverters:  
        inv.igen = getIntervals(inv, indexlist, daylist)
        
        for ap in inv.apartments:  
            #check if the apartment has the appliance we are analysing
            for appli in range(len(ap.appliances)):
                if applianceID in ap.appliances[appli].ID:
                    appliance = ap.appliances[appli]
                    ap.applianceindex = appli
                    appliance.consumption_new = appliance.consumption
                    
            ap.icons = getIntervals(ap, indexlist, daylist, appliance)
            ap.comp, ap.rem = getShiftableIntervals(ap.icons, inv.igen)
            ap.shifted = setShiftedArrays(ap)
            

def setShiftedArrays(ap):
    """Function to identify which consumption intervals are already inside the pv generation interval"""
    shifted = md.np.zeros_like(ap.consumption)
    for i in range(len(ap.comp)):
        for j in range(len(ap.comp[i])):
            if ap.comp[i][j] == True:
                start = ap.icons[i][j][0]; end = ap.icons[i][j][1]
                shifted[start:end+1] = md.np.ones(ap.icons[i][j][2]+1)
    return shifted




def getIntervals(item, indexlist, daylist, appliance="none"):
    """Function to set the interval list for each object; apartments get consumption, inverters get generation"""
    currentday = md.datetime(2000, 1, 1)
    icons =[]; igen = []
    for j in range(len(item.timestamp)):
        tsday = item.timestamp[j].date()
        #setting up the analysis for each individual day
        if tsday != currentday:
            currentday = tsday
            dayindex = daylist.index(currentday)
            indexes = indexlist[dayindex]
            
            if type(item) == md.Inverter:
                genday = item.generation[indexes[0]:indexes[1]]
                igen.append(getGenerationIntervals(genday, indexes, dayindex, daylist))
            elif type(item) == md.Apartment:
                #getting the relevant intervals
                applicons = appliance.consumption[indexes[0]:indexes[1]]
                icons.append(getConsumptionIntervals(applicons, indexes, dayindex, daylist))
     
    if type(item) == md.Inverter:
        igen = unifyGenIntervals(igen)
        return igen
    elif type(item) == md.Apartment:
        return icons
                
                











    