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

#%% Analysis function for entities in the system - Switching version

def switchAnalysis(item, batlist):
    
    if type(item) == md.Inverter:
        buffer = np.column_stack((i.energyreceived for i in item.apartments))
        maxreceived = np.zeros(len(buffer))
        for j in range(len(buffer)):
            maxreceived[j] = max(buffer[j])
  
        #Find the battery associated to this inverter
        for i in range(len(batlist)):
            if batlist[i].connectedto.ID == item.ID:
                batindex = i
    
    
    
        #Following the maximum + battery behavior
        plt.figure()
        plt.title("Consumption x Maximum Energy Received per Apartment")
        plt1, = plt.plot(item.timestamp, item.generation, 'k', label="Generation associated to Inverter "+item.ID)
        handllist = [plt1]
        for i in item.apartments:
            itemplt1, = plt.plot(item.timestamp, i.consumption, linewidth=0.6, label="Consumption of apt "+i.ID)
            itemplt, = plt.plot(item.timestamp, i.energyreceived, label="Energy Received of apt "+i.ID)
            handllist.append(itemplt1)
            handllist.append(itemplt)
        itemplt2, = plt.plot(item.timestamp, maxreceived, 'k--', linewidth = 0.9, label="Maximum Energy Received on all apartments")
        handllist.append(itemplt2)
        plt3, = plt.plot(item.timestamp, batlist[batindex].chargeStatus, label="Battery charge status")
        plt4, = plt.plot(item.timestamp, batlist[batindex].chargeRate, label="Charge rate of the battery")
        plt5, = plt.plot(item.timestamp, batlist[batindex].chargeStatus - np.ones(len(batlist[batindex].chargeStatus))*batlist[batindex].depthDisch, 'r--', label="Remaining Charge of the battery")
        handllist.append(plt3); handllist.append(plt4);  handllist.append(plt5)
        plt.legend(handles = handllist)
        plt.grid()
        
#        #Following each apartment
#        plt.figure()
#        plt.title("Consumption x Energy Received per Apartment")
#        plt1, = plt.plot(item.timestamp, item.generation, 'k', label="Generation associated to Inverter "+item.ID)
#        handllist = [plt1]
#        for i in item.apartments:
#            itemplt, = plt.plot(item.timestamp, i.consumption, label="Consumption of apt "+i.ID)
#            handllist.append(itemplt)
#            itemplt2, = plt.plot(item.timestamp, i.energyreceived, 'k--', linewidth = 1.0, label="Energy sent to apt "+i.ID)
#            handllist.append(itemplt2)
#        plt.legend(handles = handllist)
#        
#        
#        #For all apartments connected to the inverter + battery x generation
#        fig = plt.figure()
##        ax = fig.add_subplot((len(item.apartments)+2), 1, 1)
##        ax.plot(item.timestamp, item.generation)
#        for i in range(len(item.apartments)):
#            ax1 = fig.add_subplot(len(item.apartments)+1, 1, i+1)
#            plt1, = ax1.plot(item.timestamp, item.apartments[i].energyreceived, label="Energy Used")
#            plt2, = ax1.plot(item.timestamp, item.apartments[i].batcharge, label="Energy to Battery")
#            plt3, = ax1.plot(item.timestamp, item.apartments[i].gridfeedin, label="Energy to Grid")
#            plt4, = ax1.plot(item.timestamp, (item.apartments[i].energyreceived + item.apartments[i].batcharge + item.apartments[i].gridfeedin),'k--', linewidth=0.5, label="Total Energy Sent to Apartment")
#            plt5, = ax1.plot(item.timestamp, item.apartments[i].consumption, label="Total Consumption")
#            plt.legend(handles = [plt1, plt2, plt3, plt4])
#    
#        ax = fig.add_subplot((len(item.apartments)+1), 1, len(item.apartments)+1)
#        plt1, = ax.plot(item.timestamp, item.generation, label="Generation associated to the inverter")
#        plt2, = ax.plot(item.timestamp, batlist[batindex].chargeStatus, label="Battery charge status")
#        plt.legend(handles = [plt1, plt2])
#
#
#        #Battery behavior
#        plt.figure()
#        plt1, = plt.plot(item.timestamp, item.generation, label="Generation in the inverter")
#        plt2, = plt.plot(item.timestamp, item.consumption, label="Total consumption in the inverter")
#        plt3, = plt.plot(item.timestamp, batlist[batindex].chargeStatus, label="Battery charge status")
#        plt4, = plt.plot(item.timestamp, batlist[batindex].chargeRate, label="Charge rate of the battery")
#        for i in range(len(item.apartments)):
#            plt5, = plt.plot(item.timestamp, item.apartments[i].consumption, label="Energy consumption")
#            plt6, = plt.plot(item.timestamp, item.apartments[i].energyreceived, 'k--', label="Energy Used")
#        plt.grid()
#        plt.legend(handles = [plt1, plt2, plt3, plt4])    
        
    #elif type(item) == md.Apartment:
        
   
        
        
#%% Analysis function for Energy Received

#This function will analyse the effects of reactive switching in the self-consumption and self-sufficiency of an apartment
def AnalysisSw1(item):
    """Function to analyse the effects of the first switching logic implemented - Reactive switching"""
    
    plt.figure()
    plt1, = plt.plot(item.timestamp, item.energyreceived, label="Energy Received after Switching")
    plt2, = plt.plot(item.timestamp, item.consumption, label="Consumption")
    plt3, = plt.plot(item.timestamp, item.generation, label="Generation (previous)")
    plt4, = plt.plot(item.timestamp, item.selfCinst, label="Self-consumption")
    plt.legend(handles=[plt1, plt2, plt3, plt4])
    
