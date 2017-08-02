# -*- coding: utf-8 -*-
"""
Created on Tue May  2 13:35:31 2017

@author: Sergio

This file will describe the connection schemes for the two pilot projects.
It acts as a map to create the representation of the system in the model.
"""

#%% Aquaradius connection scheme
def aquaradius():
    
    #The list of all inverters in aquaradius project
    aquaradius_inv= ['aqr_0104', 'aqr_0105', 'aqr_0106', 'aqr_0107', 'aqr_0108', 'aqr_0109', 'aqr_0110']
    
    #The associated apartments to each inverter
    aq_0104 = ['35', '91', '97']
    aq_0105 = ['11', '37', '67', '93', '111', '43', '99']
    aq_0106 = ['27', '83', '19', '45']
    aq_0107 = ['29', '59', '85', '21', '77']
    aq_0108 = ['5', '31', '61', '105', '117', '49', '79', '9']
    aq_0109 = ['7', '33', '107', '119', '17', '51']
    aq_0110 = ['39', '69', '53', '81', '55']
    
    #Creating a dictionary to associate apartment and inverter
    connection = {'aqr_0104':aq_0104, 'aqr_0105':aq_0105,'aqr_0106':aq_0106,'aqr_0107':aq_0107,
                  'aqr_0108':aq_0108,'aqr_0109':aq_0109,'aqr_0110':aq_0110}
    
    #And respective channels in each inverter, connected to each apartment respectively:
    aq_0104_chnl = ['_2_', '_4_', '_8_']
    aq_0105_chnl = ['_1_', '_2_', '_3_', '_4_', '_5_', '_6_', '_8_']
    aq_0106_chnl = ['_2_', '_4_', '_6_', '_7_']
    aq_0107_chnl = ['_1_', '_2_', '_3_', '_6_', '_8_']
    aq_0108_chnl = ['_1_', '_2_', '_3_', '_4_', '_5_', '_6_', '_7_', '_8_']
    aq_0109_chnl = ['_1_', '_2_', '_5_', '_6_', '_7_', '_8_']
    aq_0110_chnl = ['_2_', '_3_', '_6_', '_7_', '_8_']
    
    connection_chnl = {'aqr_0104':aq_0104_chnl, 'aqr_0105':aq_0105_chnl,'aqr_0106':aq_0106_chnl,'aqr_0107':aq_0107_chnl,
                  'aqr_0108':aq_0108_chnl,'aqr_0109':aq_0109_chnl,'aqr_0110':aq_0110_chnl}
    
    #Creating dictionary of apartments to call them by their numbers - this is useful just for visualization and will be used in some aspects of the code    
    apartments = {}
    
    for i in range(len(connection)):
        for j in range(len(connection[aquaradius_inv[i]])):
            apartments[connection[aquaradius_inv[i]][j]] = (i, j)
    
    inverters = {}
    
    for i in range(len(aquaradius_inv)):
        inverters[aquaradius_inv[i]] = i
        
       
    return connection, connection_chnl, apartments, inverters


#%% Ons Dorp connection scheme

def onsdorp():
    #The list of all inverters in aquaradius project
    onsdorp_inv= ['onsdorp_0045', 'onsdorp_0046']
    
    #The associated apartments to each inverter
    onsdorp_0045 = ['50B', '50D']
    onsdorp_0046 = ['50F', '50G', '50H', '50K', '50L']

    
    #Creating a dictionary to associate apartment and inverter
    connection = {'onsdorp_0045':onsdorp_0045, 'onsdorp_0046':onsdorp_0046}
    
    #And respective channels in each inverter, connected to each apartment respectively:
    onsdorp_0045_chnl = ['_2_', '_4_']
    onsdorp_0046_chnl = ['_1_', '_2_', '_3_', '_4_', '_5_']

    
    connection_chnl = {'onsdorp_0045':onsdorp_0045_chnl, 'onsdorp_0046':onsdorp_0046_chnl}
    
    #Creating dictionary of apartments to call them by their numbers
    apartments = {}
    
    for i in range(len(connection)):
        for j in range(len(connection[onsdorp_inv[i]])):
            apartments[connection[onsdorp_inv[i]][j]] = (i, j)
    
    inverters = {}
    
    for i in range(len(onsdorp_inv)):
        inverters[onsdorp_inv[i]] = i
        
       
    return connection, connection_chnl, apartments, inverters

#%% Auxiliary functions


#Function to translate an apartment number as a string to the apartment object in our inverters list
def apartments(string, inverters, aptlist):
    """input string, list of inverter objects, dictionary of apartment list"""
    return inverters[aptlist[string][0]].apartments[aptlist[string][1]]

#Function to translate an inverter number as a string to the inverter object in our inverters list
def inverters(string, inverterlist, inv):
    for key in inv:
        pilot = key[0:key.index('_')]
        
    return inverterlist[inv[pilot+'_'+string]]

#Function to translate an appliance ID as a string to the appliance object in our inverters list
def appliances(string, inverterlist):
    for i in range(len(inverterlist)):
        for j in range(len(inverterlist[i].apartments)):
            for k in range(len(inverterlist[i].apartments[j].appliances)):
                if inverterlist[i].apartments[j].appliances[k].ID == string:
                    return inverterlist[i].apartments[j].appliances[k]






