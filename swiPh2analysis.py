# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 11:17:40 2017

@author: Sergio

This file will contain the functions to perform the analysis of the system after a switching logic has been implemented.
A separate file contains the analysis for the full systems as they are, without any 'smartness' in it - this script will check just
how smart the system actually becomes after the switching operations.
"""

import model as md
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import switchPh2 as sw

#%% Setting matplotlib's legends as TeX


#%% Analysis function for entities in the system - Switching version

def switchAnalysis(item, batlist, inverters, outcomes):
    
    #Analysis for inverters
    if type(item) == md.Inverter:
        buffer = np.column_stack((i.energyreceived for i in item.apartments))
        maxreceived = np.zeros(len(buffer))
        for j in range(len(buffer)):
            maxreceived[j] = max(buffer[j])
  
        #Find the battery associated to this inverter
        for i in range(len(batlist)):
            if batlist[i].connectedto.ID == item.ID:
                batindex = i
       
        #Plot of the full inverter's analysis
        plt.figure()
        ax = plt.subplot(111)
        plotAllOutcomes(inverters, outcomes, batindex)
        handllist = []
        plt.title("Analysis of inverter " + item.ID + " with Switching Phase II")
        #To change the legends to TeX, use True below - for fitting the full document#
        plt.rc('text', usetex=False)
        plt1, = plt.plot(item.timestamp, item.generation, 'k--', linewidth=0.6, label="Generation in "+item.ID)
        handllist = [plt1]
        colour = ["blue", "red", "green", "cyan", "magenta", "yellow", "black", "orange"]
        for i in item.apartments:
            itemplt1, = plt.plot(item.timestamp, i.consumption, color=colour[item.apartments.index(i)], linewidth=0.6, label="Consumption ap."+i.ID)
            itemplt, = plt.plot(item.timestamp, i.energyreceived, color=colour[item.apartments.index(i)], linewidth = 1.6, linestyle = ':', label="Energy Received ap. "+i.ID)
            handllist.append(itemplt1)
            handllist.append(itemplt)
        itemplt2, = plt.plot(item.timestamp, maxreceived, 'y*', linewidth = 0.9, label="Max Energy Received")
        handllist.append(itemplt2)
        plt3, = plt.plot(item.timestamp, batlist[batindex].chargeStatus, label="Battery charge status")
        plt4, = plt.plot(item.timestamp, batlist[batindex].chargeRate, label="Battery charge rate")
        handllist.append(plt3); handllist.append(plt4);
        
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width*0.9, box.height])
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=1, fancybox=True, prop={'size':8})
        plt.ylabel('Energy (kWh)')
        plt.xlabel('Time (timestamp)')
        plt.grid()
        
      
        #For all apartments connected to the inverter + battery x generation
        fig = plt.figure()
#        ax = fig.add_subplot((len(item.apartments)+2), 1, 1)
#        ax.plot(item.timestamp, item.generation)
        for i in range(len(item.apartments)):
            ax1 = fig.add_subplot(len(item.apartments)+1, 1, i+1)
            plt5, = ax1.plot(item.timestamp, item.apartments[i].consumption, label="Total Consumption")
            plt1, = ax1.plot(item.timestamp, item.apartments[i].energyreceived, label="Energy Used")
            plt2, = ax1.plot(item.timestamp, item.apartments[i].batcharge, label="Energy to Battery")
            plt3, = ax1.plot(item.timestamp, item.apartments[i].gridfeedin, label="Energy to Grid")
            plt4, = ax1.plot(item.timestamp, (item.apartments[i].energyreceived + item.apartments[i].batcharge + item.apartments[i].gridfeedin),'k--', linewidth=0.5, label="Total Energy Sent to Ap." + item.apartments[i].ID)
            box = ax1.get_position()
            ax1.set_position([box.x0, box.y0, box.width*0.9, box.height])
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=1, fancybox=True, prop={'size':8})
            plt.grid()
            plt.ylabel('Energy (kWh)')
            plt.xlabel('Time (timestamp)')
        
    
        ax = fig.add_subplot((len(item.apartments)+1), 1, len(item.apartments)+1)
        plt1, = ax.plot(item.timestamp, item.generation, label="Generation associated to the inverter")
        plt2, = ax.plot(item.timestamp, batlist[batindex].chargeStatus, label="Battery charge status")
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width*0.9, box.height])
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=1, fancybox=True, prop={'size':8})
        plt.grid()
        plt.ylabel('Energy (kWh)')
        plt.xlabel('Time (timestamp)')

        
    #Analysis for apartments
    if type(item) == md.Apartment:
        
        plt.figure()
        
        #If we want to see what is happening at each time:
        for i in range(len(inverters)):
            if item.inv == inverters[i].ID:
                index = i
        plotAllOutcomes(inverters, outcomes, index)
        
        #Plotting the parameters for the apartment
        plt.title("Apartment "+item.ID+ " full analysis - Previous x Switching Phase II")
        plt1, = plt.plot(item.timestamp, item.consumption, label="Consumption")
        plt2, = plt.plot(item.timestamp, item.generation, label="Generation (prev.)")
        plt3, = plt.plot(item.timestamp, item.energyreceived, label="Energy Received (sII)")
        plt4, = plt.plot(item.timestamp, item.feedin, 'g', linewidth=0.9, label="Grid feed-in (prev.)")
        plt5, = plt.plot(item.timestamp, item.gridfeedin, 'g--', label="Grid feed-in (sII)")
        plt6, = plt.plot(item.timestamp, item.griduse, 'c', linewidth=0.9, label="Grid usage (prev.)")
        plt7, = plt.plot(item.timestamp, item.griduse_new, 'c--', label="Grid usage (sII)")
        plt10, = plt.plot(item.timestamp, item.batcharge, linestyle='--', label="Battery charging (sII)")
        plt8, = plt.plot(item.timestamp, item.selfCinst, 'k', linewidth=0.9, label="Self-consumption (prev.)")
        plt9, = plt.plot(item.timestamp, item.selfCinst_new, 'k--', label="Self-consumption (sII)")
        plt11, = plt.plot(item.timestamp, inverters[index].generation, linestyle=':', linewidth=0.6, label="Generation inverter " + inverters[index].ID)
        plt.grid()
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=1, fancybox=True, prop={'size':8})
        plt.ylabel('Instantaneous Energy (kWh)')
        plt.xlabel('Time (timestamp)')
        
        print("-----\nApartment "+item.ID+" self-consumption\n")
        print("Prev. | SII \n")
        print( "%.2f" %(item.selfC) + " | " + "%.2f" %(item.selfC_new))
        print("-----\nApartment "+item.ID+" self-sufficiency\n")
        print("Prev. | SII \n")
        print( "%.2f" %(item.selfS) + " | " + "%.2f" %(item.selfS_new))
        
        
 

#%% Analysis function for self-consumption and self-sufficiency before and after the switching

def beforeAfterSwitching(inverters, mode = "None"):

    #initializing inicial values for self-consumption and self-sufficiency
    beforeC = []; beforeS= []
    #initializing new values for self-consumption and self-sufficiency
    afterC = []; afterS = []
    inverterlist = []; apartmentlist = []
    
    for i in inverters:
        for j in i.apartments:
            inverterlist.append(j.inv)
            apartmentlist.append(j.ID)
            beforeC.append(j.selfC*100)
            beforeS.append(j.selfS*100)
            afterC.append(j.selfC_new*100)
            afterS.append(j.selfS_new*100)            
        
    #Performing calculations in increase
    increaseC = (np.array(afterC)/np.array(beforeC) - np.ones(len(afterC))) * 100
    increaseS = (np.array(afterS)/np.array(beforeS) - np.ones(len(afterC))) * 100
    
    visualization = np.column_stack((inverterlist, apartmentlist, beforeC, afterC, increaseC, beforeS, 
                                     afterS, increaseS))
    headers = ["Inverter", "Apartment", "Self-consumption (prev)", "Self-consumption (sII)", "Increase(%)", 
               "Self-sufficiency (prev)", "Self-sufficiency (sII)", "Increase(%)"]    
    frame = pd.DataFrame(visualization, columns=headers, dtype = np.float64)   
      
    averageC = np.mean(afterC)
    averageS = np.mean(afterS)
    
    
    if mode == "Show":
        plt.figure()
        plt.title("Increase of self-consumption and self-sufficiency after Switching Phase II")
        plt1, = plt.plot(range(len(apartmentlist)), beforeC, 'b-', label="self-consumption (prev.)")
        plt2, = plt.plot(range(len(apartmentlist)), afterC, 'b:', label="self-consumption (sII)")
        plt3, = plt.plot(range(len(apartmentlist)), beforeS, 'r-', label="self-sufficiency (prev.)")
        plt4, = plt.plot(range(len(apartmentlist)), afterS, 'r:', label="self-sufficiency (sII)")
        plt5, = plt.plot(range(len(apartmentlist)), increaseC, 'k--', label="Increase in self-consumption")
        plt6, = plt.plot(range(len(apartmentlist)), increaseS, 'c--', label="Increase in self-sufficiency")
        plt.legend()
        plt.xticks(range(len(apartmentlist)), apartmentlist)
        plt.ylabel('(%)')
        plt.xlabel('Apartment')
        print("Average self-consumption after switching is %.2f\nAverage self-sufficiency after switching is %.2f" %(averageC, averageS))
    return frame, visualization, apartmentlist
        
        



#%% Analysis function for different battery parameters

def batAnalysis(inverters, symarray, cRarray, mode):
    
    savefile = 'C:/Users/Sergio/Dropbox (Personal)/InnoEnergy/Master Thesis/BeforeAfterAnalysis.xls'
    writer = pd.ExcelWriter(savefile)
    
    #Results of the before x after analysis on SC and SS
    baresults = []
    scAVG = []; ssAVG = []
    sclist = []; sslist = []
    
    for i in range(len(symarray)):
        batlist = []
        outcomes = []
        #Adding the batteries in the system
        batlist = sw.addBatteries(inverters, symarray[i], cRarray[i])
        outcomes = sw.switchingPhase2(inverters, batlist)
        
        #Performing the before x after analysis
        frame, visualization, aptlist = beforeAfterSwitching(inverters)
        
        #Saving all results in a list of results
        baresults.append(frame)
        sclist.append(frame['Self-consumption (sII)'])
        sslist.append(frame['Self-sufficiency (sII)'])
        
        scAVG.append(np.mean(np.array(frame['Self-consumption (sII)'])))
        ssAVG.append(np.mean(np.array(frame['Self-sufficiency (sII)'])))
        #Writing it to an excel file
        frame.to_excel(writer, sheet_name='Simulation %s'%i)
    
    #Writing it on Excel file
    writer.save()
    

    if mode == "capacity":
        title = "battery capacity"
        printBatAnalysis(title, symarray, scAVG, ssAVG, sclist, sslist, aptlist)
    elif mode == "cRate":
        title = "charge rate"
        printBatAnalysis(title, cRarray, scAVG, ssAVG, sclist, sslist, aptlist)

    
    return baresults
    
def printBatAnalysis(title, array, scAVG, ssAVG, sclist, sslist, aptlist):
    

    #showing results for average self-consumption and self-sufficiency
    plt.figure()
    plt.title("Average self-consumption and self-sufficiency per " + title)
    plt.plot(array, scAVG, label="self-consumption")
    plt.plot(array, ssAVG, label="self-sufficiency")
    plt.legend()
    plt.ylabel('(%)')
    plt.xlabel('Battery capacity (kWh)')
    #Getting a boxplot for self-consumption and self-sufficiency

    scarray = np.transpose(np.array(sclist))
    ssarray = np.transpose(np.array(sslist))

    plt.figure()
    plt.title("Self-consumption per " + title)
    plt.boxplot(np.array(sclist))
    plt.xticks(range(1, len(scarray)+1), aptlist)
    plt.ylabel('Self-consumption (%)')
    plt.xlabel('Apartment')

    plt.figure()
    plt.title("Self-sufficiency per " + title)
    plt.boxplot(np.array(sslist))
    plt.xticks(range(1, len(ssarray)+1), aptlist)
    plt.ylabel('Self-sufficiency (%)')
    plt.xlabel('Apartment')

    






#%% AUXILIARY FUNCTIONS


#Cumulative energy received in each apartment per timestamp
def cumulativeER(inverters):
    for inv in inverters:
        for ap in inv.apartments:
            ap.cumulativeER = md.np.zeros(len(ap.timestamp))
            for i in range(len(ap.timestamp)):
                ap.cumulativeER[i] = md.np.trapz(ap.energyreceived[:i])
        


#Switching losses
def switchingLosses(numberswitchings, inverters, switchinglosses):
    #Getting the number of inverters in the system and the number of data points we have
    numbinv = len(inverters); numbtimes = len(inverters[0].timestamp)
    
    nbswitching_percent = numberswitchings/(numbinv * numbtimes)                     #Percentage of time in which a switching occurs

    #Calculating the energy losses in regards of the generation    
    totalgen = 0
    for i in inverters:
        totalgen = totalgen + sum(i.generation)
    
    #Switching losses depend on the inverter and switching device
    energylosses = numberswitchings*switchinglosses
    
    #Losses in percent
    energylosses_percent = energylosses/totalgen
    
    #Print this information?
    return nbswitching_percent, energylosses, energylosses_percent


   


#%% Auxiliar function to get intervals

def getIntervals(vector, timestamp):
    rise = -1; fall=-1
    risenew= 0; fallnew = 0
    interval = []
    for i in range(len(vector)):
        if i == 0 and vector[i] == 1:
            #for the start
            risenew = i 
        if i == len(vector)-1 and vector[i] == 1:
            #for the end
            fallnew = i  
        if vector[i] == 1 and vector[i] != vector[i-1]:
            #there is a swich UP
            risenew = i
        if vector[i] == 0 and vector[i] != vector[i-1]:
            #there is a switch down
            fallnew = i
        if (risenew != rise and fallnew != fall and fallnew > risenew):
            interval.append((risenew, fallnew, timestamp[risenew], timestamp[fallnew]))
            rise = risenew
            fall = fallnew
    return interval
        
        
        
        
#%% Function to plot the shade over the intervals

def plotShades(inverters, intervals, colour, j, inv):
    outcomes = ['PV+B to L', 'PV+G to L', 'PV to L+B', 'PV to L+G', 'B+G to L', 'B to L', 'G to L']
    for i in range(len(intervals)):
        md.plt.axvspan(inverters[inv].timestamp[intervals[i][0]], inverters[inv].timestamp[intervals[i][1]], alpha=0.3, color=colour, label =  "_"*i + outcomes[j])
    
        
#%% Plotting all the outcomes to analyse

def plotAllOutcomes(inverters, outcomes, inv):
    #There are 7 outcomes - using the color scheme found in http://colorbrewer2.org/#type=sequential&scheme=Blues&n=7
    #colors = ['#eff3ff', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#084594']  
    #colors = ['#8c510a', '#d8b365', '#f6e8c3', '#f5f5f5', '#c7eae5', '#5ab4ac', '#01665e']
    #colors = ['#d73027', '#fc8d59', '#fee08b', '#ffffbf', '#d9ef8b', '#91cf60', '#1a9850']     
    
    colors = ['#156300', '#35f400','#91cf60', '#1a9850',  '#fc8d59', '#999600', '#707070']
  
    intervals = []        
    
    for i in range(len(outcomes[inv])):
        intervals.append(getIntervals(outcomes[inv][i], inverters[inv].timestamp))
        plotShades(inverters, intervals[i], colors[i], i, inv)    
        
        
        
        
        
        
        
        
        
        
        












