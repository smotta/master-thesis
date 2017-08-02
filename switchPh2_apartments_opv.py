# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 12:43:42 2017

@author: Sergio

This will be the script to store all the functions necessary for the switching - phase 2

THIS FILE ONLY CONSIDER THE LOSSES ON THE PV SYSTEM, NOT ON THE BATTERY
"""

import model as md
#%% 
##### SWITCHING FUNCTION IMPLEMENTED #####
def switchingPhase2(inverters, batlist, batteryplace):
    """Function to implement the switching phase 2 as described in 
    'Schakelschema Herman Fase 2 v0.2.1 (English).pdf"""
    
    
    #creating the possible outcomes
    global outcomes
    outcomes = md.np.zeros((len(inverters), 7, len(inverters[0].timestamp)))
    
    
    global mode
    mode = batteryplace   
    
    #Creating the arrays to split the energy that is directed towards each apartment into used energy, fed to the grid and to the battery
    #print("Creating the energy received vectors...")
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
    
    #The batteries are placed in each apartment
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

#%%%
##### SWITCHING FUNCTIONS #####
#Each function represents a stage in the switching scheme

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
    global mode; global selected
    if mode == "inv":
        if batlist[i].chargeStatus[j-1] > batlist[i].depthDisch:
            #If the battery can be drained, we have Outcome 1
            outcome(0, i, j, inverters, batlist)
        else:
            #If the battery is "empty", Outcome 2 yields
            outcome(1, i, j, inverters, batlist)
    elif mode == "ap":
        if batlist[i][selected].chargeStatus[j-1] > batlist[i][selected].depthDisch:
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
        if batlist[i].chargeStatus[j-1] < batlist[i].capacity:
            #If the battery is not at full capacity, Outcome 3 will happen
            outcome(2, i, j, inverters, batlist)
        else:
            #If the battery is already at full capacity, Outcome 4 follows
            outcome(3, i, j, inverters, batlist)
    elif mode == "ap":
        if batlist[i][selected].chargeStatus[j-1] < batlist[i][selected].capacity:
            #If the battery is not at full capacity, Outcome 3 will happen
            outcome(2, i, j, inverters, batlist)
        else:
            #If the battery is already at full capacity, Outcome 4 follows
            outcome(3, i, j, inverters, batlist)
        
  
    
    
    
####### No PV generation ##########    


#When there is no PV, check if there is battery charge
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
        if (batlist[i].chargeStatus[j-1] - batlist[i].depthDisch) > inverters[i].apartments[selected].consumption[j]:
            #if the battery charge is enough to cover the load, check if the load is the highest
            switchHighDemand_noPV(i, j, inverters, batlist)
        else:
            #if the load is higher than the battery level, search for the apartment that received the least amount of energy
            switchLowestER(i, j, inverters, batlist)
    elif mode == "ap":
        if (batlist[i][selected].chargeStatus[j-1] - batlist[i][selected].depthDisch) > inverters[i].apartments[selected].consumption[j]:
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
        if inverters[i].apartments[lowest].consumption[j] > batlist[i].chargeStatus[j-1]:
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
        if inverters[i].apartments[lowest].consumption[j] > batlist[i][selected].chargeStatus[j-1]:
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
        if batlist[i].cRate < inverters[i].apartments[selected].consumption[j]:
            #if the c-Rate is lower than the demand, we need the grid support
            outcome(4, i, j, inverters, batlist)
        else:
            #if c-Rate is higher than the demand - we can supply all the demand from the battery
            outcome(5, i, j, inverters, batlist)
    elif mode == "ap":
        if batlist[i][apartment].cRate < inverters[i].apartments[apartment].consumption[j]:
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




###############################################################################   
#Outcome function to define each situation's ourcome:
def outcome(situation, i, j, inverters, batlist, apartment = "void"):
    
    #Registering the outcome
    global outcomes
    outcomes[i][situation][j] = 1
    global mode; global selected
    
    if mode == "inv":
        if situation == 0:
            """Load > PV; BatLVL > limit
            PV + Battery go to the load, no feed-in, possible griduse"""
          
            
            #considering now the switching losses in the generation - each switch takes up to 1 minute, or 6.7% (1/15) of the energy at that timestamp
            #this is only valid for outcomes that take into account the solar power generation (0 to 3)
            if outcomes[i][situation][j] == numberswitches[i][j] and numberswitches[i][j] == 1:
            #meaning that there was a switching towards this outcome
                inverters[i].receivedgen[j] = inverters[i].generation[j] - 0.07889*inverters[i].generation[j]
                #the new energy from the solar panels is reduced in 6.7%
            else:
                inverters[i].receivedgen[j] = inverters[i].generation[j]
                #if there was no switching, the generated energy flows through as a whole
                
                
            #energy supplied by the battery is the lowest between the c-rate, remaining charge and difference between consumption and generation
            batenergy = min(batlist[i].cRate, (batlist[i].chargeStatus[j-1] - batlist[i].depthDisch), 
                            abs(inverters[i].receivedgen[j] - inverters[i].apartments[selected].consumption[j]))
          
            
            #energy received by the apartment is the sum of the PV + batenergy
            inverters[i].apartments[selected].energyreceived[j] = inverters[i].receivedgen[j] + batenergy
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
            
            #considering now the switching losses in the generation - each switch takes up to 1 minute, or 6.7% (1/15) of the energy at that timestamp
            #this is only valid for outcomes that take into account the solar power generation (0 to 3)
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
            inverters[i].apartments[selected].griduse_new[j] = (inverters[i].apartments[selected].consumption[j] - \
                                                                inverters[i].apartments[selected].energyreceived[j])
        
            #battery is being affected as
            batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1]
            batlist[i].chargeArray[j] = 0   #no action
            batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
    
        elif situation == 2:
            """Load < PV; BatLVL < capacity
            PV goes to the load + battery, possible feed-in, no griduse"""
            
            #considering now the switching losses in the generation - each switch takes up to 1 minute, or 6.7% (1/15) of the energy at that timestamp
            #this is only valid for outcomes that take into account the solar power generation (0 to 3)
            if outcomes[i][situation][j] == numberswitches[i][j] and numberswitches[i][j] == 1:
            #meaning that there was a switching towards this outcome
                inverters[i].receivedgen[j] = inverters[i].generation[j] - 0.07889*inverters[i].generation[j]
                #the new energy from the solar panels is reduced in 6.7%
            else:
                inverters[i].receivedgen[j] = inverters[i].generation[j]
                #if there was no switching, the generated energy flows through as a whole
                
            #energy is being supplied TO the battery now, at a rate as the minimum between the c-Rate, remaining capacity and the surplus energy
    
            #energy received by the apartment is exactly its demand
            inverters[i].apartments[selected].energyreceived[j] = inverters[i].apartments[selected].consumption[j]
            inverters[i].apartments[selected].energyreceivedtotal += inverters[i].apartments[selected].energyreceived[j]
    
            #griduse is zero as the whole demand is being met by the generation
            inverters[i].apartments[selected].griduse_new[j] = 0
            #the apartment is charging the battery now as the minimum between the c-Rate, the remaining capacity and the surplus energy
            inverters[i].apartments[selected].batcharge[j] =  min(batlist[i].cRate, (batlist[i].capacity - batlist[i].chargeStatus[j-1]), 
                     (inverters[i].receivedgen[j] - inverters[i].apartments[selected].energyreceived[j]))
            #the apartment sends energy to the grid as the generation - used energy - energy that goes to the battery
            inverters[i].apartments[selected].gridfeedin[j] = (inverters[i].receivedgen[j]- inverters[i].apartments[selected].energyreceived[j] - 
                                                                 inverters[i].apartments[selected].batcharge[j])
            #battery being affected as
            batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1] + inverters[i].apartments[selected].batcharge[j]
            batlist[i].chargeArray[j] = 1 #charge
            batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
            
        elif situation == 3:
            """Load < PV; BatLVL = capacity
            PV goes to the load, the battery is fully charged; feed-in, no griduse"""
            
            #considering now the switching losses in the generation - each switch takes up to 1 minute, or 6.7% (1/15) of the energy at that timestamp
            #this is only valid for outcomes that take into account the solar power generation (0 to 3)
            if outcomes[i][situation][j] == numberswitches[i][j] and numberswitches[i][j] == 1:
            #meaning that there was a switching towards this outcome
                inverters[i].receivedgen[j] = inverters[i].generation[j] - 0.07889*inverters[i].generation[j]
                #the new energy from the solar panels is reduced in 6.7%
            else:
                inverters[i].receivedgen[j] = inverters[i].generation[j]
                #if there was no switching, the generated energy flows through as a whole
                
            #no energy is supplied or extracted from the battery
            
            #energy received by the apartment is exactly its demand
            inverters[i].apartments[selected].energyreceived[j] = inverters[i].apartments[selected].consumption[j]
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
            
            #There are no generation losses in this case
            inverters[i].receivedgen[j] = inverters[i].generation[j]
            
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
            
            #There are no generation losses in this case
            inverters[i].receivedgen[j] = inverters[i].generation[j]
            
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
            
            #There are no generation losses in this case
            inverters[i].receivedgen[j] = inverters[i].generation[j]
            
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
    
    
    
    
    #PLACING THE BATTERIES IN EACH APARTMENT
    
    elif mode == "ap":
        if situation == 0:
            """Load > PV; BatLVL > limit
            PV + Battery go to the load, no feed-in, possible griduse"""
          
                                    
            #considering now the switching losses in the generation - each switch takes up to 1 minute, or 6.7% (1/15) of the energy at that timestamp
            #this is only valid for outcomes that take into account the solar power generation (0 to 3)
            if outcomes[i][situation][j] == numberswitches[i][j] and numberswitches[i][j] == 1:
            #meaning that there was a switching towards this outcome
                inverters[i].receivedgen[j] = inverters[i].generation[j] - 0.07889*inverters[i].generation[j]
                #the new energy from the solar panels is reduced in 6.7%
            else:
                inverters[i].receivedgen[j] = inverters[i].generation[j]
                #if there was no switching, the generated energy flows through as a whole
                
            #energy supplied by the battery is the lowest between the c-rate, remaining charge and difference between consumption and generation
            batenergy = min(batlist[i][selected].cRate, (batlist[i][selected].chargeStatus[j-1] - batlist[i][selected].depthDisch), 
                            abs(inverters[i].receivedgen[j] - inverters[i].apartments[selected].consumption[j]))
          
            #energy received by the apartment is the sum of the PV + batenergy
            inverters[i].apartments[selected].energyreceived[j] = inverters[i].receivedgen[j] + batenergy
            inverters[i].apartments[selected].energyreceivedtotal += inverters[i].apartments[selected].energyreceived[j]
            #battery is being discharged by batenergy
            inverters[i].apartments[selected].batdischarge[j] = -batenergy
            #energy taken from the grid to supplement the demand
            inverters[i].apartments[selected].griduse_new[j] = (inverters[i].apartments[selected].consumption[j] - \
                                                                inverters[i].apartments[selected].energyreceived[j])

      
            #battery is being affected as
            batlist[i][selected].chargeStatus[j] = batlist[i][selected].chargeStatus[j-1] - batenergy
            batlist[i][selected].chargeArray[j] = -1 #discharge
            batlist[i][selected].chargeRate[j] = batlist[i][selected].chargeStatus[j] - batlist[i][selected].chargeStatus[j-1] #should be -batenergy
        
            checkRemainingBats(i, j, inverters, batlist)

        elif situation == 1:
            """Load > PV; BatLVL < limit
            PV to the load, no feed-in and no battery discharge"""
            
                                                
            #considering now the switching losses in the generation - each switch takes up to 1 minute, or 6.7% (1/15) of the energy at that timestamp
            #this is only valid for outcomes that take into account the solar power generation (0 to 3)
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
            inverters[i].apartments[selected].griduse_new[j] = (inverters[i].apartments[selected].consumption[j] - \
                                                                inverters[i].apartments[selected].energyreceived[j])
        
            #battery is being affected as
            batlist[i][selected].chargeStatus[j] = batlist[i][selected].chargeStatus[j-1]
            batlist[i][selected].chargeArray[j] = 0   #no action
            batlist[i][selected].chargeRate[j] = batlist[i][selected].chargeStatus[j] - batlist[i][selected].chargeStatus[j-1]
    
            checkRemainingBats(i, j, inverters, batlist)

        elif situation == 2:
            """Load < PV; BatLVL < capacity
            PV goes to the load + battery, possible feed-in, no griduse"""
            
                                                            
            #considering now the switching losses in the generation - each switch takes up to 1 minute, or 6.7% (1/15) of the energy at that timestamp
            #this is only valid for outcomes that take into account the solar power generation (0 to 3)
            if outcomes[i][situation][j] == numberswitches[i][j] and numberswitches[i][j] == 1:
            #meaning that there was a switching towards this outcome
                inverters[i].receivedgen[j] = inverters[i].generation[j] - 0.07889*inverters[i].generation[j]
                #the new energy from the solar panels is reduced in 6.7%
            else:
                inverters[i].receivedgen[j] = inverters[i].generation[j]
                #if there was no switching, the generated energy flows through as a whole
                
            #energy is being supplied TO the battery now, at a rate as the minimum between the c-Rate, remaining capacity and the surplus energy
    
            #energy received by the apartment is exactly its demand
            inverters[i].apartments[selected].energyreceived[j] = inverters[i].apartments[selected].consumption[j]
            inverters[i].apartments[selected].energyreceivedtotal += inverters[i].apartments[selected].energyreceived[j]
    
            #griduse is zero as the whole demand is being met by the generation
            inverters[i].apartments[selected].griduse_new[j] = 0
            #the apartment is charging the battery now as the minimum between the c-Rate, the remaining capacity and the surplus energy
            inverters[i].apartments[selected].batcharge[j] =  min(batlist[i][selected].cRate, (batlist[i][selected].capacity - batlist[i][selected].chargeStatus[j-1]), 
                     (inverters[i].receivedgen[j] - inverters[i].apartments[selected].energyreceived[j]))
            #the apartment sends energy to the grid as the generation - used energy - energy that goes to the battery
            inverters[i].apartments[selected].gridfeedin[j] = (inverters[i].receivedgen[j] - inverters[i].apartments[selected].energyreceived[j] - 
                                                                 inverters[i].apartments[selected].batcharge[j])
            #battery being affected as
            batlist[i][selected].chargeStatus[j] = batlist[i][selected].chargeStatus[j-1] + inverters[i].apartments[selected].batcharge[j]
            batlist[i][selected].chargeArray[j] = 1 #charge
            batlist[i][selected].chargeRate[j] = batlist[i][selected].chargeStatus[j] - batlist[i][selected].chargeStatus[j-1]
            
            checkRemainingBats(i, j, inverters, batlist)

        elif situation == 3:
            """Load < PV; BatLVL = capacity
            PV goes to the load, the battery is fully charged; feed-in, no griduse"""
            
                                                                        
            #considering now the switching losses in the generation - each switch takes up to 1 minute, or 6.7% (1/15) of the energy at that timestamp
            #this is only valid for outcomes that take into account the solar power generation (0 to 3)
            if outcomes[i][situation][j] == numberswitches[i][j] and numberswitches[i][j] == 1:
            #meaning that there was a switching towards this outcome
                inverters[i].receivedgen[j] = inverters[i].generation[j] - 0.07889*inverters[i].generation[j]
                #the new energy from the solar panels is reduced in 6.7%
            else:
                inverters[i].receivedgen[j] = inverters[i].generation[j]
                #if there was no switching, the generated energy flows through as a whole
                
            #no energy is supplied or extracted from the battery
            
            #energy received by the apartment is exactly its demand
            inverters[i].apartments[selected].energyreceived[j] = inverters[i].apartments[selected].consumption[j]
            inverters[i].apartments[selected].energyreceivedtotal += inverters[i].apartments[selected].energyreceived[j]
    
            #griduse is zero as the whole demand is being met by the generation
            inverters[i].apartments[selected].griduse_new[j] = 0
            #the apartment does not charge the battery;
            #the apartment sends energy to the grid as the generation - used energy; no battery charging occurs
            inverters[i].apartments[selected].gridfeedin[j] = (inverters[i].receivedgen[j] - inverters[i].apartments[selected].energyreceived[j])
            
            #battery being affected as
            batlist[i][selected].chargeStatus[j] = batlist[i][selected].chargeStatus[j-1]
            batlist[i][selected].chargeArray[j] = 0 #no action
            batlist[i][selected].chargeRate[j] = batlist[i][selected].chargeStatus[j] - batlist[i][selected].chargeStatus[j-1]
            
            checkRemainingBats(i, j, inverters, batlist)

            
        #NO PV ANYMORE    
        #SELECTED is irrelevant for the following outcomes - they will happen for all apartments
        elif situation == 4:
            """ No PV; BatLVL> 0; c-Rate < demand
            Battery goes to the load; grid goes to the load"""
            
            if (inverters[i].receivedgen[j] ==0):
                inverters[i].receivedgen[j] = inverters[i].generation[j]
                
            #energy is supplied by the battery is the minimum between the remaining charge of the battery and its c-Rate
            batenergy = min(batlist[i][apartment].cRate, (batlist[i][apartment].chargeStatus[j-1] - batlist[i][apartment].depthDisch))
            
            #energy received by the apartment comes from the battery
            inverters[i].apartments[apartment].energyreceived[j] = batenergy
            inverters[i].apartments[apartment].energyreceivedtotal += inverters[i].apartments[apartment].energyreceived[j]
    
            #the relation with the battery is also the energy supplied by it, but as a discharge (negative)
            inverters[i].apartments[apartment].batdischarge[j] = -batenergy
            #the griduse to supplement the battery is given as
            inverters[i].apartments[apartment].griduse_new[j] = inverters[i].apartments[apartment].consumption[j] - inverters[i].apartments[apartment].energyreceived[j]
            #there is no grid feedin
            
            #battery being affected as
            batlist[i][apartment].chargeStatus[j] = batlist[i][apartment].chargeStatus[j-1] - batenergy
            batlist[i][apartment].chargeArray[j] = -1 #discharge
            batlist[i][apartment].chargeRate[j] = batlist[i][apartment].chargeStatus[j] - batlist[i][apartment].chargeStatus[j-1]
            
        elif situation == 5:
            """No PV; BatLVL > 0; c-Rate > demand
            Battery has a c-Rate high enough to supply the demand, but we don't know about the charge. maybe grid support is needed"""
            
            if (inverters[i].receivedgen[j] ==0):
                inverters[i].receivedgen[j] = inverters[i].generation[j]
            
            #energy is supplied by the battery is the minimum between the remaining charge and the demand (we already know the c-Rate is higher than the demand)
            batenergy = min((batlist[i][apartment].chargeStatus[j-1] - batlist[i][apartment].depthDisch), inverters[i].apartments[apartment].consumption[j])
            
            #energy received comes from the battery
            inverters[i].apartments[apartment].energyreceived[j] = batenergy
            inverters[i].apartments[apartment].energyreceivedtotal += inverters[i].apartments[apartment].energyreceived[j]
    
            #the relation with the battery is the energy supplied by it, as a discharge
            inverters[i].apartments[apartment].batdischarge[j] = -batenergy
            #Nowe we don't know if there is need for the grid yet, as the demand can be higher than the battery charge.
            #If energy received is smaller than consumption, it was because the remaining charge was smaller than the demand.
            inverters[i].apartments[apartment].griduse_new[j] = max(0, 
                     (inverters[i].apartments[apartment].consumption[j] - inverters[i].apartments[apartment].energyreceived[j]))
            #there is no grid feedin
            
            #battery being affected as
            batlist[i][apartment].chargeStatus[j] = batlist[i][apartment].chargeStatus[j-1] - batenergy
            batlist[i][apartment].chargeArray[j] = -1 #discharge
            batlist[i][apartment].chargeRate[j] = batlist[i][apartment].chargeStatus[j] - batlist[i][apartment].chargeStatus[j-1]
            
            
        elif situation == 6:
            """No PV; No battery charge; 
            Grid directly supplying the apartment that received the lowest amount of energy"""
            
            if (inverters[i].receivedgen[j] ==0):
                inverters[i].receivedgen[j] = inverters[i].generation[j]
                
            #There is no energy being supplied by or to the battery
            
            #There is no energy eing received
            #There is just griduse in this case
            inverters[i].apartments[apartment].griduse_new[j] = inverters[i].apartments[apartment].consumption[j]
            
            #battery being affected as
            batlist[i][apartment].chargeStatus[j] = batlist[i][apartment].chargeStatus[j-1]
            batlist[i][apartment].chargeArray[j] = 0 #no action
            batlist[i][apartment].chargeRate[j] = batlist[i][apartment].chargeStatus[j] - batlist[i][apartment].chargeStatus[j-1]
            
        else:
            print("No situation described")
            return 0
    
      
    
#%%  
#Defining a function to add the batteries to the system       
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
                j.selfC_new = md.selfConsumption(j.consumption, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i])
                j.selfS_new = md.selfSufficiency(j.consumption, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i])
                if how == "All":
                    j.selfCinst_new = md.selfConsumptionInst(j.consumption, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i])
                    j.selfSinst_new = md.selfSufficiencyInst(j.consumption, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i])
    elif mode == "ap":
        for i in range(len(inverters)):
            apartment = 0
            for j in inverters[i].apartments:
                j.selfC_new = md.selfConsumption(j.consumption, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i][apartment])
                j.selfS_new = md.selfSufficiency(j.consumption, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i][apartment])
                if how == "All":
                    j.selfCinst_new = md.selfConsumptionInst(j.consumption, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i][apartment])
                    j.selfSinst_new = md.selfSufficiencyInst(j.consumption, (j.energyreceived + j.batcharge + j.gridfeedin), j.timestamp, j, batlist[i][apartment])
                apartment += 1
    
    
    
