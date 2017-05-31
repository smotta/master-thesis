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


#%%Describing the system's connections

#Using a module for setting up the connection scheme. This enables the easy interchange between the two pilot projects
connection, connection_chnl, aptlist, invlist = cn.aquaradius()
#connection, connection_chnl, aptlist, invlist = cn.onsdorp()


#This is the folder containing all data for the apartments' generation and consumption
file_path = 'C:/Users/Sergio/Dropbox (Personal)/InnoEnergy/Master Thesis/ECN/Data from LENS/tki-data-20170418/locationdata/'
#TO-DO - Make this a prompt request with browsing window

#%%Creating the model and connections

#creating a list of Inverter objects to describe the system
inverters = []


#UNCOMMENT THIS IF THIS IS THE FIRST TIME WE RUN/CREATE THE SYSTEM MODEL - ANY NEW CHANGES SHOULD BE RUN AGAIN
#initializing each inverter with its apartments (and each with its appliances) - creating the whole system's hierarchy
#for inverter in invlist:
#    inverters.append(md.Inverter(file_path+inverter, connection[inverter], connection_chnl[inverter]))
#    
#md.saveLoad(inverters, "save")

#THIS IF THE SYSTEM MODEL IS ALREADY BUILT AND ONLY ANALYSIS ARE BEING PERFORMED
inverters = md.saveLoad(inverters, "load")

#%% Analysis of the whole system

#sa.Demo(inverters, invlist, aptlist)

 
#%% Run a data diagnostic to see where we have missing data

#sa.dataDiagnostics(inverters)
sa.Analysis(inverters[0].apartments[1].appliances[0], inverters, invlist, aptlist, "all")

#%% Classification of the apartments (clustering)
#
#
#modes = md.np.array(["period_avg", "period_total", "total+avg", "all"])
#labels =[]
#
#for i in modes:
#    model, aptid, database = cl.runKmeans(inverters, 4, i)
#    labels.append(model.labels_)
#    

#Check out k-NN method for classification    
#from sklearn.neighbors import KNeighborsClassifier
#
#x = database[:36]
#y = model.labels_[:36]
#
#neigh = KNeighborsClassifier(n_neighbors = 3)
#neigh.fit(x, y)














