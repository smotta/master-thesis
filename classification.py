# -*- coding: utf-8 -*-
"""
Created on Fri May 19 15:15:00 2017

@author: Sergio

This will be the module related to the classification of the apartments and everything related to machine learning or
forecasting. It will call functions from other modules and be called in the main function for the overall classification.
"""


import sysanalysis as sa
import matplotlib.pyplot as plt
import numpy as np

from sklearn.cluster import KMeans
import sklearn.metrics as sm
from mpl_toolkits.mplot3d import axes3d, Axes3D


#%% Defining a function to get anything related to the consumption of an item to classify it

def itemConsumption(item):
    
    #splitting the indexes that represent each day in the timestamp
    indexlist, daylist = sa.splitDays(item.timestamp)
    
    #initializing the consumption for each day
    consdaily=[]
    morningcons = []
    afternooncons = []
    nightcons = []
    consdailymean=[]
    consdailytotal=[]
    
    dailymorncons = []
    dailyaftcons = []
    dailynightcons = []
    
    #the day is snipped from the consumption; mean and total are calculated
    for i in indexlist:
        day = item.consumption[i[0]:i[1]]
        daytimestamp = item.timestamp[i[0]:i[1]]                                #getting the day timestamp
        
        #now we split the timestamps into morning, afternoon and night
        for i in range(len(daytimestamp)):
            if (daytimestamp[i].hour >= 4 and daytimestamp[i].hour < 12):
                morningcons.append(day[i])
            elif (daytimestamp[i].hour >= 12 and daytimestamp[i].hour < 20):
                afternooncons.append(day[i])
            else:
                nightcons.append(day[i])
        
        
        
        dailymorncons.append((np.mean(morningcons), np.sum(morningcons)))
        dailyaftcons.append((np.mean(afternooncons), np.sum(afternooncons)))
        dailynightcons.append((np.mean(nightcons), np.sum(nightcons)))
        consdaily.append(day)
        consdailymean.append(np.mean(day))
        consdailytotal.append(np.sum(day))


    return consdaily, daytimestamp, np.mean(consdailymean), consdailymean, np.sum(consdailytotal), consdailytotal, daylist, \
    dailymorncons, dailyaftcons, dailynightcons


#%% Running k-Means algorithm for a given dataset


def runKmeans(inverters, nclusters, mode):
    
    #getting the consumption for all apartments
    aptcons = []
    aptid = []
    aptdays = []
    aptconsAVG = []
    aptconsMEAN = []
    aptconsTotal = []
    aptconsSUM = []
    
    morningcons = []; afternooncons = []; nightcons = []  
    avgmorningcons = []; avgaftcons = []; avgnightcons = [] 
    
    #Creating the arrays for all apartments in the pilot
    for i in inverters:
        for j in i.apartments:
            consdaily, daytimestamp, avgmean, consdailymean, sumtotal, consdailytotal, daylist, \
            dailymorncons, dailyaftcons, dailynightcons = itemConsumption(j)
            
            aptid.append(j.ID)
            aptcons.append(consdaily)
            aptdays.append(daytimestamp)
            aptconsAVG.append(avgmean)
            aptconsMEAN.append(consdailymean)
            aptconsTotal.append(sumtotal)
            aptconsSUM.append(consdailytotal)
            
            
            morningcons.append(dailymorncons)
            avgmorningcons.append((sum(v[0] for v in dailymorncons)/len(dailymorncons), sum(v[1] for v in dailymorncons)))
            afternooncons.append(dailyaftcons)
            avgaftcons.append((sum(v[0] for v in dailyaftcons)/len(dailyaftcons), sum(v[1] for v in dailyaftcons)))
            nightcons.append(dailynightcons)
            avgnightcons.append((sum(v[0] for v in dailynightcons)/len(dailynightcons), sum(v[1] for v in dailynightcons)))
    
    
    aptcons = np.array(aptcons)
    aptconsAVG = np.array(aptconsAVG)
    aptconsMEAN = np.array(aptconsMEAN)
    aptconsTotal = np.array(aptconsTotal)
    aptconsSUM = np.array(aptconsSUM)   
        
    morncons = np.array([v[0] for v in avgmorningcons])
    morntotalcons = np.array([v[1] for v in avgmorningcons])
    aftcons = np.array([v[0] for v in avgaftcons])
    afttotalcons = np.array([v[1] for v in avgaftcons])
    nightcons = np.array([v[0] for v in avgnightcons])
    nighttotalcons = np.array([v[1] for v in avgnightcons])
    
    
    
    
    model = KMeans(nclusters)
    colormap = np.array(['red', 'lime', 'black', 'blue'])
    
    if mode == "period_avg":
        database = np.column_stack((morncons, aftcons, nightcons))
        model.fit(database)
        #Visualizing
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(morncons, aftcons, nightcons, c=colormap[model.labels_], marker='o')
        ax.scatter(model.cluster_centers_[:, 0],model.cluster_centers_[:,1],model.cluster_centers_[:,2], marker='x', color='b')   
        ax.set_xlabel('Morning avg (kWh)')
        ax.set_ylabel('Afternoon avg (kWh)')
        ax.set_zlabel('Night avg (kWh)')
        
        for i, txt in enumerate(aptid):
            ax.text(morncons[i], aftcons[i], nightcons[i], txt, size=7)
            
        plt.show()
    elif mode == "period_total":
        database = np.column_stack((morntotalcons, afttotalcons, nighttotalcons))
        model.fit(database)
        #Visualizing
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(morntotalcons, afttotalcons, nighttotalcons, c=colormap[model.labels_], marker='o')
        ax.scatter(model.cluster_centers_[:, 0],model.cluster_centers_[:,1],model.cluster_centers_[:,2], marker='x', color='b')   
        ax.set_xlabel('Morning total consumption (kWh)')
        ax.set_ylabel('Afternoon total consumption (kWh)')
        ax.set_zlabel('Night total consumption (kWh)')
        
        for i, txt in enumerate(aptid):
            ax.text(morntotalcons[i], afttotalcons[i], nighttotalcons[i], txt, size=7)
        
        plt.show()
        
    elif mode == "total+avg":
        database = np.column_stack((aptconsAVG, aptconsTotal))
        model.fit(database)
        #Visualizing
        plt.figure(figsize=(14,7))
        colormap = np.array(['red', 'lime', 'black', 'blue']) 
        plt.scatter(aptconsTotal, aptconsAVG, c=colormap[model.labels_], s=40)
        for i, txt in enumerate(aptid):
            plt.annotate(txt, (aptconsTotal[i], aptconsAVG[i]))
            
    elif mode == "all":
        print("Warning: No visualization possible as this classification has more than 3 dimensions\n")
        database = np.column_stack((aptconsAVG, aptconsTotal, morncons, morntotalcons, aftcons, afttotalcons, nightcons, nighttotalcons))
        model.fit(database)
    else:
        print("Mode not valid\n")
    
    
    cluster_order = np.argsort(model.cluster_centers_.mean(axis=1))
    print(cluster_order)
    for i in range(len(cluster_order)):
        print("Cluster %d is in position %d in order of consumption." %(cluster_order[i], i))
    
    
    
    return model, aptid, database
    
    #return aptcons, aptdays, aptconsAVG, aptconsMEAN, aptconsTotal, aptconsSUM, daylist, morningcons, afternooncons, nightcons, \
    #avgmorningcons, avgaftcons, avgnightcons   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    


