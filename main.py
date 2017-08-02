# -*- coding: utf-8 -*-
"""
Created on Tue May  2 10:24:31 2017

@author: Sergio

This is the main file to run the model for the Herman Smart Grid project.
This file executes and import different files for each "module" and function of said model.
The main goal here is to have the file easily change between different analysis and scenarios, 
using code from other files while maintaining readability.
"""

#%% Importing the required libraries
import model as md
import connection as cn
import sysanalysis as sa
import classification as cl
#import swiPh2analysis as swa
#import switchPh2 as sw           #switching second implementation (functions)
import switchPh2_apartments as sw
import swiPh2analysis_apartments as swa

import switchPh3 as sw3
#%%Describing the system's connections

#--CYCLE BETWEEN ONSDORP AND AQUARADIUS

#Using a module for setting up the connection scheme. This enables the easy interchange between the two pilot projects
connection, connection_chnl, aptlist, invlist = cn.aquaradius()
#connection, connection_chnl, aptlist, invlist = cn.onsdorp()





#--SET THE LOCATION OF THE DATA

#This is the folder containing all data for the apartments' generation and consumption
#file_path = 'C:/Users/Sergio/Dropbox (Personal)/InnoEnergy/Master Thesis/SEAC - ECN/Data from LENS/tki-data-20170418/locationdata/'

#new data
file_path = 'C:/Users/Sergio/Dropbox (Personal)/InnoEnergy/Master Thesis/SEAC - ECN/Data from LENS/tki-data-20170801/locationdata/'

#Other computer
#file_path = 'C:/Users/Sergio/Dropbox/InnoEnergy/Master Thesis/SEAC - ECN/Data from LENS/tki-data-20170724/locationdata/'

#TO-DO - Make this a prompt request with browsing window





#%%Creating the model and connections

#creating a list of Inverter objects to describe the system
inverters = []


#--UNCOMMENT THIS IF THIS IS THE FIRST TIME WE RUN/CREATE THE SYSTEM MODEL - ANY NEW CHANGES SHOULD BE RUN AGAIN

##initializing each inverter with its apartments (and each with its appliances) - creating the whole system's hierarchy
#for inverter in invlist:
#    inverters.append(md.Inverter(file_path+inverter, connection[inverter], connection_chnl[inverter]))
#
##to put all entities' consumptions at the same length and make up for the lost data
#md.equality(inverters) 
#md.saveLoad(inverters, 'inverter_08.pickle', "save")



#--THIS IF THE SYSTEM MODEL IS ALREADY BUILT AND ONLY ANALYSIS ARE BEING PERFORMED

inverters = md.saveLoad(inverters, 'inverter_08.pickle', "load")

#After setting up the inverters, correcting the generation data issues for the inverters - doesn't affect the apartments' generation:
md.invgeneration(inverters)





#%% Run a data diagnostic to see where we have missing data

#sa.dataDiagnostics(inverters)

#
#sa.findHeatPump(inverters)
#
#
#for inv in inverters:
#    for apt in inv.apartments:
#        for appli in apt.appliances:
#           if "rmtepomp" in appli.ID:
#               sa.Analysis(appli, inverters, invlist, aptlist, "all")


#%% Analysis of the whole system AS IS now

#sa.Demo(inverters, invlist, aptlist)

#Other analysis functions exist but are all integrated on the Demo. Check sysanalysis.py for more info on each analysis function.





#%% Switching Phase II implemented with the functions on switchPh2_apartments.py

#SETTING UP THE MODE - "inv" for batteries placed in each Herman, "ap" for batteries placed in each apartment
mode = "inv"

###### Adding the batteries in the system
batlist = sw.addBatteries(inverters, 2, 0.5, mode)

##implementing the switching logic 2
#outcomes, numberswitches = sw.switchingPhase2(inverters, batlist, mode)
#
##Saving the files
#md.saveLoad([inverters, batlist, outcomes, numberswitches], 'swi2_08i205_l.pickle', "save")
#
#sc2 = []
#for i in inverters:
#    for ap in i.apartments:
#        sc2.append(ap.selfC_new)
#        
#print(md.np.mean(sc2))

######## Loading the arrays for quicker processing
#batlist = []
#outcomes = []
#
#[inverters, batlist, outcomes, numberswitches] = md.saveLoad([inverters, batlist, outcomes], "swi2_07i205_l.pickle", "load")




#%% Testing the switching losses. This includes running twice the switching Phase II to get the results; once with the losses and once without.
#This needs to be run again when writing the thesis with the proper values of consumption and rechecking the full data.

# Running the losses analysis


#overall_nl, energyloss_nl, totalgen_nl, outcomelist_nl, bats_nl, switchesoutcomes_nl, numberswitches_nl, overall_opv, energyloss_opv, totalgen_opv, \
#outcomelist_opv, bats_opv, switchesoutcomes_opv, numberswitches_opv, overall_bat, energyloss_bat, totalgen_bat, outcomelist_bat, bats_bat, switchesoutcomes_bat, numberswitches_bat\
#= swa.influenceSwitchingLosses(inverters, [2, 0.5], mode)


#%% Analysis functions for the system after Switching Phase II

#
##Running the Analysis for all inverters
#for i in inverters:
#    swa.switchAnalysis(i, batlist, inverters, outcomes, mode)

#
##Analysis for a specific apartment (ap 35)
#swa.switchAnalysis(inverters[0].apartments[0], batlist, inverters, outcomes, mode)
#
##Analysis for a specific inverter
#swa.switchAnalysis(inverters[0], batlist, inverters, outcomes, mode)
#
#
##Before x After analysis for apartment's self-consumption and self-sufficiency
#frame, visualization, apartmenttlist_string = swa.beforeAfterSwitching(inverters, mode="Show")
#
#



#%% Battery parameters analysis
#
##Before x After analysis for multiple battery capacities

##Setting up the simulation values - must be the same length!
#batcapacities = [0.0, 1.0, 2.0, 3.0, 5.0, 8.0, 10, 12, 15, 20, 25, 30]
#batCRate = [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]
#
##Indicating which parameter is being analysed
#parameter = "capacity"
##parameter = "cRate"
#
##Running battery analysis for both apartments and inverter placement to compare
##print("running for aps")
##baresults = swa.batAnalysis(inverters, batcapacities, batCRate, parameter, mode="ap")
##print("running for invs")
#baresults2 = swa.batAnalysis(inverters, batcapacities, batCRate, parameter, mode="inv")
##saving the results
#md.saveLoad(baresults2, 'batcapacity.pickle', 'save')       




#%% Creating a load profile for each apartment

#Running the analysis of the apartment as is
#sa.Analysis(cn.apartments('35', inverters, aptlist), inverters, invlist, aptlist, "all")
##Generating its load profile
#sa.loadProfile(cn.apartments('35', inverters, aptlist), inverters)

#Creating the overlapping consumption
#sa.loadOverlap(inverters)




#checking with plots
md.plt.figure()
md.plt.plot(inverters[0].timestamp, inverters[0].generation, linewidth = 0.7, label="gen")
#md.plt.plot(inverters[0].timestamp, inverters[0].apartments[0].consumption, '--', label="cons old")
#md.plt.plot(inverters[0].timestamp, inverters[0].apartments[0].consumption_new, 'k--', linewidth = 0.8, label="cons new")
md.plt.plot(inverters[0].timestamp, inverters[0].apartments[0].appliances[0].consumption, label="hp cons old")
#md.plt.plot(inverters[0].timestamp, inverters[0].apartments[0].appliances[0].consumption_new, label="hp cons new")
#md.plt.plot(inverters[0].timestamp, inverters[0].apartments[0].shifted, label="times of shift")



#%%%Switching Phase 3 implementation

#batlist = sw3.addBatteries(inverters, 2, 0.5, mode)

outcomes3, numberswitches3 = sw3.switchingPhase3(inverters, batlist, mode, "tepo")

md.plt.plot(inverters[0].timestamp, inverters[0].apartments[0].appliances[0].consumption, label="hp cons new")
md.plt.legend()


#%%
#checking with plots
md.plt.figure()
md.plt.plot(inverters[0].timestamp, inverters[0].generation, linewidth = 0.7, label="gen")
md.plt.plot(inverters[0].timestamp, inverters[0].apartments[0].consumption, '--', label="cons old")
md.plt.plot(inverters[0].timestamp, inverters[0].apartments[0].consumption_new, 'k--', linewidth = 0.8, label="cons new")
md.plt.plot(inverters[0].timestamp, inverters[0].apartments[0].appliances[0].consumption, label="hp cons old")
#md.plt.plot(inverters[0].timestamp, inverters[0].apartments[0].appliances[0].consumption_new, label="hp cons new")
md.plt.plot(inverters[0].timestamp, inverters[0].apartments[0].shifted, label="times of shift")
md.plt.legend()


sc3 = []
for i in inverters:
    for ap in i.apartments:
        sc3.append(ap.selfC_new)
        
print(md.np.mean(sc3))



#%% Classification of the apartments (clustering)
##
#modes = md.np.array(["period_avg", "period_total", "total+avg", "all", "switchII"])
#clustering, models, labels = cl.runClustering(modes, inverters)















