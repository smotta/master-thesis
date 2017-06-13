# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 11:48:53 2017

@author: Sergio
Phase 2 - Smart Switching based on consumption data
This file will run the logic behind the switching - phase 2 for each inverter.
"""

import model as md

#Switching function phase 2
def switching1(inverters, batlist):
    """Function to implement the switching logic for Phase 2 - Smart Switching based on consumption data"""


    #Creating the arrays to split the energy that is directed towards each apartment into used energy, fed to the grid and to the battery
    #print("Creating the energy received vectors...")
    for i in inverters:
        for j in i.apartments:
            j.energyreceived = md.np.zeros(len(j.timestamp))
            j.gridfeedin = md.np.zeros(len(j.timestamp))
            j.batcharge = md.np.zeros(len(j.timestamp))
     
    for i in batlist:
        i.chargeArray = md.np.zeros(len(i.chargeArray))
        i.chargeStatus = md.np.zeros(len(i.chargeStatus))
        i.chargeRate = md.np.zeros(len(i.chargeStatus))
         
    ##### Switching Logic #####
    print("Implementing Switching Logic 1...")
    for i in range(len(inverters)):
        selected = 0                                                            #Initializing the first apartment
        for j in range(len(inverters[i].timestamp)):
            #If there is generation associated with the inverter at this time
            if inverters[i].generation[j] > 0:
                #is the load of the selected apartment highter than the generation at this time?
                if (inverters[i].apartments[selected].consumption[j] > inverters[i].generation[j]):
                    #is the battery charged?
                    if batlist[i].chargeStatus[j-1] > batlist[i].depthDisch:
                        #yes - PV + B to the load
                        batenergy = min(batlist[i].cRate, batlist[i].chargeStatus[j-1] - batlist[i].depthDisch, inverters[i].apartments[selected].consumption[j] - inverters[i].generation[j])
                        inverters[i].apartments[selected].energyreceived[j] = min((inverters[i].generation[j] + batenergy), inverters[i].apartments[selected].consumption[j])
                        batlist[i].chargeStatus[j] = max(batlist[i].chargeStatus[j-1] - batenergy, 0)
                        batlist[i].chargeArray[j] = -1
                        batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
                        inverters[i].apartments[selected].batcharge[j] = batlist[i].chargeRate[j]
                    else:
                        #no - just PV to the load
                        inverters[i].apartments[selected].energyreceived[j] = inverters[i].generation[j]
                        batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1]
                        batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
                        inverters[i].apartments[selected].batcharge[j] = batlist[i].chargeRate[j]
                else:
                    #the load is smaller than the PV generation. Is the load the highest in the inverter?
                    if selected != inverters[i].consumption_perAp[j].index(max(inverters[i].consumption_perAp[j])):
                        #since the load is not the highest load in the inverter, we change to the highest
                        selected = inverters[i].consumption_perAp[j].index(max(inverters[i].consumption_perAp[j]))
                        if (inverters[i].apartments[selected].consumption[j] > inverters[i].generation[j]):
                            #is the highest load in the system higher than the PV production? Then we check the battery and see if it is charged,
                            if batlist[i].chargeStatus[j-1] > batlist[i].depthDisch:
                                #yes - PV + B to the load
                                batenergy = min(batlist[i].cRate, batlist[i].chargeStatus[j-1] - batlist[i].depthDisch, inverters[i].apartments[selected].consumption[j] - inverters[i].generation[j])
                                inverters[i].apartments[selected].energyreceived[j] = min((inverters[i].generation[j] + batenergy), inverters[i].apartments[selected].consumption[j])
                                batlist[i].chargeStatus[j] = max(batlist[i].chargeStatus[j-1] - batenergy, 0)
                                batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
                                batlist[i].chargeArray[j] = -1
                                inverters[i].apartments[selected].batcharge[j] = batlist[i].chargeRate[j]
                            else:
                                #no - just PV to the load
                                inverters[i].apartments[selected].energyreceived[j] = inverters[i].generation[j]
                                batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1]
                                batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
                                inverters[i].apartments[selected].batcharge[j] = batlist[i].chargeRate[j]
                        else:
                            #the highest load is smaller than the PV production. Can we charge the battery?
                            if batlist[i].chargeStatus[j-1] < batlist[i].capacity and j > 1:
                                #If the battery can still be charged, we then have
                                inverters[i].apartments[selected].energyreceived[j] = inverters[i].apartments[selected].consumption[j]
                                batlist[i].chargeArray[j] = 1.0
                                batlist[i].chargeStatus[j] = min(batlist[i].chargeStatus[j-1] + min(batlist[i].cRate, abs(inverters[i].generation[j] - inverters[i].apartments[selected].consumption[j])), batlist[i].capacity)
                                inverters[i].apartments[selected].gridfeedin[j] = max(abs(inverters[i].generation[j] - inverters[i].apartments[selected].consumption[j]) - (batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]), 0)
                                batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
                                inverters[i].apartments[selected].batcharge[j] = batlist[i].chargeRate[j]
                            else:
                                #The battery is fully charged
                                inverters[i].apartments[selected].energyreceived[j] = inverters[i].apartments[selected].consumption[j]
                                #feed-in??
                                inverters[i].apartments[selected].gridfeedin[j] = inverters[i].generation[j] - inverters[i].apartments[selected].energyreceived[j]
                                batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1]
                                batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
                                inverters[i].apartments[selected].batcharge[j] = batlist[i].chargeRate[j]
                    else:
                        #The load is the highest load already! So we jump and check the battery
                        if batlist[i].chargeStatus[j-1] < batlist[i].capacity and j > 1:
                            #If the battery can still be charged, we then have
                            inverters[i].apartments[selected].energyreceived[j] = inverters[i].apartments[selected].consumption[j]
                            batlist[i].chargeArray[j] = 1.0
                            batlist[i].chargeStatus[j] = min(batlist[i].chargeStatus[j-1] + min(batlist[i].cRate, abs(inverters[i].generation[j] - inverters[i].apartments[selected].consumption[j])), batlist[i].capacity)
                            inverters[i].apartments[selected].gridfeedin[j] = max(abs(inverters[i].generation[j] - inverters[i].apartments[selected].consumption[j]) - (batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]), 0)
                            batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
                            inverters[i].apartments[selected].batcharge[j] = batlist[i].chargeRate[j]

                        else:
                            #The battery is fully charged
                            inverters[i].apartments[selected].energyreceived[j] = inverters[i].apartments[selected].consumption[j]
                            #feed-in??
                            inverters[i].apartments[selected].gridfeedin[j] = inverters[i].generation[j] - inverters[i].apartments[selected].energyreceived[j]
                            batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1]
                            batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
                            inverters[i].apartments[selected].batcharge[j] = batlist[i].chargeRate[j]
            else:
                #There is no generation of solar power at the moment! Do we have charge in the battery?
                if batlist[i].chargeStatus[j-1] > batlist[i].depthDisch:
                    #There is charge in the battery - is it higher than the demand?
                    if (batlist[i].chargeStatus[j-1]-batlist[i].depthDisch) > inverters[i].apartments[selected].consumption[j]:
                        #yes - but are we considering the highest demand at the time?
                        if selected != inverters[i].consumption_perAp[j].index(max(inverters[i].consumption_perAp[j])):
                            #The load is not the highest load in the inverter, we change to the highest
                            print("Switched at " + str(inverters[i].timestamp[j]))
                            selected = inverters[i].consumption_perAp[j].index(max(inverters[i].consumption_perAp[j]))
                            #HERE IT ENTERS THE MAXIMUM POWER BATTERY - WHAT IS THIS?? SKIPPED FOR NOW
                            #since the battery charge is higher than the maximum demand we have, the generation associated with it is the max between the discharge rate and the total charge 
                            batenergy = min(batlist[i].cRate, batlist[i].chargeStatus[j-1] - batlist[i].depthDisch, inverters[i].apartments[selected].consumption[j])
                            inverters[i].apartments[selected].energyreceived[j] = min(batenergy, inverters[i].apartments[selected].consumption[j])
                            batlist[i].chargeStatus[j] = max(batlist[i].chargeStatus[j-1] - batenergy, batlist[i].depthDisch)
                            batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
                            batlist[i].chargeArray[j] = -1
                            inverters[i].apartments[selected].batcharge[j] = batlist[i].chargeRate[j]
                        else:
                            #The load is already the highest associated to this inverter
                            batenergy = min(batlist[i].cRate, batlist[i].chargeStatus[j-1] - batlist[i].depthDisch, inverters[i].apartments[selected].consumption[j])
                            inverters[i].apartments[selected].energyreceived[j] = min(batenergy, inverters[i].apartments[selected].consumption[j])
                            batlist[i].chargeStatus[j] = max(batlist[i].chargeStatus[j-1] - batenergy, batlist[i].depthDisch)
                            batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
                            batlist[i].chargeArray[j] = -1
                            inverters[i].apartments[selected].batcharge[j] = batlist[i].chargeRate[j]

                    else:
                        #The battery charge is smaller than the demand, but we can use it anyway
                        #HERE IT ENTERS THE DISTRIBUTION QUOTA - STILL NEED TO IMPLEMENT THIS
                        batenergy = min(batlist[i].cRate, batlist[i].chargeStatus[j-1] - batlist[i].depthDisch, inverters[i].apartments[selected].consumption[j])
                        inverters[i].apartments[selected].energyreceived[j] = min(batenergy, inverters[i].apartments[selected].consumption[j])
                        batlist[i].chargeStatus[j] = max(batlist[i].chargeStatus[j-1] - batenergy, batlist[i].depthDisch)
                        batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
                        batlist[i].chargeArray[j] = -1
                        inverters[i].apartments[selected].batcharge[j] = batlist[i].chargeRate[j]

                else:
                    #No solar power and no battery - no generation associated to any apartment and the grid connection is used.
                    inverters[i].apartments[selected].energyreceived[j] = 0
                    batlist[i].chargeStatus[j] = batlist[i].chargeStatus[j-1]
                    batlist[i].chargeRate[j] = batlist[i].chargeStatus[j] - batlist[i].chargeStatus[j-1]
                    inverters[i].apartments[selected].batcharge[j] = batlist[i].chargeRate[j]
   
    #Recalculating self-consumption and self-sufficiency
    



    
def addBatteries(inverters, capacity):
    """Function to add the batteries to the system, as it is created without any by default on the main file"""
    
    batlist = []
    for i in inverters:
        batlist.append(md.Battery(i, capacity))
     
    #bypassing the battery model into new null arrays that will be determined by the switching logic
    #TO DO - change the initalization of the batteries so this becomes obsolete
    for i in batlist:
        i.chargeArray = md.np.zeros(len(i.chargeArray))
        i.chargeStatus = md.np.zeros(len(i.chargeStatus))
        i.chargeRate = md.np.zeros(len(i.chargeStatus))
        
    return batlist
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
