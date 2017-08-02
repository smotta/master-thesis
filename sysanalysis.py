# -*- coding: utf-8 -*-
"""
Created on Wed May  3 21:34:16 2017

@author: Sergio
This file will serve to perform the statistical analysis of the full system modeled in the main file.
Here all the code to run model.Analysis() for all objects will be done - This is expected to take quite some time,
as there will be 7 inverters, 38 apartments and a number of appliances to be analysed.

Yet again, this full analysis will be performed a few times just for presentation purposes, as it is not extremely
relevant for our model. 
"""
import model as md
import connection as cn
import matplotlib.pyplot as plt
import sysanalysisprint as sap
from matplotlib.ticker import MaxNLocator





#%% ###########################################################################
""" FUNCTIONS FOR THE SYSTEM ANALYSIS AS IS - NO SWITCHING ANALYZED """
#%% Analysis function

#A generic analysis function that receives an object as an input and returns a thorough analysis of it, with plots and relevant information.
#The intent of this function is to perform a detailed overview of each object in the system scope, and be able to analyze its performance for different
#scenarios. 
def Analysis(item, inv, invlist, aptlist, mode):
        
    systeminfo = [0, 0, 0, 0, 0]
    systeminfo[0], systeminfo[1] = md.totalSystemValues(inv)
    
    if type(item) == md.Inverter:
        itemconsumption = sum(item.consumption)
        itemgeneration = sum(item.generation)
        
        #Calculate the consumption of all apartments connected to this inverter and find what is the maximum
        apartmentconsumption = []
        for i in range(len(item.apartments)):
            apartmentconsumption.append(sum(item.apartments[i].consumption))
        maxapartmentcons = item.apartments[apartmentconsumption.index(max(apartmentconsumption))]
        
        #Calculate the generation of all apartments connected to this inverter and find what is the maximum
        apartmentgeneration = []
        for i in range(len(item.apartments)):
            apartmentgeneration.append(sum(item.apartments[i].generation))
        maxapartmentgen = item.apartments[apartmentgeneration.index(max(apartmentgeneration))]        
       
        #Printing the information
                  
        sap.getPrint_inv(mode, item, systeminfo, itemconsumption, itemgeneration, maxapartmentcons, maxapartmentgen)
            
        return (itemconsumption, itemgeneration, maxapartmentcons, maxapartmentgen)
        
    elif type(item) == md.Apartment:
        
        #calculating the inverter's consumption
        systeminfo[2] = sum(cn.inverters(item.inv, inv, invlist).consumption)
        systeminfo[3] = sum(cn.inverters(item.inv, inv, invlist).generation)
        
        itemconsumption = sum(item.consumption)
        itemgeneration = sum(item.generation)

                
        #Calculate the consumption of all appliances connected to this apartment and find what is the maximum
        applianceconsumption = []
        
        if len(item.appliances) > 0:
            for i in range(len(item.appliances)):
                applianceconsumption.append(sum(item.appliances[i].consumption))
            maxappliancecons = item.appliances[applianceconsumption.index(max(applianceconsumption))]
        else:
            maxappliancecons = 0
     
        #Printing the information
        sap.getPrint_apt(mode, item, systeminfo, itemconsumption, itemgeneration, maxappliancecons)

        return (itemconsumption, itemgeneration, maxappliancecons)
       
    elif type(item) == md.Appliance:
        #calculating the apartment's information:
        systeminfo[4] = sum(cn.apartments(item.apt, inv, aptlist).consumption)
        
        itemconsumption = sum(item.consumption)

        #Printing the information
        sap.getPrint_app(mode, item, systeminfo, itemconsumption, inv, aptlist)
        return (itemconsumption)
        
#%% System Analysis for max and min objects

#A function to run the whole system analysis and get the max/min consumers for the respective pilot
def minmaxAnalysis(inverters, invlist, aptlist, show):
 
   
    #### Initializing lists for the calculated parameters ####
    #initializing the inverter parameters lists - consumption, generation; max apartment consumption and generation
    inv_cons = []; inv_gen = []
    inv_maxapc = []; inv_maxapg = []
    inv_id = []
    
    #initializing the apartment parameter lists
    apt_cons = []; apt_gen = []
    apt_id = []
    apt_maxapp = []; 
    
    #initializing the appliances parameter lists
    app_cons = []; app_id = []
    
    #### Running the whole system analysis in "silent" mode - just returning values ####
    for i in range(len(inverters)):
        #calculating the analysis for the inverters, one at a time
        invc, invg, aptc, aptg = Analysis(inverters[i], inverters, invlist, aptlist, "silent")     
        inv_cons.append(invc); inv_gen.append(invg)
        inv_maxapc.append(aptc); inv_maxapg.append(aptg);
        inv_id.append(inverters[i].ID)
        
        for j in range(len(inverters[i].apartments)):
            #calculating the analysis for the apartments of each inverter
            apcons, apgen, maxappcons = Analysis(inverters[i].apartments[j], inverters, invlist, aptlist, "silent")
            apt_cons.append(apcons); apt_gen.append(apgen); apt_maxapp.append(maxappcons)
            apt_id.append(inverters[i].apartments[j].ID)
            
            for k in range(len(inverters[i].apartments[j].appliances)):
                #calculating the analysis for the appliances of each apartment
                appcons= Analysis(inverters[i].apartments[j].appliances[k], inverters, invlist, aptlist, "silent")
                app_cons.append(appcons)
                app_id.append(inverters[i].apartments[j].appliances[k].ID)
            
    #This gives us the analysis and cons/gen values listed for all entities in our pilot. We then find the maximum value in these lists:
        
    #### Getting the max/min indexes in these lists ####
    #Inverters:
    inv_cons_idx = inv_cons.index(max(inv_cons)); inv_gen_idx = inv_gen.index(max(inv_gen))
    inv_cons_idxmin = inv_cons.index(min(inv_cons)); inv_gen_idxmin = inv_gen.index(min(inv_gen))
    
    maxinv = inv_id[inv_cons_idx]
    maxinvgen = inv_id[inv_gen_idx]
    mininv = inv_id[inv_cons_idxmin]
    mininvgen = inv_id[inv_gen_idxmin]
        
    #Apartments:
    cons_idx = apt_cons.index(max(apt_cons)); gen_idx = apt_gen.index(max(apt_gen))
    cons_idxmin = apt_cons.index(min(apt_cons)); gen_idxmin = apt_gen.index(min(apt_gen))
    
    maxap = apt_id[cons_idx]
    maxapgen = apt_id[gen_idx]
    minap = apt_id[cons_idxmin]
    minapgen = apt_id[gen_idxmin]
    
    #Appliances:
    app_idx = app_cons.index(max(app_cons)); app_idxmin = app_cons.index(min(app_cons))
        
    maxapp = app_id[app_idx]
    minapp = app_id[app_idxmin]
    
    #Printing the information
    sap.getPrint_minmax(show, inv_cons, inv_gen, maxinv, maxinvgen, mininv, mininvgen, apt_cons, apt_gen, minap, maxap, minapgen, maxapgen, app_cons, maxapp, minapp)
    
    return maxinv, mininv, maxinvgen, mininvgen, maxap, minap, maxapgen, minapgen, maxapp, minapp
    #Returns a list of the IDs of the min/max appliances

#%% System Analysis using all previous analysis

#function to create plots of average consumption compared to max and min
def sysAnalysisAvg(inv, invlist, aptlist):
    """Function to get the average consumption and generation over all apartments; It also provides with the std deviation of the consumption."""
    #Using two auxiliary functions, we get all the timestamps that occur in our data
    alltimestamps = sysAllTimestamps(inv)
    #And the consumption, generation and which apartment is associated to each one of these single timestamps
    totalcons, totalgen, totalID = setTimestampData(inv, alltimestamps)
    
    #Initializing the arrays for mean, standard deviation, max and min
    #consumption
    meanc = md.np.zeros(len(alltimestamps)); stdc = md.np.zeros(len(alltimestamps))
    maximc = md.np.zeros(len(alltimestamps)); minimc = md.np.zeros(len(alltimestamps)) 
    
    #generation
    meang = md.np.zeros(len(alltimestamps)); stdg = md.np.zeros(len(alltimestamps))
    maximg = md.np.zeros(len(alltimestamps)); minimg = md.np.zeros(len(alltimestamps)) 
    
    #calculating average, standard deviation, max and min for consumption and generation in apartments
    for i in range(len(alltimestamps)):
        meanc[i] = md.np.mean(totalcons[i])
        stdc[i] = md.np.std(totalcons[i])
        maximc[i] = max(totalcons[i])
        minimc[i] = min(totalcons[i])
        
        meang[i] = md.np.mean(totalgen[i])
        stdg[i] = md.np.std(totalgen[i])
        maximg[i] = max(totalgen[i])
        minimg[i] = min(totalgen[i])
      
    #getting the max and min inverters, apartments and appliances for inserting them in the plot for comparison - using minmaxAnalysis() above
    maxinv, mininv, maxinvgen, mininvgen, maxap, minap, maxapgen, minapgen, maxapp, minapp = minmaxAnalysis(inv, invlist, aptlist, "hide")
    
    #Printing the consumption data
    plt.figure()
    plt.ylabel("Instantaneous Consumption (kWh)")
    plt.xlabel("Time (timestamp)")
    plt.title("Average consumption of apartment versus highest and lowest consuming apartments")
    plt1, = plt.plot(cn.apartments(maxap, inv, aptlist).timestamp, cn.apartments(maxap, inv, aptlist).consumption, 'r--', label="Maximum consumption apartment " + cn.apartments(maxap, inv, aptlist).ID)
    plt2, = plt.plot(cn.apartments(minap, inv, aptlist).timestamp, cn.apartments(minap, inv, aptlist).consumption, 'g--', label="Minimum consumption apartment " + cn.apartments(minap, inv, aptlist).ID)
    plt3, = plt.plot(alltimestamps, meanc, label="Average apartment consumption")
    plt.legend(handles=[plt1, plt2, plt3])
    
    
    #Printing the generation data
    plt.figure()
    plt.ylabel("Instantaneous Generation (kWh)")
    plt.xlabel("Time (timestamp)")
    plt.title("Average generation of all apartments versus highest and lowest generation for apartments")
    plt1, = plt.plot(cn.apartments(maxapgen, inv, aptlist).timestamp, cn.apartments(maxapgen, inv, aptlist).consumption, 'r--', label="Maximum generation apartment " + cn.apartments(maxapgen, inv, aptlist).ID)
    plt2, = plt.plot(cn.apartments(minapgen, inv, aptlist).timestamp, cn.apartments(minapgen, inv, aptlist).consumption, 'g--', label="Minimum generation apartment " + cn.apartments(minapgen, inv, aptlist).ID)
    plt3, = plt.plot(alltimestamps, meang, label="Average apartment generation")
    plt.legend(handles=[plt1, plt2, plt3])
        
#%% Full system Analysis


#calculating the full system parameters and plotting the full system consumption and generation
def pilotAnalysis(inverters):
    """Function to run the full system analysis in consumption, generation, self-consumption and self-sufficiency with plots"""
    #Merging all the apartments into arrays with generation and consumption for the full system
    timestamp = sysAllTimestamps(inverters)
    allconsumption, allgeneration, ID = setTimestampData(inverters, timestamp) 
    
    consumption = md.np.zeros(len(timestamp))
    generation = md.np.zeros(len(timestamp))
    
    for i in range(len(timestamp)):
        consumption[i] = sum(allconsumption[i])
        generation[i] = sum(allgeneration[i])   
    
    #Calculating the full system self-consumption and self-sufficiency
    selfC = md.selfConsumption(consumption, generation, timestamp, item=inverters[0])
    selfS = md.selfSufficiency(consumption, generation, timestamp, item=inverters[0])
    selfCinst = md.selfConsumptionInst(consumption, generation, timestamp, item=inverters[0])
    selfSinst = md.selfSufficiencyInst(consumption, generation, timestamp, item=inverters[0])
    #Note: This gives how much the system would have as self-consumption and self-sufficiency if there was no switching - electricity would flow to
    #all the apartments at the same time. It is a rough estimate on the actual potention for this.

    #Plots for showing the whole system parameters
    plt.figure()
    plt.title("Self-consumption and self-sufficiency of the full Pilot")
    plt.xlabel("Time (timestamp)")
    plt.ylabel("Self-consumption and self-sufficiency (%)")
    plt1, = plt.plot(timestamp, selfCinst, label="System self consumption")
    plt2, = plt.plot(timestamp, selfSinst, label="System self sufficiency")
    plt3, = plt.plot(timestamp, consumption, label="System total consumption")
    plt4, = plt.plot(timestamp, generation, label="System total generation")
    plt.legend(handles=[plt1, plt2, plt3, plt4])
    
    #Consumption     
    fig = plt.figure()
    plt.title("System consumption")
    ax = fig.add_subplot((len(inverters)+1),1,1)
    ax.plot(timestamp, consumption)
    for i in range(len(inverters)):
        ax1 = fig.add_subplot((len(inverters)+1),1,i+2)
        ax1.plot(inverters[i].timestamp, inverters[i].consumption)
    plt.xlabel("Time (timestamp)")
    plt.ylabel("Consumption (kWh)")
    
    plt.figure()
    plt.title("Total consumption versus inverter's")
    totalplt, = md.plt.plot(timestamp, consumption, label="Total system generation")
    handl = [totalplt]
    for i in range(len(inverters)):
        handl1, = plt.plot(inverters[i].timestamp, inverters[i].consumption, label="Consumption for inverter " + inverters[i].ID)
        handl.append(handl1)
    plt.legend(handles=handl)
    plt.xlabel("Time (timestamp)")
    plt.ylabel("Consumption (kWh)")
    
    
    #Generation 
    fig = plt.figure()
    plt.title("System generation")
    ax = fig.add_subplot(8,1,1)
    ax.plot(timestamp, generation)
    plt.xlabel("Time (timestamp)")
    plt.ylabel("Generation (kWh)")
    for i in range(len(inverters)):
        ax1 = fig.add_subplot(8,1,i+2)
        ax1.plot(inverters[i].timestamp, inverters[i].generation)

    
    plt.figure()
    plt.title("Total generation versus inverter's")
    totalplt, = md.plt.plot(timestamp, generation, label="Total system generation")
    handl = [totalplt]
    for i in range(len(inverters)):
        handl1, = plt.plot(inverters[i].timestamp, inverters[i].generation, label="Generation for inverter " + inverters[i].ID)
        handl.append(handl1)
    plt.legend(handles=handl)
    plt.xlabel("Time (timestamp)")
    plt.ylabel("Generation (kWh)")
    #Printing the information:
    sap.getPrint_pilotAnalysis(consumption, generation, selfC, selfS)
    
    return generation, consumption, timestamp, selfC, selfS, selfCinst, selfSinst
    
#%% Self-consumption and self-sufficiency calculation

#This is a function to print and show all apartment's self-consumption and self-sufficiency and the full system average
def selfCselfS(inverters):
    """Function to calculate and show the average self-consumption and self-sufficiency of the system"""
    somaC = 0
    somaS = 0
    print("System self-consumption and self-sufficiency analysis:")
    for i in inverters:
        for j in range(len(i.apartments)):
            somaC += i.apartments[j].selfC
            somaS += i.apartments[j].selfS
            #Printing the self-consumption and self-sufficiency for each individual apartment:
            print("Apartment " + i.apartments[j].ID + " self-consumption is %.2f" %(i.apartments[j].selfC*100))
            print("Apartment " + i.apartments[j].ID + " self-sufficiency is %.2f\n" %(i.apartments[j].selfS*100))
    
    print("Average self-consumption for all 38 apartments is %.2f \n" %(somaC/38 * 100))
    print("Average self-sufficiency for all 38 apartments is %.2f \n" %(somaS/38 * 100))
    
#%% Date Analysis function

#This function is used for a specific date/period analysis, which will be useful in the end to visualize data

def analysisDay(item, date):
    """Function to perform and split the analysis for a specific date or time period"""
    #If there is just one date specified, the analysis will be for that 24 hour period
    if type(date) == str:
        data = md.datetime.strptime(date, "%Y-%m-%d")
        indexes = []
        for i in range(len(item.timestamp)):
            if item.timestamp[i].date() == data.date():
                indexes.append(i)
                
        #Finding the values for consumption, generation, self-consumption and self-sufficiency for that day  
        datetimestamp = item.timestamp[indexes[0]:indexes[-1]]
        dateconsumption = item.consumption[indexes[0]:indexes[-1]]
        dategeneration = item.generation[indexes[0]:indexes[-1]]
        dateSC = md.selfConsumption(dateconsumption, dategeneration, datetimestamp)
        dateSCinst = md.selfConsumptionInst(dateconsumption, dategeneration, datetimestamp)
        dateSS = md.selfSufficiency(dateconsumption, dategeneration, datetimestamp)
        dateSSinst = md.selfSufficiencyInst(dateconsumption, dategeneration, datetimestamp)
        
        plt.figure()
        plt.title("Self-consumption and self-sufficiency analysis for date " + date)
        plt.plot(datetimestamp, dateSCinst)
        plt.plot(datetimestamp, dateSSinst)
        plt.plot(datetimestamp, dateconsumption)
        plt.plot(datetimestamp, dategeneration)
        plt.xlabel("Time (timestamp)")
        plt.ylabel("Instantaneous energy (kWh)")
        
        print("\n# The self-consumption for that day was %.2f and the self-sufficiency was %.2f\n\n" %(dateSC*100, dateSS*100))
        return datetimestamp, dateconsumption, dategeneration, dateSC, dateSCinst, dateSS, dateSSinst
    #If there are two dates specified, we strip the time period
    else:
        data1 = md.datetime.strptime(date[0], "%Y-%m-%d")
        data2 = md.datetime.strptime(date[1], "%Y-%m-%d")
        indexes = []
        for i in range(len(item.timestamp)):
            if item.timestamp[i].date() == data1.date() or item.timestamp[i].date() == data2.date():
                indexes.append(i)
        #Finding the values for consumption, generation, self-consumption and self-sufficiency for that time period        
        datetimestamp = item.timestamp[indexes[0]:indexes[-1]]
        dateconsumption = item.consumption[indexes[0]:indexes[-1]]
        dategeneration = item.generation[indexes[0]:indexes[-1]]
        dateSC = md.selfConsumption(dateconsumption, dategeneration, datetimestamp)
        dateSCinst = md.selfConsumptionInst(dateconsumption, dategeneration, datetimestamp)
        dateSS = md.selfSufficiency(dateconsumption, dategeneration, datetimestamp)
        dateSSinst = md.selfSufficiencyInst(dateconsumption, dategeneration, datetimestamp)
              
        
        plt.figure()
        plt.title("Self-consumption and self-sufficiency analysis for dates " + date[0] + " - " + date[1])
        plt.plot(datetimestamp, dateSCinst)
        plt.plot(datetimestamp, dateSSinst)
        plt.plot(datetimestamp, dateconsumption)
        plt.plot(datetimestamp, dategeneration)
        if type(item) == md.Apartment:
            dateenergyreceived = item.energyreceived[indexes[0]:indexes[-1]]
            plt.plot(datetimestamp, dateenergyreceived)
            
        plt.xlabel("Time (timestamp)")
        plt.ylabel("Instantaneous energy (kWh)")
        
        print("\n# The self-consumption for that period was %.2f and the self-sufficiency was %.2f\n\n" %(dateSC*100, dateSS*100))
        return datetimestamp, dateconsumption, dategeneration, dateSC, dateSCinst, dateSS, dateSSinst






#%%% Defining the load profile of each apartment

#This is a function to establish a load profile of each individual apartment
def loadProfile(item, inverters):
    """Function to analyse and define an average load profile for each apartment of a pilot"""
    
    #as all apartments are already set with the same timestamp (done so in md.equality)
    indexlist, datearray = splitDays(inverters[0].timestamp)

    setApartParameters(inverters, indexlist)
    setApplianceParameters(inverters, indexlist)

    times_str = []; times = [] 
    for i in range(96):
        times_str.append(item.timestamp[i].time().strftime("%H:%M"))    
        times.append(item.timestamp[i].time())
        
    fig, axisarr = plt.subplots(nrows=2, ncols=1, sharex=True)
    axisarr[0].set_title("Average Load Profile of Apartment "+ item.ID)
    axisarr[0].plot(range(len(times)), item.dailyavg)
    axisarr[0].set_ylabel("Average Load (kWh)")
    axisarr[0].text(1.5, max(item.dailyavg)-0.01, 'Average consumption per day of %.2f kWh' %(sum(item.dailyavg)))
    axisarr[1].set_title("Load Distribution Per Timestamp of Ap "+ item.ID)
    axisarr[1].boxplot(item.dailycons)
    axisarr[1].set_ylabel("Distribution of Loads (kWh)")
    axisarr[1].set_ylim([0, 0.5])
    axisarr[1].grid(True, linestyle='-', color='lightgrey', alpha=0.5)
    plt.xlabel("Time (timestamp)")
    plt.xticks(range(1, len(times_str)+1), times_str, rotation = 90, fontsize=4)
    plt.savefig("images/ap"+item.ID+"avg.png", bbox_inches = "tight")
    

    
    f, axarr = plt.subplots(nrows=len(item.appliances), ncols=1, sharex=True)
    plt.suptitle("Appliance Times of Use per Timestamp for Ap. " + item.ID)
    plt.xticks(range(len(times_str)), times_str, rotation = 90, fontsize=4)
    for i in range(len(item.appliances)):
        axarr[i].bar(range(len(times)), item.appliances[i].counting)
        axarr[i].text(.5,.9, item.appliances[i].ID, horizontalalignment='center',transform=axarr[i].transAxes, fontsize=6, color='red')
        axarr[i].set_ylabel("Times used", fontsize=6)
        axarr[i].set_ylim([0, max(item.appliances[i].counting)+30])
#        axarr[i].title(item.appliances[i].ID)
#        axarr[i].ylabel("Times used")
#        ax1 = fig2.add_subplot(len(item.appliances),1,i+1)
#        ax1.bar(range(len(times)), item.appliances[i].counting, alpha=0.5)
        plt.xlabel("Time (timestamp)")
        plt.savefig("images/ap"+item.ID+"appl.png", bbox_inches = "tight")
       # plt.tick_params(axis='x', nticks=10)


#Creating the load overlap
def loadOverlap(inverters):
    
    times_str=[]; times=[]
    for i in range(96):
        times_str.append(inverters[0].timestamp[i].time().strftime("%H:%M"))    
        times.append(inverters[0].timestamp[i].time())
    
    
    #plotting the average consumption for each apartment
    apartaverages = []
    md.plt.figure()
    for i in inverters:
        for ap in i.apartments:
            apartaverages.append(ap.dailyavg)
            md.plt.plot(range(96), ap.dailyavg, linewidth=0.5)
            
    aptavg_trs = md.np.array(apartaverages).transpose()
    
    #plotting the min, max and mean consumption
    mincons=[]; maxcons=[];avgcons = []
    for i in range(len(aptavg_trs)):
        mincons.append(min(aptavg_trs[i]))
        maxcons.append(max(aptavg_trs[i]))
        avgcons.append(md.np.mean(aptavg_trs[i]))
    
    md.plt.plot(range(96), mincons, 'k--', linewidth=2.0, label="Minimal Consumption")
    md.plt.plot(range(96), maxcons, 'r--', linewidth=2.0, label="Maximal Consumption")
    md.plt.plot(range(96), avgcons, 'b--', linewidth=2.0, label="Average Consumption")
    md.plt.fill_between(range(96), mincons, alpha=0.2)
    plt.legend()
    plt.xticks(range(len(times_str)), times_str, rotation = 90, fontsize=6)
    plt.xlabel("Timestamps in a day")
    plt.ylabel("Average Consumption per Timestamp (kWh)")
    plt.title("Average Load Profile and Pilot Baseload")
    plt.text(1.5, max(maxcons)-0.01, 'Average consumption per day of %.2f kWh' %(sum(avgcons)))

    
#    
#    md.plt.figure()
#    apartcons = []
#    for i in inverters:
#        for ap in i.apartments:
#            apartcons.append(ap.consumption)
#            md.plt.plot(ap.timestamp, ap.consumption, linewidth=0.5)
#    
#    aptcns_trs = md.np.array(apartcons).transpose()
#    
#    mincons = []; maxcons = []; avgcons = []
#    for i in range(len(aptcns_trs)):
#        mincons.append(min(aptcns_trs[i]))
#        maxcons.append(max(aptcns_trs[i]))
#        avgcons.append(md.np.mean(aptcns_trs[i]))
#    
#    md.plt.plot(inverters[0].apartments[0].timestamp, mincons, 'k--', linewidth=2.0)
#    md.plt.plot(inverters[0].apartments[0].timestamp, maxcons, 'r--', linewidth=2.0)
#    md.plt.plot(inverters[0].apartments[0].timestamp, avgcons, 'b--', linewidth=2.0)
#    md.plt.fill_between(inverters[0].apartments[0].timestamp, mincons, alpha=0.2)   

    

####Auxiliary functions for load profile
def setApartParameters(inverters, indexlist):
    #setting apartment's parameters
    for i in inverters:
        for ap in i.apartments:
            dailycons = []; dailyavg = []
            for time in indexlist:
                daysplit = ap.consumption[time[0]:time[1]]
                if len(daysplit) == 96:
                    dailycons.append(daysplit)
            
            hourlyvalues = md.np.array(dailycons).transpose()
            for v in hourlyvalues:
                dailyavg.append(md.np.mean(v))
            
            ap.dailycons = md.np.array(dailycons)
            ap.dailyavg = dailyavg
        

def setApplianceParameters(inverters, indexlist):
    #setting appliances:
    for i in inverters:
        for ap in i.apartments:
            for appl in ap.appliances:
                dailycons = []
                for time in indexlist:
                    daysplit = appl.consumption[time[0]:time[1]]
                    if len(daysplit) == 96:
                        dailycons.append(daysplit)
                appl.dailycons = md.np.array(dailycons)
                appl.conspertimestamp = appl.dailycons.transpose()
                #setting the appliances consumption time
    
                for moment in appl.conspertimestamp:
                    moment[moment > 0] = 1
                appl.counting = sum(appl.conspertimestamp.transpose())






#%% Defining a DEMO function to quickly run the system's tests

#This is a function to run different analysis for showing the model
def Demo(inverters, invlist, aptlist):
    """Demonstration of the model analysis capabilities"""
    mode = input("""##\nPlease insert one of the options:\n\n
            "system" - for a full system analysis\n
            "max" - for the top consumer entities\n
            "all" - for all 7 inverters, 38 apartments, 186 appliances analysis\n
            "inv___"- for an individual analysis of the inverter of choice\n
            "apt___" - for an individual analysis of the apartment of choice\n
            "app___ - for an individual analysis of the appliance of choice\n
            "selfCS" - for the overall view of self-consumption and self-sufficiency of the system\n>>>""")
                
    print("""\n\n### Starting DEMO for ECN Model - Herman Smart Grid Project ###\n\n
          mode selected: """ + mode + "\n\n")
    #plt.close("all")
    maxinv, mininv, maxinvgen, mininvgen, maxap, minap, maxapgen, minapgen, maxapp, minapp = minmaxAnalysis(inverters, invlist, aptlist, "hide")
    
    if mode == "system":
        print("###Full system analysis mode###\n")
        minmaxAnalysis(inverters, invlist, aptlist, "show")
        print("###Average Profile###\n")
        sysAnalysisAvg(inverters, invlist, aptlist)
        print("###Pilot Analysis###\n")
        pilotAnalysis(inverters)
    elif mode == "max":
        print("- Top Consumers analysis mode\n")
        Analysis(cn.inverters(maxinv, inverters, invlist), inverters, invlist, aptlist, "all")
        Analysis(cn.apartments(maxap, inverters, aptlist), inverters, invlist, aptlist, "all")
        Analysis(cn.appliances(maxapp, inverters), inverters, invlist, aptlist, "all")
    elif mode == "all":
        print("- All individual analysis mode\n")
        for i in range(len(inverters)):
            Analysis(inverters[i], inverters, invlist, aptlist, "info")
            for j in range(len(inverters[i].apartments)):
                Analysis(inverters[i].apartments[j], inverters, invlist, aptlist, "info")
                for k in range(len(inverters[i].apartments[j].appliances)):
                    Analysis(inverters[i].apartments[j].appliances[k], inverters, invlist, aptlist, "info")
    elif mode[0:3] == "inv":
        print("- Individual inverter analysis mode\n")
        Analysis(cn.inverters(mode[3:], inverters, invlist), inverters, invlist, aptlist, "all")
    elif mode[0:3] == "apt":
        print("- Individual apartment analysis mode\n")
        Analysis(cn.apartments(mode[3:], inverters, aptlist), inverters, invlist, aptlist, "all")
    elif mode[0:3] == "app":
        print("- Individual appliance analysis mode for appliance " + mode[3:] + " \n")
        Analysis(cn.appliances(mode[3:], inverters), inverters, invlist, aptlist, "all")
    elif mode == "selfCS":
        print("\n- Full system analysis for self-consumption and self-sufficiency for each apartment and inverter\n")
        selfCselfS(inverters)
    else:
        print("##The parameter for analysis is not correct.")
    


#%% Data Diagnostics functions - to detect issues with the data


#This function will run the whole data that we gather and notify which points present data inconsistencies
def dataDiagnostics(inverters):
    """This function is run-once to detect the points in the data where there may be some issues. 
    It returns its answer in the code folder with a .txt file"""
    
    #Setting up the file for the diagnostics
    filename = "Diagnostics" + str(md.datetime.today().date()) + ".txt"
    target = open(filename, 'w')
    target.write("#Data Diagnostics for " + str(md.datetime.now()) + "\n\n\n######\n\n\n")
    target.write("#Inverter diagnostics\n\n\n")
    
    #For the inverter generation days - splitting them into days for the whole period
    indexdates, datearray = splitDays(inverters[0].timestamp)
    countinv = 0
    for i in range(len(indexdates)):
        for j in inverters:
            daygen = sum(j.generation[indexdates[i][0]:indexdates[i][1]])
            if daygen < 0.001:                                                  #If the generation is below 1W for that day
                target.write("Inverter " + j.ID + " has no generation on day " + str(datearray[i]) + "\n")
                countinv += 1
    #Checking when a single appliance has higher consumption than the whole apartment
    target.write("\n\n\n######\n\n\n")
    target.write("#Appliance diagnostics\n\n\n")
    countappli = 0
    for i in range(len(inverters)):
        for j in range(len(inverters[i].apartments)):
            for k in range(len(inverters[i].apartments[j].appliances)):
                for m in range(len(inverters[i].apartments[j].appliances[k].consumption)):
                    if inverters[i].apartments[j].appliances[k].consumption[m] > inverters[i].apartments[j].consumption[m]:
                        target.write("Appliance " + inverters[i].apartments[j].appliances[k].ID + " consumes more energy than the full apartment " + inverters[i].apartments[j].ID + " at time " + str(inverters[i].apartments[j].timestamp[m]) + "\n")
                        countappli += 1
    
    target.write("\n\n\n######\n\n\n")
    target.write("There were " + str(countinv) + " inverter issues. This is " + str(100*countinv/(len(inverters) * len(indexdates))) + " percent of the total days of generation \n")
    target.write("There were " + str(countappli) + " appliance issues \n")
    target.close()



#This function will show what appliances are present in each apartment and deterc the heatpumps present in the system

def findHeatPump(inverters):
    """This function wil runn once to detect what appliances are registered to each apartment. It returns a text file in the current folder with the output."""

    #Setting up the file for the diagnostics
    filename = "Appliances" + str(md.datetime.today().date()) + ".txt"
    target = open(filename, 'w')
    target.write("#Appliances List for each apartment -  " + str(md.datetime.now()) + "\n\n\n######\n\n\n")

    hpcount = 0
    apartcount = 0
    for inv in inverters:
        for apart in inv.apartments:
            apartcount += 1
            target.write("\n-Apartment "+apart.ID + "; Appliances:\n")
            appliancelist = ""
            for app in apart.appliances:
                appliancelist += (app.ID + "; ")
            target.write(appliancelist + "\n")
            if "rmtepomp" in appliancelist:
                hpcount += 1
            else:
                target.write("*****There are no heatpumps in this apartment!*****\n")
                

    target.write("\n\n#The total number of heatpumps in this pilot is " + str(hpcount) + " with a number of apartments in " + str(apartcount) + "#")
    target.close()




#%% Functions    
 
##### AUXILIARY FUNCTIONS #####
#A function to obtain all of the system's timestamps that occur in at least one apartment           
def sysAllTimestamps(inv):
    """Function to extract all timestamps that occur at least once for one apartment in the whole system"""
    lista = []
    for i in range(len(inv)):
        for j in range(len(inv[i].apartments)):
            lista = sorted(lista + inv[i].apartments[j].timestamp)
            #With this command, we append all timestamps in the system
    alltimestamps = sorted(list(set(lista))) #and then we remove the duplicates
    return alltimestamps
            
    
#A function to get consumption and generation data for all apartments according to the timestamps        
def setTimestampData(inv, alltimestamps):
    """Function to set the consumption and generation associated with each timestamp, for all the apartments.
    If an apartment has a value for a given timestamp, it will be added in an array representing that timestamp."""
    #creating list of lists for each timestamp
    totalcons = []; totalgen = []; totalID = []
    
    #running through all timestamps:
    for i in range(len(alltimestamps)):
        timestamp = alltimestamps[i]
        cons = []; gen = []; ID = []
        for j in range(len(inv)):
            for k in range(len(inv[j].apartments)):
                #searching all apartments for the timestamp in question      
                index = md.binarySearchII(inv[j].apartments[k].timestamp, timestamp)
                if index > -1:                                                  #If the item was found in the list
                    cons.append(inv[j].apartments[k].consumption[index])
                    gen.append(inv[j].apartments[k].generation[index])
                    ID.append(inv[j].apartments[k].ID)
        #appending the lists for the timestamps in the list of lists            
        totalcons.append(md.np.array(cons))
        totalgen.append(md.np.array(gen))
        totalID.append(ID)
    
    return totalcons, totalgen, totalID
    


#A function to split every day according to its indexes in allTimestamps - Used in dataDiagnostics()
def splitDays(timestamps):
    """Getting all timestamps for the system and splitting them into day arrays with the start and end indexes"""
    alldates = []
    for i in timestamps:
        alldates.append(i.date())
        
    #removing duplicates
    datearray = sorted(list(set(alldates)))
    
    #creating a list of tuples containing a day's start and end indexes
    indexlist = []
    for j in datearray:
        index1 =  alldates.index(j)
        index2 = len(alldates) - list(reversed(alldates)).index(j)
        indexlist.append((index1, index2))
        
    return indexlist, datearray
        
    
    