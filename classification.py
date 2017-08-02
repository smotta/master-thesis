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
import pandas as pd

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
    
    
    #after switching phase II
    dailyER = []
    dailyGF = []
    dailyBC = []
    
    #the day is snipped from the consumption; mean and total are calculated
    for i in indexlist:
        day = item.consumption[i[0]:i[1]]
        daytimestamp = item.timestamp[i[0]:i[1]]                                #getting the day timestamp
        ER = item.energyreceived[i[0]:i[1]]
        GF = item.gridfeedin[i[0]:i[1]]
        BC = item.batcharge[i[0]:i[1]]
        
        
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


        #daily values for ER, GF and BC - this is the sum of values per day
        dailyER.append(np.sum(ER))
        dailyGF.append(np.sum(GF))
        dailyBC.append(np.sum(BC))


    return consdaily, daytimestamp, np.mean(consdailymean), consdailymean, np.sum(consdailytotal), consdailytotal, daylist, \
    dailymorncons, dailyaftcons, dailynightcons, dailyER, dailyGF, dailyBC


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
    
    #morning, afternoon and night
    morningcons = []; afternooncons = []; nightcons = []  
    avgmorningcons = []; avgaftcons = []; avgnightcons = [] 
    
    #After switching Phase II - energy received, grid feed-in and battery charge
    aptER = []
    aptGF = []
    aptBC = []
    
    #Creating the arrays for all apartments in the pilot
    for i in inverters:
        for j in i.apartments:
            consdaily, daytimestamp, avgmean, consdailymean, sumtotal, consdailytotal, daylist, \
            dailymorncons, dailyaftcons, dailynightcons, dailyER, dailyGF, dailyBC = itemConsumption(j)
            
            aptid.append(j.ID)
            aptcons.append(consdaily)
            aptdays.append(daytimestamp)
            aptconsAVG.append(avgmean)
            aptconsMEAN.append(consdailymean)
            aptconsTotal.append(sumtotal)
            aptconsSUM.append(consdailytotal)
            
            #energy received, grid feed-in and battery charge per day (total values)
            aptER.append(np.sum(dailyER))
            aptGF.append(np.sum(dailyGF))
            aptBC.append(np.sum(dailyBC))
            
            
            morningcons.append(dailymorncons)
            avgmorningcons.append((sum(v[0] for v in dailymorncons)/len(dailymorncons), sum(v[1] for v in dailymorncons)))
            afternooncons.append(dailyaftcons)
            avgaftcons.append((sum(v[0] for v in dailyaftcons)/len(dailyaftcons), sum(v[1] for v in dailyaftcons)))
            nightcons.append(dailynightcons)
            avgnightcons.append((sum(v[0] for v in dailynightcons)/len(dailynightcons), sum(v[1] for v in dailynightcons)))


    
    morncons = np.array([v[0] for v in avgmorningcons])
    morntotalcons = np.array([v[1] for v in avgmorningcons])
    aftcons = np.array([v[0] for v in avgaftcons])
    afttotalcons = np.array([v[1] for v in avgaftcons])
    nightcons = np.array([v[0] for v in avgnightcons])
    nighttotalcons = np.array([v[1] for v in avgnightcons])
    
    
    
    
    model = KMeans(nclusters, random_state = 0)
    colormap = np.array(['red', 'lime', 'black', 'blue'])
    
    if mode == "period_avg":
        database = np.column_stack((morncons, aftcons, nightcons))
        model.fit(database)
        #correcting the labels
        model.labels_ = correctLabels(model, nclusters)
        #setting the clusters as parameters in each apartment
        setClusters(inverters, model, aptid)        
        #Visualizing
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(morncons, aftcons, nightcons, c=colormap[model.labels_], marker='o')
        ax.scatter(model.cluster_centers_[:, 0],model.cluster_centers_[:,1],model.cluster_centers_[:,2], marker='x', color='c', linewidth=1.5)   
        ax.set_xlabel('Morning avg (kWh)')
        ax.set_ylabel('Afternoon avg (kWh)')
        ax.set_zlabel('Night avg (kWh)')
        ax.set_title('Average consumption per Period of Day')
        for i, txt in enumerate(aptid):
            ax.text(morncons[i], aftcons[i], nightcons[i], txt, size=7)
            
        plt.show()
    elif mode == "period_total":
        database = np.column_stack((morntotalcons, afttotalcons, nighttotalcons))
        model.fit(database)
        #correcting the labels
        model.labels_ = correctLabels(model, nclusters)
        #setting the clusters as parameters in each apartment
        setClusters(inverters, model, aptid)
        #Visualizing
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(morntotalcons, afttotalcons, nighttotalcons, c=colormap[model.labels_], marker='o')
        ax.scatter(model.cluster_centers_[:, 0],model.cluster_centers_[:,1],model.cluster_centers_[:,2], marker='x', color='c', linewidth=1.5)   
        ax.set_xlabel('Morning total consumption (kWh)')
        ax.set_ylabel('Afternoon total consumption (kWh)')
        ax.set_zlabel('Night total consumption (kWh)')
        ax.set_title('Total consumption per Period of Day')
        
        for i, txt in enumerate(aptid):
            ax.text(morntotalcons[i], afttotalcons[i], nighttotalcons[i], txt, size=7)
        
        plt.show()
        
    elif mode == "total+avg":
        database = np.column_stack((aptconsAVG, aptconsTotal))
        model.fit(database)
        #correcting the labels
        model.labels_ = correctLabels(model, nclusters) 
        #setting the clusters as parameters in each apartment
        setClusters(inverters, model, aptid)
        #Visualizing
        plt.figure(figsize=(14,7))
        colormap = np.array(['red', 'lime', 'black', 'blue']) 
        plt.scatter(aptconsTotal, aptconsAVG, c=colormap[model.labels_], s=40)
        plt.ylabel('Average consumption (kWh)')
        plt.xlabel('Total consumption (kWh)')
        plt.title('Total consumption x Average consumption clusterization')
        for i, txt in enumerate(aptid):
            plt.annotate(txt, (aptconsTotal[i], aptconsAVG[i]))
    
    #Adding modes for switching phase II
    elif mode == "switchII":
        database = np.column_stack((aptER, aptGF, aptBC))
        model.fit(database)
        #correcting the labels
        model.labels_ = correctLabels(model, nclusters)   
        #setting the clusters as parameters in each apartment
        setClusters(inverters, model, aptid)
        #Visualizing
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(aptER, aptGF, aptBC, c=colormap[model.labels_], marker='o')
        ax.scatter(model.cluster_centers_[:, 0],model.cluster_centers_[:,1],model.cluster_centers_[:,2], marker='x', color='c', linewidth=1.5)   
        ax.set_xlabel('Total Energy Received (kWh)')
        ax.set_ylabel('Total Grid Feed-in (kWh)')
        ax.set_zlabel('Total Battery Charge (kWh)')
        ax.set_title('Switching Phase II Values')
        
        for i, txt in enumerate(aptid):
            ax.text(aptER[i], aptGF[i], aptBC[i], txt, size=7)
        
        plt.show()


        
    elif mode == "all":
        print("Clusterization considering all parameters.\nWarning: No visualization possible as this classification has more than 3 dimensions\n")
        database = np.column_stack((aptconsAVG, aptconsTotal, morncons, morntotalcons, aftcons, afttotalcons, nightcons, nighttotalcons))
        model.fit(database) 
        #correcting the labels
        model.labels_ = correctLabels(model, nclusters)  
        setClusters(inverters, model, aptid)
    else:
        print("Mode not valid\n")

    return model, aptid, database
    
    #return aptcons, aptdays, aptconsAVG, aptconsMEAN, aptconsTotal, aptconsSUM, daylist, morningcons, afternooncons, nightcons, \
    #avgmorningcons, avgaftcons, avgnightcons   
    
def setClusters(inverters, model, aptid):
    """Function to set which cluster the apartment belongs to as a parameter of the objects Apartment"""
    
    count = 0
    for i in inverters:
        for ap in i.apartments:
            if ap.ID == aptid[count]:
                ap.cluster = model.labels_[count]
            count+= 1
    
#%% Running the clustering for different parameters
def runClustering(modes, inverters):
    """Run the clustering for different set modes and return a comparison between the results obtained"""
    labels = []
    models = []
    for i in modes:
        model, aptid, database = runKmeans(inverters, 4, i)
        labels.append(model.labels_)
        models.append(model)
        
    clustering = pd.DataFrame(np.transpose(np.array(labels)), index=aptid, columns = modes)
    
    #writing to excel
    savefile = 'C:/Users/Sergio/Dropbox (Personal)/InnoEnergy/Master Thesis/ClusteringResults.xls'
    #Other computer:
    #savefile = 'C:/Users/Sergio/Dropbox/InnoEnergy/Master Thesis/ClusteringResults.xls'
    writer = pd.ExcelWriter(savefile)
    clustering.to_excel(writer, sheet_name='Clustering comparison')
    writer.save()
    
    return clustering, models, labels    
    
    

#%% K-NN CLASSIFICATION


##Check out k-NN method for classification    
#from sklearn.neighbors import KNeighborsClassifier
#
#x = database[:36]
#y = model.labels_[:36]
#
#neigh = KNeighborsClassifier(n_neighbors = 3)
#neigh.fit(x, y)

   
#%% AUXILIARY FUNCTIONS

def correctLabels(model, nclusters):
    """Function to make up for the random initialization of the clusters in the k-means method; 
    Sequence the labels from highest to lowest for better comparison between different clusterings"""
    
    #creating a look-up table
    indexes = np.argsort(model.cluster_centers_.sum(axis=1))
    lookuptable = np.zeros_like(indexes)
    lookuptable[indexes] = np.arange(nclusters)
    
    #redefining the labels
    return lookuptable[model.labels_]
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    


