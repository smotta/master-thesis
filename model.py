# -*- coding: utf-8 -*-
"""
Created on Tue May  2 10:28:26 2017

@author: Sergio

This is the file that describes and provides structure for the entities in the Herman Project.
In here, the inverters, apartments, appliances, batteries and any other object worthy of a model in this 
project will be described and have its parameters set. 
This file is intended to be imported by the main file, while serving as a backbone for the whole model.

It will provide basic functions and class definitions, which will be used in the main file and by other files for analysis.
"""



#%% Importing libraries as needed. This will forward the import to the main file as well, without need to import it again.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, datetime, timedelta
#For the sunrise and sunset times
import sunrise
#For binarySearchII
from bisect import bisect_left
#to save and load the inverter file#
import pickle


#%% Inverter
#Class inverter to account for the solar panels generation and bundle apartments together
class Inverter:
    """Inverter class, connected to the solar PV system and the apartments of the Herman project"""
    
    #the inverter is initialized with its ID, list of connected apartments, generation, consumption and timestamps, 
    #as well as self-consumption and self-sufficiency information.
    
    def __init__(self, filename, apartments, channels):
        self.ID = filename[-4:]
        self.apartments = self.setApartments(filename, apartments, channels)
        self.generation, self.consumption, self.timestamp = self.inverterBundle()
        self.selfCinst = selfConsumptionInst(self.consumption, self.generation, self.timestamp)
        self.selfC = selfConsumption(self.consumption, self.generation, self.timestamp)
        self.selfSinst = selfSufficiencyInst(self.consumption, self.generation, self.timestamp)
        self.selfS = selfSufficiency(self.consumption, self.generation, self.timestamp)
                                          
    #### FUNCTIONS ####   
    
    #setting the Apartment objects connected to each individual inverter: This function creates a list of Apartment objects and associates them with
    #each inverter in the system.
    def setApartments(self, filename, apartments, channels):
        connected_apartments = []
        for i in range(len(apartments)):
            filepath = filename+channels[i]+apartments[i] + '.csv'
            connected_apartments.append(Apartment(filepath, apartments[i], channels[i], filename[-4:]))
        return connected_apartments
           
    #adding together all the consumption/generation associated to this inverter. This is useful to get a broader view of each Herman device.
    def inverterBundle(self):
        generation = self.apartments[0].generation
        consumption = self.apartments[0].consumption
        timestamp = self.invAllTimestamps()
        for i in range(len(self.apartments)-1):
            consumption, generation = self.invSetTimestampData(timestamp)
        return generation, consumption, timestamp

    #Auxiliary functions  
    #A function to obtain all of the system's timestamps that occur in at least one apartment - used in inverterBundle()           
    def invAllTimestamps(self):
        lista = []
        for j in range(len(self.apartments)):
            lista = sorted(lista + self.apartments[j].timestamp)
            #With this command, we append all timestamps in the system
        alltimestamps = sorted(list(set(lista)))
        return alltimestamps
                
        
    #A function to get consumption and generation data for all apartments according to the timestamps        
    def invSetTimestampData(self, alltimestamps):
        #creating list of lists for each timestamp
        totalcons = []; totalgen = []
        
        #running through all timestamps:
        for i in range(len(alltimestamps)):
            timestamp = alltimestamps[i]
            cons = []; gen = []
            for k in range(len(self.apartments)):
                #searching all apartments for the timestamp in question      
                index = binarySearchII(self.apartments[k].timestamp, timestamp)
                if index > -1:                                                  #If the item was found in the list
                    cons.append(self.apartments[k].consumption[index])
                    gen.append(self.apartments[k].generation[index])
            #appending the lists for the timestamps in the list of lists            
            totalcons.append(sum(cons))
            totalgen.append(sum(gen))
        
        return totalcons, totalgen

#%% Apartment
#Class apartment for creating apartment entities to be controlled and modeled better
class Apartment:
    """Apartment class, connected to inverters and containing appliances""" 
     
    #the apartments will be initialized with its data, ID, channel in which it is connected, inverter associated, timestamp, consumption and generation, 
    #appliance list, self-consumption and self-sufficiency
    def __init__(self, filename, apartID, channel, inv):
        self.apartdata = pd.read_csv(filename)
        self.ID = apartID
        self.channel = channel
        self.inv = inv
        self.timestamp = self.setTimestamp(self.apartdata['time'])
        self.griduse = np.nan_to_num(self.apartdata['griduse'])
        self.consumption = np.nan_to_num(self.apartdata['griduse'])
        self.feedin = np.nan_to_num(self.apartdata['gridfeedin'])
        self.pv_se = np.nan_to_num(self.apartdata['pv_se'])
        self.pv_herman = np.nan_to_num(self.apartdata['pv_herman'])
        self.generation = self.setGeneration()
        self.consumption = self.setConsumptionFeedIn()                          #Considering the grid feed-in in the generation
        self.numbappliances = len(self.apartdata.columns)-5                     #time, gridfeedin, griduse, pv_se and pv_herman are disconsidered, the rest are appliances
        self.appliances = self.setAppliances()
        self.appliancecons, self.applianceconspercent = self.appConsumption()
        self.selfCinst = selfConsumptionInst(self.consumption, self.generation, self.timestamp)
        self.selfC = selfConsumption(self.consumption, self.generation, self.timestamp)
        self.selfSinst = selfSufficiencyInst(self.consumption, self.generation, self.timestamp)
        self.selfS = selfSufficiency(self.consumption, self.generation, self.timestamp)

     #### FUNCTIONS ####   
        
    #setting its timestamp as datetime object instead of pandas.Series of strings
    def setTimestamp(self, timestampseries):
        self.timestamp = []
        for i in range(len(timestampseries)):
            self.timestamp.append(datetime.strptime(timestampseries[i][0:19], "%Y-%m-%d %H:%M:%S"))
        return self.timestamp
    
    #setting the generation associated with each apartment as the highest value between the pv_se and pv_herman imported data
    def setGeneration(self):
        self.generation = np.zeros(len(self.pv_se))
        for i in range(len(self.pv_se)):
            self.generation[i] = max(self.pv_se[i], self.pv_herman[i])
        return self.generation

    #setting the consumption considering the grid feed-in
    def setConsumptionFeedIn(self):
        for i in range(len(self.feedin)):
            if (self.feedin[i] > 0 and self.generation[i] - self.feedin[i] > 0):
                self.consumption[i] = self.consumption[i] + (self.generation[i] - self.feedin[i])
        return self.consumption
    
    
    #setting the appliances in each apartment
    def setAppliances(self):
        self.appliances = []
        for i in range(1, self.numbappliances+1):
            self.appliances.append(Appliance(self.apartdata, i, self.ID))
        return self.appliances
        
    #defining the apartment's consumption for all the monitored appliances (different from the total consumption as there are other unmonitored appliances)
    def appConsumption(self):
        applend = len(self.apartdata.columns) - 2
        self.appliancearray = np.array(self.apartdata[self.apartdata.columns[3:applend]])
        self.appliancecons = np.ones(len(self.appliancearray))
        self.applianceconspercent = np.ones(len(self.appliancearray))
        for i in range(len(self.appliancearray)):
            self.appliancecons[i] = sum(self.appliancearray[i])
            if self.consumption[i] < 0.0005:
                self.applianceconspercent[i] = 0
            else:
                self.applianceconspercent[i] = self.appliancecons[i]/self.consumption[i]
        return self.appliancecons, self.applianceconspercent



#%% Appliance
#Class appliance for making it easier to control and monitor each appliance individually
class Appliance(object):
    """Appliance class, connected to Apartment and main consumer"""
    
    #The appliances are initialized with their consumption data and ID
    def __init__(self, apartdata, i, apID):
        self.consumption = np.nan_to_num(apartdata[apartdata.columns[2+i]])
        self.ID = apartdata.columns[2+i] + apID
        self.apt = apID     
          
                 
#%% Battery
#Class battery for the energy storage studies - first iteration of it at least
class Battery(object):
    """Battery class, connected to an apartment or an inverter"""
    
    #The batteries are initialized with their ID, capacity, charging rate, depth of discharge and efficiency, and have calculated
    #their charge status and amount of energy stored per timestamp
    def __init__(self, connectedto, capacity):
        self.ID = "battery" + connectedto.ID
        self.capacity = capacity
        self.cRate = 1.25                                                       #for the Tesla Powerwall 2
        self.depthDisch = 1 - 0.0*self.capacity
        self.efficiency = 0.90
        self.chargeArray = self.chargeArray(connectedto)
        self.chargeStatus = self.chargeStatus(connectedto)
        
    #### FUNCTIONS ####
    
    #Defining a function to specify the charging status of the battery - if it is charging or discharging
    def chargeArray(self, connectedto):
        self.chargeArray = np.zeros(len(connectedto.timestamp))
        for i in range(len(connectedto.generation)):
            if connectedto.generation[i] > connectedto.consumption[i]:          #If there is surplus, the battery should be charging
                self.chargeArray[i] = 1
            else:                                                               #No surplus, discharge the battery
                self.chargeArray[i] = 0
        return self.chargeArray

    #Defining a function to specify the charge status of the battery - how much energy is stored in it at a given timestamp
    def chargeStatus(self, connectedto):        
        self.chargeStatus = np.zeros(len(self.chargeArray))    
        for i in range(1, len(self.chargeArray)):
            if ((self.chargeArray[i] > 0) and (self.chargeStatus[i-1] < self.capacity)):          #charging state and not full
                self.chargeStatus[i] = self.chargeStatus[i-1] + min(self.cRate, abs(connectedto.generation[i] - connectedto.consumption[i]))
            elif (self.chargeArray[i] > 0):                                     #charging state but full
                self.chargeStatus[i] = self.chargeStatus[i-1]                
            else:                                                               #discharging state
                self.chargeStatus[i] = self.chargeStatus[i-1] - min(self.cRate, self.chargeStatus[i-1], 
                                 abs(connectedto.consumption[i] - connectedto.generation[i]))
        return self.chargeStatus


       
#%% Functions
#### CORE FUNCTIONS #### 
#These functions perform core taks and calculations, such as self-consumption and statistical analysis

#calculating self-consumption as an integral
def selfConsumption(demand, generation, timestamp):
    
    sunperiod = setSunperiod(timestamp)
    #sunperiod = np.ones(len(timestamp))
    minimum = np.zeros(len(demand))
    for i in range(len(minimum)):
        if sunperiod[i] == 1:
            minimum[i] = min(demand[i], generation[i])
    selfconsumption = np.trapz(minimum)/np.trapz(generation)
    return selfconsumption

#calculating self-consumption as an instantaneous value per timestamp
def selfConsumptionInst(demand, generation, timestamp):
    
    sunperiod = setSunperiod(timestamp)
    #sunperiod = np.ones(len(timestamp))  
    minimum = np.zeros(len(demand))
    selfConsumptionInst = np.zeros(len(demand))
    for i in range(len(minimum)):
        if sunperiod[i] == 1:
            minimum[i] = min(demand[i], generation[i])
            if generation[i] == 0:
                selfConsumptionInst[i] = 0
            else:
                selfConsumptionInst[i] = minimum[i]/generation[i]
    return selfConsumptionInst
    
#calculating self-sufficiency as an integral
def selfSufficiency(demand, generation, timestamp):
    
    sunperiod = setSunperiod(timestamp)  
    #sunperiod = np.ones(len(timestamp))
    minimum = np.zeros(len(demand))
    for i in range(len(minimum)):
        if sunperiod[i] == 1:
            minimum[i] = min(demand[i], generation[i])
    selfsufficiency = np.trapz(minimum)/np.trapz(demand)
    return selfsufficiency

#calculating self-sufficiency as an instantaneous value per timestamp
def selfSufficiencyInst(demand, generation, timestamp):
    sunperiod = setSunperiod(timestamp)
    #sunperiod = np.ones(len(timestamp))
    minimum = np.zeros(len(demand))
    selfSufficiencyInst = np.zeros(len(demand))
    for i in range(len(minimum)):
        if sunperiod[i] == 1:
            minimum[i] = min(demand[i], generation[i])
            if demand[i] == 0:
                selfSufficiencyInst[i] = 1
            else:
                selfSufficiencyInst[i] = minimum[i]/demand[i]
    return selfSufficiencyInst


#%% Functions
#### AUXILIARY FUNCTIONS ####
#These functions are but auxiliary ones, to help the code run more efficiently. 

#----- Obsolete funcions -----
#a function to compare timestamps and add consumptions - used mostly for inverterBundle
#def compareTimestamp(ts1, ts2, arr1, arr2):    
#    if len(ts1) < len(ts2):
#        timestamp1 = ts1                                                       #timestamp1 is always the smaller
#        array1 = arr1
#        timestamp2 = ts2                                                       #timestamp2 is always the bigger
#        array2 = arr2
#    else:
#        timestamp1 = ts2
#        array1 = arr2
#        timestamp2 = ts1
#        array2 = arr1        
#    addition = np.zeros(len(timestamp1))                                       #the addition will always have the smaller length
#    for i in range(len(timestamp1)):
#        addition[i] = array1[i] + array2[binarySearch(timestamp2, timestamp1[i], 30)]
#    return addition, timestamp1

#Implementing binary search, as found in http://interactivepython.org/XikcZ/courselib/static/pythonds/SortSearch/TheBinarySearch.html
#this function is used mostly for compareTimestamp
#def binarySearch(alist, item, criteria_seconds):
#    first = 0
#    last = len(alist)-1
#    found = False    
#    while first <= last and not found:
#        midpoint = (first + last)//2
#        difference = alist[midpoint] - item
#        if abs(difference.total_seconds()) < criteria_seconds:
#            found = True
#        else:
#            if item < alist[midpoint]:
#                last = midpoint - 1
#            else:
#                first = midpoint + 1
#    return midpoint
#----- Obsolete funcions -----

#Implementing binary search, as found in http://stackoverflow.com/questions/212358/binary-search-bisection-in-python
#This is used to return -1 if not found
def binarySearchII(a, x, lo=0, hi=None):  # can't use a to specify default for hi
    hi = hi if hi is not None else len(a)  # hi defaults to len(a)   
    pos = bisect_left(a, x, lo, hi)  # find insertion position
    return (pos if pos != hi and a[pos] == x else -1)  # don't walk off the end

#Creating a function to get total comnsumption of each object. It can also be used for generation, of course. 
#This function is used to get the total system consumption and generation, mainly in the Analysis function defined previously.
def totalSystemValues(lista):
    cons = 0
    gen = 0
    for i in range(len(lista)):
        cons += sum(lista[i].consumption)
        gen += sum(lista[i].generation)
    return cons/4, gen/4                                                        #Here a division by 4 as the data is given in kWh values in 15 minutes intervals. This means that to average it out, a division has to be performed.

#Creating a function to set the sunrise and sunset to filter generation noise
#It uses the code from sunrise.py to do so, therefore the file is necessary.
def setSunperiod(timestamp):
    #Starting the daylight saving time:
    dst1 = datetime(2017, 3, 26)
    dst2 = datetime(2017, 10, 29)
    
    sunrisetime = []
    sunsettime = []
    sunperiod = np.zeros(len(timestamp))
    
    s = sunrise.sun()
    for i in range(len(timestamp)):
        if timestamp[i] > dst1 and timestamp[i] < dst2:
            delta = timedelta(hours = 2)
        else:
            delta = timedelta(hours = 1)
        
        sunrisetime.append(datetime.combine(date.today(), s.sunrise(timestamp[i])) + delta)
        sunsettime.append(datetime.combine(date.today(), s.sunset(timestamp[i])) + delta)

        if timestamp[i].time() > sunrisetime[i].time() and timestamp[i].time() < sunsettime[i].time():
            sunperiod[i] = 1
    return sunperiod


#Creating a function to save and load the inverter file
def saveLoad(inverters, opt):
    if opt == "save":
        with open('inverter.pickle', 'wb') as f:
            pickle.dump(inverters, f)
    elif opt == "load":
        with open('inverter.pickle', 'rb') as f:
            return pickle.load(f)
    else:
        print("No valid option")



