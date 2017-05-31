# -*- coding: utf-8 -*-
"""
Created on Wed May 31 11:03:05 2017

@author: Sergio
File to give in the printing statements for the Analysis function. This is just to make the Analysis function clearer and easier to read.
This file is a bunch of strings and plots - nobody should see this! It is just a "warehouse" (a messy one) for the Analysis functions.
"""
import matplotlib.pyplot as plt


def getPrint_inv(mode, item, systeminfo, itemconsumption, itemgeneration, maxapartmentcons, maxapartmentgen):
    """Printing for the Analysis function for Inverters"""
    
    percentage_cons = itemconsumption/systeminfo[0]
    percentage_gen = itemgeneration/systeminfo[1]
    apartmentcons_percentage = (sum(maxapartmentcons.consumption)/4)/itemconsumption
    apartmentgen_percentage = (sum(maxapartmentgen.generation)/4)/itemgeneration
    
    apartmentlist = ""
    for i in range(len(item.apartments)):
        apartmentlist = apartmentlist + item.apartments[i].ID + "; "
            
    info_inv = "Total consumption of all apartments connected to this inverter is %.2f kWh, or %.2f percent of the total system consumption.\n" %(itemconsumption, percentage_cons*100)
    info_invgen = "Total generation that goes to the apartments in this inverter is %.2f kWh, or %.2f percent of the total system generation.\n" %(itemgeneration, percentage_gen*100)
    info_aptcons = "The apartment that consumes the most is " + maxapartmentcons.ID + " with %.2f percent of the consumption of the inverter.\n" %(apartmentcons_percentage*100)
    info_aptgen = "The apartment that has the most generation sent to is " + maxapartmentgen.ID + " with %.2f percent of the generation of the inverter.\n" %(apartmentgen_percentage*100)
    info_scss = "The potential self-consumption is %.2f  percent and the self-sufficiency is %.2f percent for this inverter.\n" %(item.selfC*100, item.selfS*100)
    info_all = "# Inverter " + item.ID + ": \n" + "Connected to apartments: " + apartmentlist + "\n\n"
    info = info_all + info_inv + info_invgen + info_aptcons + info_aptgen + info_scss
    
    if mode == "all":
        print(info)
        
        plt.figure()
        plt.ylabel('Instantaneous consumption (kWh)')
        plt.xlabel('samples')
        plt.title('Total Consumption of Inverter ' + item.ID + " and apartments")
        itemplt, = plt.plot(item.timestamp, item.consumption, label="Inverter consumption")
        handllist = [itemplt]
        for i in range(len(item.apartments)):
            subitemplt, = plt.plot(item.apartments[i].timestamp, item.apartments[i].consumption, label="Apartment " + item.apartments[i].ID + " consumption")
            handllist.append(subitemplt)
        plt.legend(handles = handllist)
        
        plt.figure()
        plt.ylabel("Instantaneous Generation (kWh)")
        plt.xlabel("Samples")
        plt.title("Total Generation - sum of all apartments connected to Inverter " + item.ID)
        itemplt, = plt.plot(item.timestamp, item.generation, label="Inverter generation")
        handllist = [itemplt]
        for i in range(len(item.apartments)):
            subitemplt, = plt.plot(item.apartments[i].timestamp, item.apartments[i].generation, label="Apartment " + item.apartments[i].ID + " generation")            
            handllist.append(subitemplt)
        plt.legend(handles = handllist)
        
        
        plt.figure()
        plt.title("Self-consumption and self-sufficiency of Inverter " + item.ID)
        plt.xlabel("Samples")
        plt.ylabel("Self-consumption and self-sufficiency as percent")
        plt1, = plt.plot(item.timestamp, item.selfCinst, label="Inverter self consumption")
        plt2, = plt.plot(item.timestamp, item.selfSinst, label="Inverter self sufficiency")
        plt3, = plt.plot(item.timestamp, item.consumption, label="Total consumption of the inverter")
        plt4, = plt.plot(item.timestamp, item.generation, label="Total associated generation of the inverter")
        plt.legend(handles=[plt1, plt2, plt3, plt4])

    elif mode == "info":
        print(info)
        
     
def getPrint_apt(mode, item, systeminfo, itemconsumption, itemgeneration, maxappliancecons):
    """Printing for Analysis function for Apartments"""

    percentage_consSYS = itemconsumption/systeminfo[0]
    percentage_genSYS = itemgeneration/systeminfo[1]
    percentage_consINV = itemconsumption/systeminfo[2]
    percentage_genINV = itemgeneration/systeminfo[3]
        
    
    appliancelist = ""
    for i in range(len(item.appliances)):
        appliancelist = appliancelist + item.appliances[i].ID + "; "
            
    info_apt = "Total consumption of this apartment is %.2f kWh, or %.2f percent of the total system consumption, and %.2f of the total inverter consumption.\n" %(itemconsumption, percentage_consSYS*100, percentage_consINV*100)
    info_aptgen = "Total generation sent to this apartment is %.2f kWh, or %.2f percent of the total system generation, and %.2f of the total inverter generation.\n" %(itemgeneration, percentage_genSYS*100, percentage_genINV*100)
    if maxappliancecons == 0:
        info_appcons = "The apartment has no appliances monitored. \n"
    else:
        info_appcons = "The appliance that consumes the most is " + maxappliancecons.ID + " with %.2f percent of the consumption of the apartment.\n" %(((sum(maxappliancecons.consumption)/4)/itemconsumption)*100)
    info_scss = "The total self-consumption is %.2f and the self-sufficiency is %.2f for this apartment.\n" %(item.selfC*100, item.selfS*100)
    info_all = "# Apartment " + item.ID + ": \n" + "Connected to Inverter: " + item.inv + "\nAnd with appliances: " + appliancelist + "\n\n"
    info = info_all + info_apt + info_aptgen + info_appcons + info_scss
    
    if mode == "all":
        print(info)
        plt.figure()
        plt.ylabel('Instantaneous consumption (kWh)')
        plt.xlabel('samples')
        plt.title('Total Consumption of Apartment ' + item.ID + " and appliances")
        itemplt, = plt.plot(item.timestamp, item.consumption, label="Apartment Consumption")
        handllist = [itemplt]
        for i in range(len(item.appliances)):
            subitemplt, = plt.plot(item.timestamp, item.appliances[i].consumption, label="Appliance " + item.appliances[i].ID + " consumption")
            handllist.append(subitemplt)
        plt.legend(handles=handllist)
        
        plt.figure()
        plt.ylabel("Instantaneous Generation (kWh)")
        plt.xlabel("Samples")
        plt.title("Total Generation associated with Apartment " + item.ID)
        itemplt, = plt.plot(item.timestamp, item.generation, label="Apartment associated generation")
        plt.legend(handles = [itemplt])
        
        plt.figure()
        plt.title("Self-consumption and self-sufficiency of Apartment " + item.ID)
        plt.xlabel("Samples")
        plt.ylabel("Self-consumption and self-sufficiency as percent")
        plt1, = plt.plot(item.timestamp, item.selfCinst, label="Apartment self consumption")
        plt2, = plt.plot(item.timestamp, item.selfSinst, label="Apartment self sufficiency")
        plt3, = plt.plot(item.timestamp, item.consumption, label="Apartment consumption")
        plt4, = plt.plot(item.timestamp, item.generation, label="Apartment associated generation")
        plt.legend(handles=[plt1, plt2, plt3, plt4])
        
    elif mode == "info":
         print(info)
        
    
def getPrint_app(mode, item, systeminfo, itemconsumption, inv, aptlist):
    """Printing for Analysis function for Appliances"""
   
    percentage_consAP = itemconsumption/systeminfo[4]
    percentage_consSYS = itemconsumption/systeminfo[0] 
    
    info_app = "Total consumption of this appliance is %.2f kWh, with %.2f percent of the total apartment consumption and %.2f of the total system consumption.\n" %(itemconsumption, percentage_consAP*100, percentage_consSYS*100)
    info_all = "# Appliance " + item.ID + ": \n" + "Connected to Apartment: " + item.apt + "\n\n"
    info = info_all + info_app

    if mode == "all":
        print(info)
        plt.figure()
        plt.ylabel('Instantaneous consumption (kWh)')
        plt.xlabel('samples')
        plt.title('Total Consumption of Appliance ' + item.ID + ' versus the consumption of Apartment ' + item.apt)
        plt1, = plt.plot(inv[aptlist[item.apt][0]].apartments[aptlist[item.apt][1]].timestamp, inv[aptlist[item.apt][0]].apartments[aptlist[item.apt][1]].consumption, label="Apartment "+ inv[aptlist[item.apt][0]].apartments[aptlist[item.apt][1]].ID + " total consumption")
        plt2, = plt.plot(inv[aptlist[item.apt][0]].apartments[aptlist[item.apt][1]].timestamp, item.consumption, label="Appliance " + item.ID + " consumption")           
        plt.legend(handles=[plt1, plt2])
    elif mode == "info":
        print(info)




def getPrint_minmax(show, inv_cons, inv_gen, maxinv, maxinvgen, mininv, mininvgen, apt_cons, apt_gen, minap, maxap, minapgen, maxapgen, app_cons, maxapp, minapp):
    
        
    initialize = "\n### Full Pilot Analysis ###\n\n This analysis is performed for data for a given period. All values are for the whole period of time.\n\n"
    finalize = "\n### End of Analysis ###\n\n"
    info_invmax = ("There are %d inverters in the system. \nThe inverter that consumes the most is "%(len(inv_cons)) + maxinv + " with %.2f kWh. \nThe inverter that has most generation associated with it is  "%(max(inv_cons))+ maxinvgen + " with %.2f kWh.\n" %(max(inv_gen)))
    info_invmin = ("The inverter that consumes the least is " + mininv + " with %.2f kWh.\nThe inverter that has least generation associated with it is  "%(min(inv_cons))+ mininvgen + " with %.2f kWh.\n" %(min(inv_gen)))

    info_aptmax = ("There are %d apartments in the system. \nThe apartment that consumes the most is "%(len(apt_cons)) + maxap + " with %.2f kWh. \nThe apartment that has most generation associated with it is Apartment "%(max(apt_cons)) + maxapgen + " with %.2f kWh.\n" %(max(apt_gen)))
    info_aptmin = ("The apartment that consumes the least is " + minap + " with %.2f kWh. \nThe apartment that has least generation associated with it is Apartment "%(min(apt_cons)) + minapgen + " with %.2f kWh.\n" %(min(apt_gen)))

    info_appmax = ("There are %d appliances in the system. \nThe appliance with the highest consumption in the pilot is "%(len(app_cons)) + maxapp + " with %.2f kWh.\n" %(max(app_cons)))
    info_appmin = ("The appliance with the lowest consumption in the pilot is " + minapp + " with %.2f kWh.\n" %(min(app_cons)))
    
    
    info = initialize + info_invmax + info_invmin + info_aptmax + info_aptmin + info_appmax + info_appmin + finalize
    
    if show == "show":
        print(info)
    else:
        print("\n")



def getPrint_pilotAnalysis(consumption, generation, selfC, selfS):
    initialize = "\n### Full pilot analysis ###\n\n"
    info_cons = "The total system consumption in the period is %.2f kWh\n" %(sum(consumption)/4)
    info_gen = "The total system generation in the period is %.2f kWh\n" %(sum(generation)/4)
    info_sc = "The system's potential self-consumption is %.2f percent\n" %(selfC*100)
    info_ss = "The system's potential self-sufficiency is %.2f percent\n" %(selfS*100)
    
    info = initialize + info_cons+ info_gen + info_sc + info_ss
    print(info)















