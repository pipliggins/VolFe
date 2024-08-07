# model_dependent_variables.py

import pandas as pd
import numpy as np
import gmpy2 as gp
import math
import densityx as dx

import melt_gas as mg

################
### Contents ###
################

# Solubility constants
# Solid/liquid saturation
# Equilibrium constants
# Fugacity coefficients
# Speciation 

#################################################################################################################################
##################################################### SOLUBILITY CONSTANTS ######################################################
#################################################################################################################################

###################################
### Solubility constant for H2O ###
###################################
def C_H2O(run,PT,melt_wf,setup,species,models):
    
    if models.loc["Hspeciation","option"] == "none": ### C_H2O = (xmH2O)^2/fH2O ### (mole fraction)
        model = models.loc["water","option"]
        if model == "AllisonDataComp": # fitted to experimental data compilation from Allison et al. (2022) for H2O < 6 wt%
            C = 4.6114e-6   
    return C

        
        
##############################################
### Solubility constant for carbon dioxide ###
##############################################
def C_CO3(run,PT,melt_wf,setup,species,models): ### C_CO2,T = xmCO2,T/fCO2 ### (mole fraction) ***except Shishkina14 - wmCO2 ppm***
    model = models.loc["carbon dioxide","option"]

    P = PT['P']
    T_K = PT['T']+273.15     
    # Calculate cation proportions with no volatiles but correct Fe speciation if available (a la Dixon 1997)
    tot, Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P_, H, C = mg.melt_cation_proportion(run,melt_wf,setup,species,"no","no")

    R = 83.15
    T0 = 1473.15 # K
    PI = -6.5*(Si+Al) + 20.17*(Ca+0.8*K+0.7*Na+0.4*Mg+0.4*FeT) # Dixon (1997) Am. Min. 82:368-378
    PI_ = (Ca+0.8*K+0.7*Na+0.4*Mg+0.4*FeT)/(Si+Al) # Shishkina et al. (2014) Chem. Geol. 388:112-129
    DH = -13.1 # kJ/mol # Lesne et al. (2011) CMP 162:153-168 from basanite of Holloway & Blank (1994)
 
    if model == "Dixon95": # Dixon et al. (1995)
        DV = 23. # cm3/mol
        P0 = 1.0 # bar
        A = 3.8e-7
        B = (-DV*(P-P0))/(R*T0)
        C = A*gp.exp(B)
    elif model == "Dixon97": # Compositional dependence from Dixon (1997) Am. Min. 82:368-378 as shown by Witham et al. (2012) [assumes PI-SiO2 relationship in caption of figre 2 is 10.19 instead of 10.9 - if 10.9 is assumed you get negative C_CO3]
        DV = 23 # cm3/mol
        P0 = 1.0 # bar
        A = (7.94e-7)*(PI+0.762)
        B = (-DV*(P-P0))/(R*T0)
        C = A*gp.exp(B)
    elif model == "Lesne11": # Lesne et al. (2011)
        DV = 23 # cm3/mol
        P0 = 1.0 # bar
        A = 7.94e-7*((((871*PI)+93.0)/1000.0)+0.762)
        B = (-DV*(P-P0))/(R*T0)
        C = A*gp.exp(B)
    elif model == "VES-9": # Lesne et al. (2011) CMP 162:153-168
        DV = 31.0 # cm3/mol
        P0 = 1000.0 # bar
        A = gp.exp(-14.10)
        B = -((DV/(R*T_K))*(P-P0)) + (DH/R)*((1.0/T0) - (1.0/T_K))
        C = A*gp.exp(B)
    elif model == "ETN-1": # Lesne et al. (2011) CMP 162:153-168
        DV = 23.0 # cm3/mol
        P0 = 1000.0 # bar
        A = gp.exp(-14.55)
        B = -((DV/(R*T_K))*(P-P0)) + (DH/R)*((1.0/T0) - (1.0/T_K))    
        C = A*gp.exp(B)
    elif model == "PST-9": # Lesne et al. (2011) CMP 162:153-168
        DV = 6.0 # cm3/mol
        P0 = 1000.0 # bar
        A = gp.exp(-14.74)
        B = -((DV/(R*T_K))*(P-P0)) + (DH/R)*((1.0/T0) - (1.0/T_K))
        C = A*gp.exp(B)
    elif model == "Sunset Crater": # Sunset Crater from Allison et al. (2022) CMP 177:40
        R_ = 83.144621 # cm3 bar K−1 mol−1
        DV = 16.40 # cm3/mol
        P0 = 1000.0 # bar
        A = gp.exp(-14.67)
        B = -((DV/(R_*T_K))*(P-P0))
        C = A*gp.exp(B)
    elif model == "SFVF": # SFVF from Allison et al. (2022) CMP 177:40
        R_ = 83.144621 # cm3 bar K−1 mol−1
        DV = 15.02 # cm3/mol
        P0 = 1000.0 # bar
        A = gp.exp(-14.87)
        B = -((DV/(R_*T_K))*(P-P0))
        C = A*gp.exp(B)
    elif model == "Erebus": # Erebus from Allison et al. (2022) CMP 177:40
        R_ = 83.144621 # cm3 bar K−1 mol−1
        DV = -14.65 # cm3/mol
        P0 = 1000.0 # bar
        A = gp.exp(-14.65)
        B = -((DV/(R_*T_K))*(P-P0))
        C = A*gp.exp(B)
    elif model == "Vesuvius": # Vesuvius from Allison et al. (2022) CMP 177:40
        R_ = 83.144621 # cm3 bar K−1 mol−1
        DV = 24.42 # cm3/mol
        P0 = 1000.0 # bar
        A = gp.exp(-14.04)
        B = -((DV/(R_*T_K))*(P-P0))
        C = A*gp.exp(B)
    elif model == "Etna": # Etna from Allison et al. (2022) CMP 177:40
        R_ = 83.144621 # cm3 bar K−1 mol−1
        DV = 21.59 # cm3/mol
        P0 = 1000.0 # bar
        A = gp.exp(-14.28)
        B = -((DV/(R_*T_K))*(P-P0))
        C = A*gp.exp(B)
    elif model == "Stromboli": # Stromboli from Allison et al. (2022) CMP 177:40
        R_ = 83.144621 # cm3 bar K−1 mol−1
        DV = 14.93 # cm3/mol
        P0 = 1000.0 # bar
        A = gp.exp(-14.68)
        B = -((DV/(R_*T_K))*(P-P0))
        C = A*gp.exp(B)
    elif model == "Basanite": # Basanite composition from Holloway and Blank (1994), data from Allison et al. (2022) CMP 177:40
        R_ = 83.144621 # cm3 bar K−1 mol−1
        DV = 21.72 # cm3/mol
        P0 = 1000.0 # bar
        A = gp.exp(-14.32)
        B = -((DV/(R_*T_K))*(P-P0))
        C = A*gp.exp(B)
    elif model == "Leucite": # Leucite composition from Thibault and Holloway (1994), data from Allison et al. (2022) CMP 177:40
        R_ = 83.144621 # cm3 bar K−1 mol−1
        DV = 21.53 # cm3/mol
        P0 = 1000.0 # bar
        A = gp.exp(-13.36)
        B = -((DV/(R_*T_K))*(P-P0))
        C = A*gp.exp(B)
    elif model == "AH3 phonotephrite": # AH3 Phonotephrite composition from Vetere et al. (2014), data from Allison et al. (2022) CMP 177:40
        R_ = 83.144621 # cm3 bar K−1 mol−1
        DV = 30.45 # cm3/mol
        P0 = 1000.0 # bar
        A = gp.exp(-13.26)
        B = -((DV/(R_*T_K))*(P-P0))
        C = A*gp.exp(B)
    elif model == "N72 Basalt": # N72 basalt composition from Shishkina et al. (2010), data from Allison et al. (2022) CMP 177:40
        R_ = 83.144621 # cm3 bar K−1 mol−1
        DV = 19.05 # cm3/mol
        P0 = 1000.0 # bar
        A = gp.exp(-14.86)
        B = -((DV/(R_*T_K))*(P-P0))
        C = A*gp.exp(B)
    elif model == "Blank93": # Blank et al. (1993) - rhyolite - tried for workshop
        DV = 28 # cm3/mol
        P0 = 1.0 # bar
        A = gp.exp(-14.45)
        B = (-DV*(P-P0))/(R*(850.+273.15))
        C = A*gp.exp(B)
    return C


########################################
### solubility constant for sulphide ###
########################################
def C_S(run,PT,melt_wf,setup,species,models): ### C_S = wmS2-*(fO2/fS2)^0.5 ### (weight ppm)
    
    model = models.loc["sulphide","option"]
    
    T = PT['T'] + 273.15 # T in K
    
    def ONeill21(T,Na,K,Mg,Ca,Fe,Mn,Ti,Al,Si):
        lnC = (8.77 - (23590.0/T) + (1673.0/T)*(6.7*(Na+K) + 4.9*Mg + 8.1*Ca + 8.9*(Fe+Mn) + 5.0*Ti + 1.8*Al - 22.2*Ti*(Fe+Mn) + 7.2*Fe*Si) - 2.06*math.erf(-7.2*(Fe+Mn)))
        return lnC
    
    if model == "ONeill21":
        # Mole fractions in the melt on cationic lattice (all Fe as FeO) no volatiles
        tot, Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P, H, C = mg.melt_cation_proportion(run,melt_wf,setup,species,"no","no")
        lnC = ONeill21(T,Na,K,Mg,Ca,FeT,Mn,Ti,Al,Si)
     
    if model == "ONeill21dil":
        # Mole fractions in the melt on cationic lattice (all Fe as FeO) no volatiles
        tot, Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P, H, C = mg.melt_cation_proportion(run,melt_wf,setup,species,"water","no")        
        lnC = ONeill21(T,Na,K,Mg,Ca,FeT,Mn,Ti,Al,Si)

    if model == "ONeill21hyd":
        # Mole fractions in the melt on cationic lattice (all Fe as FeO) no volatiles
        tot, Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P, H, C = mg.melt_cation_proportion(run,melt_wf,setup,species,"no","no")
        lnC_nondil = ONeill21(T,Na,K,Mg,Ca,FeT,Mn,Ti,Al,Si)
        tot, Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P, H, C = mg.melt_cation_proportion(run,melt_wf,setup,species,"water","no")
        lnCdil = ONeill21(T,Na,K,Mg,Ca,FeT,Mn,Ti,Al,Si)
        lnCH = (H*(6.4 + 12.4*H - 20.3*Si + 73.0*(Na+K)))
        lnC = lnCdil+lnCH


    C = math.exp(lnC) 
    return C



########################################
### solubility constant for sulphate ###
########################################
def C_SO4(run,PT,melt_wf,setup,species,models): ### C_SO4 = wmS6+*(fS2*fO2^3)^-0.5 ### (weight ppm)
    model = models.loc["sulphate","option"]
    T = PT['T'] + 273.15 # T in Kelvin
    P = PT['P'] # P in bars
    slope = 115619.707 # slope for T-dependence for melt inclusion fits
            
    def ONeill22(Na,Mg,Al,K,Ca,Mn,Fe2,T):
        lnC = -8.02 + ((21100. + 44000.*Na + 18700.*Mg + 4300.*Al + 44200.*K + 35600.*Ca + 12600.*Mn + 16500.*Fe2)/T) #CS6+ = [S6+, ppm]/fSO3
        Csulphate = gp.exp(lnC)*KOSg2(PT,models) # ppm S
        return Csulphate
    
    if model == "Nash19": # Nash et al. (2019) EPSL 507:187-198
        S = 1. # S6+/S2- ratio of S6+/S2- of 0.5
        Csulphide = C_S(run,PT,melt_wf,setup,species,models)
        A = PT_KCterm(run,PT,setup,species,models) # P, T, compositional term from Kress & Carmicheal (1991)
        B = (8743600/T**2) - (27703/T) + 20.273 # temperature dependence from Nash et al. (2019)
        a = 0.196 # alnfO2 from Kress & Carmicheal (1991)
        F = 10**(((math.log10(S))-B)/8.)
        fO2 = math.exp(((math.log(0.5*F))-A)/a)
        Csulphate = (S*Csulphide)/(fO2**2)
    elif model == "Boulliung22nP": # Boullioung & Wood (2022) GCA 336:150-164 [eq5] - corrected!
        # Mole fractions in the melt on cationic lattice (all Fe as FeO) no volatiles
        tot,Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P, H, C = mg.melt_cation_proportion(run,melt_wf,setup,species,"no","no")
        logCS6 = -12.948 + ((15602.*Ca + 28649.*Na - 9596.*Mg + 4194.*Al +16016.*Mn + 29244.)/T) # wt% S
        Csulphate = (10.**logCS6)*10000. # ppm S
    elif model == "Boulliung22wP": # Boullioung & Wood (2022) GCA 336:150-164 [eq5] - corrected!
        # Mole fractions in the melt on cationic lattice (all Fe as FeO) no volatiles
        tot,Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P_, H, C = mg.melt_cation_proportion(run,melt_wf,setup,species,"no","no")
        logCS6 = -12.659 + ((3692.*Ca - 7592.*Si - 13736.*Ti + 3762.*Al + 34483)/T) - (0.1*P*1.5237)/T # wt% S
        Csulphate = (10.**logCS6)*10000. # ppm S
    elif model == "ONeill22": # O'Neill & Mavrogenes (2022) GCA 334:368-382 eq[12a]
        # Mole fractions in the melt on cationic lattice (Fe as Fe2 and Fe3) no volatiles
        tot,Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P, H, C = mg.melt_cation_proportion(run,melt_wf,setup,species,"no","yes")   
        Csulphate = ONeill22(Na,Mg,Al,K,Ca,Mn,Fe2,T)
    elif model == "ONeill22dil": # O'Neill & Mavrogenes (2022) GCA 334:368-382 eq[12a]
        # Mole fractions in the melt on cationic lattice (Fe as Fe2 and Fe3) includes water
        tot,Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P, H, C = mg.melt_cation_proportion(run,melt_wf,setup,species,"water","yes")   
        Csulphate = ONeill22(Na,Mg,Al,K,Ca,Mn,Fe2,T)
    return Csulphate



###################################
### solubility constant for H2S ###
###################################
def C_H2S(run,PT,melt_wf,setup,species,models): # C_H2S = wmH2S/fH2S (ppm H2S, fH2S bar)
    model = models.loc["hydrogen sulfide","option"]
    if model == "basalt":
        K = 10.23 # fitted to basalt data from Moune+ 2009 CMP 157:691–707 and Lesne+ 2015 ChemGeol 418:104–116
    elif model == "basaltic andesite":
        K = 6.82 # fitted to basaltic andesite data from Moune+ 2009 CMP 157:691–707 and Lesne+ 2015 ChemGeol 418:104–116 
    return K



########################################
### solubility constant for hydrogen ###
########################################
def C_H2(run,PT,melt_wf,setup,species,models): # C_H2 = wmH2/fH2 (wtppm)
    # Hirchmann et al. (2012) EPSL 345-348:38-48
    model = models.loc["hydrogen","option"] 
    R = 83.144598 # bar cm3 /mol /K
    P = PT['P'] # pressure in bars
    T = PT['T'] + 273.15 # T in Kelvin SHOULD BE T0
    P0 = 100.*0.01 # kPa to bars
    if model == "basalt":
        #lnK0 = -11.4 # T0 = 1400 'C, P0 = 100 kPa for mole fraction H2
        lnK0 = -0.9624 # for ppm H2 (fitted in excel)
        DV = 10.6 # cm3/mol
    elif model == "andesite":
        #lnK0 = -10.6 # T0 = 1400 'C, P0 = 100 kPa for mole fraction H2
        lnK0 = -0.1296 # for ppm H2 (fitted in excel)
        DV = 11.3 # cm3/mol
    lnK = lnK0 - (DV*(P-P0))/(R*T) # = ln(XH2/fH2) in ppm/bar
    C = gp.exp(lnK) 
    return C



######################################
### solubility constant for methane ##
######################################
def C_CH4(run,PT,melt_wf,setup,species,models): # C_CH4 = wmCH4/fCH4 (ppm)
    model = models.loc["methane","option"]
    if model == "Ardia13": # Ardia et al. (2013) GCA 114:52-71
        R = 83.144598 # bar cm3 /mol /K 
        P = PT['P'] # pressure in bars
        T = PT['T'] + 273.15 # T in Kelvin SHOULD BE T0
        P0 = 100.*0.01 # kPa to bars
        lnK0 = 4.93 # ppm CH4 
        #lnK0 = -7.63 # mole fraction CH4
        DV = 26.85 # cm3/mol
        lnK = lnK0 - (DV*(P-P0))/(R*T) 
        K_ = gp.exp(lnK) # for fCH4 in GPa
        K = 0.0001*K_ # for fCH4 in bars 
    return K



#################################
### solubility constant for CO ##
#################################
def C_CO(run,PT,melt_wf,setup,species,models): # C_CO = wmCO/fCO (ppm)
    model = models.loc["carbon monoxide","option"]
    if model == "basalt": # from fitting Armstrong et al. (2015) GCA 171:283-302; Stanley+2014, and Wetzel+13 thermodynamically
        R = 83.144598 # bar cm3 /mol /K 
        P = PT['P'] # pressure in bars
        T = PT['T'] +273.15 # T in Kelvin
        P0 = 1. # in bars
        lnK0 = -2.11 # ppm CO
        DV = 15.20 # cm3/mol
        lnK = lnK0 - (DV*(P-P0))/(R*T) 
        K = gp.exp(lnK) # CO(ppm)/fCO(bars)
    return K


#################################
### solubility constant for X ###
#################################
def C_X(run,PT,melt_wf,setup,species,models): # C_X = wmX/fX (ppm)
    species = models.loc["species X","option"]
    model = models.loc["species X solubility","option"]
    if species == "Ar":
        if model == "Iacono-Marziano10_Ar_basalt": # Iacono-Marziano et al. (2010) Chemical Geology 279(3–4):145-157
            K = 0.0799 # fitted assuming Ar is an ideal gas... i.e. yAr = 1.
        elif model == "Iacono-Marziano10_Ar_rhyolite": # Iacono-Marziano et al. (2010) Chemical Geology 279(3–4):145-157
            K = 0.4400 # fitted assuming Ar is an ideal gas... i.e. yAr = 1.
    if species == "Ne":
        if model == "Iacono-Marziano10_Ne_basalt": # Iacono-Marziano et al. (2010) Chemical Geology 279(3–4):145-157
            K = 0.1504 # fitted assuming Ne is an ideal gas... i.e. yNe = 1.
        elif model == "Iacono-Marziano10_Ne_rhyolite": # Iacono-Marziano et al. (2010) Chemical Geology 279(3–4):145-157
            K = 0.8464 # fitted assuming Ne is an ideal gas... i.e. yNe = 1.
    return K


#################################################################################################################################
################################################ solid/liquid volatile saturation ###############################################
#################################################################################################################################

################################################
### sulphate content at anhydrite saturation ###
################################################
def SCAS(run,PT,melt_wf,setup,species,models): 
    model = models.loc["SCAS","option"]
    T = PT['T'] +273.15
    
    # mole fraction melt composition including water but all Fe as FeOT
    tot,Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P, H, CO2, S, X = mg.melt_mole_fraction(run,melt_wf,setup,species,models,"water","no")
    tot = 100.*tot
    
    if model == "Chowdhury18": # sulphate content (ppm) at anhydrite saturation from Chowdhury & Dasgupta (2018) [T in K]
        a = -13.23
        b = -0.50
        dSi = 3.02
        dCa = 36.70
        dMg = 2.84
        dFe = 10.14
        dAl = 44.28
        dNa = 26.27
        dK = -25.77
        e = 0.09
        f = 0.54
        wm_H2OT = 100.*melt_wf['H2OT']
        dX = dSi*Si + dCa*Ca + dMg*Mg + dFe*FeT + dAl*Al + dNa*Na + dK*K
        lnxm_SO4 = a + b*((10.0**4.0)/T) + dX + e*wm_H2OT - f*gp.log(Ca)                                                                                  
        xm_SO4 = gp.exp(lnxm_SO4) 
        Xm_SO4 = xm_SO4*(xm_SO4 + tot)
        S6CAS = Xm_SO4*species.loc["S","M"]*10000.0
                           
    elif model == "Zajacz19":
        if Na + K + Ca >= Al:
            P_Rhyo = 3.11*(Na+K+Ca-Al)
        else:
            P_Rhyo = 1.54*(Al-(Na+K+Ca))
        NBOT = (2.*Na+2.*K+2.*(Ca+Mg+FeT)-Al*2.)/(Si+2.*Al) # according to spreadsheet not paper
        P_T = gp.exp(-7890./T)
        P_H2O = H*(2.09 - 1.65*NBOT) + 0.42*NBOT + 0.23
        P_C = ((P_Rhyo + 251.*Ca**2. + 57.*Mg**2. + 154.*FeT**2.)/(2.*Al + Si))/(1. + 4.8*NBOT)
        Ksm_SPAnh = gp.exp(1.226*gp.log(P_C*P_T*P_H2O) + 0.079)                         
        Xsm_S = Ksm_SPAnh/Ca  
        S6CAS = Xsm_S*tot*32.07*10000.
        
    elif model == "Liu23": # Liu et al. (2023) GCA 349:135-145 eq. 4
        tot,Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P, H, CO2, S, X = mg.melt_mole_fraction(run,melt_wf,setup,species,models,"no","no")
        NBOT = (2.*Na+2.*K+2.*(Ca+Mg+FeT)-Al*2.)/(Si+2.*Al) 
        tot,Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P, H, CO2, S, X = mg.melt_mole_fraction(run,melt_wf,setup,species,models,"water","no")
        lnSCAS = 12.185 - (8541./T) + (1.409*NBOT) + 9.984*Ca + melt_wf["H2OT"]*100.
        S6CAS = gp.exp(lnSCAS)

    return S6CAS

###############################################
### sulphide content at sulphide saturation ###
###############################################
def SCSS(run,PT,melt_wf,setup,species,models): # sulphide content (ppm) at sulphide saturation from O'Neill (2020) [P in bar,T in K]
    model = models.loc["SCSS","option"]
    P_bar = PT['P']
    T = PT['T'] + 273.15
    Fe3FeT = melt_wf["Fe3FeT"]
    
    def ONeill21_SCSS(P_bar,T,Si,Ti,Al,FeT,Fe2,Fe3,Mg,Ca,Na,K,P,H,C,run,PT,melt_wf,setup,species,models):
        R = 8.31441
        P = (1.0e-4)*P_bar # pressure in GPa
        D = (137778.0 - 91.66*T + 8.474*T*gp.log(T)) # J/mol
        sulphide_comp = 1.0 # assumes the sulphide is pure FeS (no Ni, Cu, etc.)
        lnaFeS = gp.log((1.0 - Fe2)*sulphide_comp)
        lnyFe2 = (((1.0-Fe2)**2.0)*(28870.0 - 14710.0*Mg + 1960.0*Ca + 43300.0*Na + 95380.0*K - 76880.0*Ti) + (1.0-Fe2)*(-62190.0*Si + 31520.0*Si**2.0))/(R*T)
        lnS = D/(R*T) + gp.log(C_S(run,PT,melt_wf,setup,species,models)) - gp.log(Fe2) - lnyFe2 + lnaFeS + (-291.0*P + 351.0*gp.erf(P))/T
        return lnS
    
    if model == "ONeill21":
        # Mole fractions in the melt on cationic lattice (Fe2 and Fe3) no volatiles
        tot,Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P, H, C = mg.melt_cation_proportion(run,melt_wf,setup,species,"no","yes")
        lnS = ONeill21_SCSS(P_bar,T,Si,Ti,Al,FeT,Fe2,Fe3,Mg,Ca,Na,K,P,H,C,run,PT,melt_wf,setup,species,models)
        
    elif model == "ONeill21dil":
        # Mole fractions in the melt on cationic lattice (Fe2 and Fe3) and water
        tot,Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P, H, C = mg.melt_cation_proportion(run,melt_wf,setup,species,"water","yes")
        lnS = ONeill21_SCSS(P_bar,T,Si,Ti,Al,FeT,Fe2,Fe3,Mg,Ca,Na,K,P,H,C,run,PT,melt_wf,setup,species,models)
        
    elif model == "ONeill21hyd":
        # Mole fractions in the melt on cationic lattice (Fe2 and Fe3) and water
        tot,Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P, H, C = mg.melt_cation_proportion(run,melt_wf,setup,species,"water","yes")
        lnS = ONeill21_SCSS(P_bar,T,Si,Ti,Al,FeT,Fe2,Fe3,Mg,Ca,Na,K,P,H,C,run,PT,melt_wf,setup,species,models)
    
    elif model == "Liu07":
        # Mole fractions in the melt on cationic lattice (Fe2 and Fe3) and water
        tot,Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P, H, C = mg.melt_cation_proportion(run,melt_wf,setup,species,"water","yes")
        MFM = (Na+K+2.*(Ca+Mg+Fe2))/(Si*(Al+Fe3))
        lnS = 11.35251 - (4454.6/T) - 0.03190*(PT["P"]/T) + 0.71006*gp.log(MFM) - 1.98063*(MFM*H) + 0.21867*gp.log(H) + 0.36192*gp.log(Fe2)
        
    elif model == "Fortin15":
        # Mole fractions in the melt on cationic lattice (all Fe as FeOT) and water
        tot,Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P, H, C = mg.melt_cation_proportion(run,melt_wf,setup,species,"water","no")
        lnS = 34.784 - (5772.3/T) - 346.54*((0.0001*PT["P"])/T) - 20.393*H - 25.499*Si - 18.344*Ti - 27.381*Al - 17.275*Fe - 22.398*Mg - 20.378*Ca - 18.954*Na - 32.195*K
    
    elif model == "Liu21":
        XFeS = 1.
        H2O = melt_wf["H2OT"]*100.
        SCSS = (XFeS*gp.exp(13.88 - (9744./T) - (328.*(0.0001*PT["P"])/T))) + 104.*H2O
        lnS = gp.log(SCSS)
    return gp.exp(lnS)

#################################################################################################################################
#################################### EQUILIBRIUM CONSTANTS FOR HOMOGENEOUS VAPOR EQUILIBRIA #####################################
#################################################################################################################################

# H2 + 0.5O2 = H2O
# K = fH2O/(fH2*(fO2)^0.5)
def KHOg(PT,models):
    T_K = PT['T']+273.15
    if models.loc["KHOg","option"] == "KO97":
        K = 10.**((12510.0/T_K)-0.979*(gp.log10(T_K))+0.483)
    return K

# H2O + 0.5S2 = H2S + 0.5O2
# K = (fH2S*(fO2)^0.5)/((fS2^0.5)*fH2O)
def KHOSg(PT,models):
    T_K = PT['T']+273.15
    if models.loc["KHOSg","option"] == "KO97": # Kerrick & Ohmoto (1997)
        K = 10.**((-8117.0/T_K)+0.188*gp.log10(T_K)-0.352)
    elif models.loc["KHOSg","option"] == "noH2S": # H2S doesn't form in the gas...
        K = 0.
    return K

# 0.5S2 + O2 = SO2
# K = fSO2/((fS2^0.5)*fO2)
def KOSg(PT,models):
    T_K = PT['T']+273.15
    if models.loc["KOSg","option"] == "KO97": # Kerrick & Ohmoto (1997)
        K = 10.**((18929.0/T_K)-3.783)
    return K

# 0.5S2 + 1.5O2 = SO3
# K = fSO3/((fS2^0.5)*(fO2^1.5)
def KOSg2(PT,models):
    T_K = PT['T']+273.15
    if models.loc["KOSg2","option"] == "OM22": # O'Neill+Mavrogenes2022 from JANF 
        lnK = (55921./T_K) - 25.07 + 0.6465*gp.log(T_K)
        K = gp.exp(lnK) 
    return K

# CO + 0.5O = CO2
# K = fCO2/(fCO*(fO2^0.5))
def KCOg(PT,models):
    T_K = PT['T']+273.15
    if models.loc["KCOg","option"] == "KO97": # Kerrick & Ohmoto (1997)
        K = 10.**((14751.0/T_K)-4.535)
    return K

# CH4 + 2O2 = CO2 + 2H2O
# K = (fCO2*(fH2O^2))/(fCH4*(fO2^2))
def KCOHg(PT,models): 
    T_K = PT['T']+273.15
    if models.loc["KCOHg","option"] == "KO97": # Kerrick & Ohmoto (1997)
        K = 10.**((41997.0/T_K)+0.719*gp.log10(T_K)-2.404)
    return K

def KOCSg(PT,models): # OCS - depends on system
    T = PT['T']+273.15
    if models.loc["carbonylsulphide","option"] == "COHS":
    # OCS + H2O = CO2 + H2S
    # K = (fCO2*fH2S)/(fOCS*fH2O)
        if models.loc["KOCSg","option"] == "EVo": 
            K = gp.exp(0.482 + (16.166e-2/T) + 0.081e-3*T - (5.715e-3/T**2) - 2.224e-1*gp.log(T))
            return K
    if models.loc["carbonylsulphide","option"] == "COS":
    # 2CO2 + OCS = 3CO + SO2 - 
    # K = (fCO^3*fSO2)/(fCO2^2*fOCS)    
        if models.loc["KOCSg","option"] == "Moussallam19": # Moussallam et al. (2019) EPSL 520:260-267
            K = 10.**(9.24403 - (15386.45/T)) # P and f in bars, T in K 
        return K

# Cgraphite + O2 = CO2
def KCOs(PT,models): 
    T_K = PT['T']+273.15
    P = PT['P']
    if models.loc["KCOs","option"] == "Holloway92": # Holloway et al. (1992) Eur J. Mineral. 4:105-114 equation (3) KI
        a = 40.07639
        b = -2.5392e-2
        c = 5.27096e-6
        d = 0.0267
        log10K = a + (b*T_K) + (c*T_K**2) + ((P-1)/T_K)
        K = 10.**log10K     
    return K
    
#################################################################################################################################
##################################### EQUILIBRIUM CONSTANTS FOR HOMOGENEOUS MELT EQUILIBRIA #####################################
#################################################################################################################################
       
# H2Omol + O = 2OH
# K = xOH*2/(xH2Omol*xO)
def KHOm(run,PT,melt_wf,setup,species,models):
    Hspeccomp = models.loc["Hspeccomp","option"]
    T_K = PT['T']+273.15
    
    if Hspeccomp == "rhyolite": # Zhang (1999) Reviews in Geophysics 37(4):493-516
        a = -3120.0
        b = 1.89
        K = gp.exp((a/T_K) + b)
    elif Hspeccomp == "alkali basalt": # average of eqn-15-17 from Lesne et al. (2010) CMP 162:133-151
        a = -8348.0 # VES-9 = -8033.0, ETN-1 = -8300.0, and PST-9 = -8710.0
        b = 7.8108 # VES-9 = 7.4222, ETN-1 = 7.4859, and PEST-9 = 8.5244
        K = gp.exp((a/T_K) + b)
    elif Hspeccomp == "PST-9": # Lesne et al. (2010) CMP 162:133-151 eqn 15
        a = -8710.0
        b = 8.5244
        K = gp.exp((a/T_K) + b)
    elif Hspeccomp == "VES-9": # Lesne et al. (2010) CMP 162:133-151 eqn 16
        a = -8033.0
        b = 7.4222
        K = gp.exp((a/T_K) + b)
    elif Hspeccomp == "ETN-1": # Lesne et al. (2010) CMP 162:133-151 eqn 17
        a = -8300.0
        b = 7.4859
        K = gp.exp((a/T_K) + b)
    elif Hspeccomp == "andesite": # eqn-7 from Botcharnikov et al. (2006) Chem. Geol. 229(1-3)125-143
        a = -3650.0
        b = 2.99
        K = gp.exp((a/T_K) + b)
    elif Hspeccomp == "MORB": # fit to Dixon et al. (1995) data digitised from Lesne et al. (2010) CMP 162:133-151
        a = -2204.99
        b = 1.2600
        K = gp.exp((a/T_K) + b)
    elif Hspeccomp == "albite": # Silver & Stolper (1989) J.Pet 30(3)667-709
        K = 0.17
    return K

def KregH2O(run,PT,melt_wf,setup,species,models):
    if Hspeccomp == "MORB": # Dixon et al. (1995)
        A = 0.403
        B = 15.333
        C = 10.894
    elif Hspeccomp == "alkali basalt XT": # No T-dependence, hence its the speciation frozen in the glass. Eqn 7-10 from Lesne et al. (2010) CMP 162:133-151 (eqn 7 is wrong)
        # wt% normalised including H2O, all Fe as FeOT
        tot,SiO2, TiO2, Al2O3, FeOT, FeO, Fe2O3, MgO, CaO, Na2O, K2O, P2O5, H2O, CO2, S, X = melt_normalise_wf(run,melt_wf,setup,species,"volatiles","Fe speciation")
        Na = Na2O*100.
        K = K2O*100.
        A = 0.5761*(Na+K) - 0.2884 # eqn-8
        B = -8.9589*(Na+K) + 24.65 # eqn-9
        C = 1.7013*(Na+K) + 9.6481 # eqn-1
    elif Hspeccomp == "alkali basalt": # Includes T-dependence, hence speciation in the melt. Eqn 24-27 from Lesne et al. (2010) CMP 162:133-151
        lnK = ((-2704.4/T_K) + 0.641)
        A = lnK + 49016.0/(R*T_K)
        B = -2153326.51/(R*T_K)
        C = 1.965495217/(R*T_K)
    elif Hspeccomp == "VES-9": # Lesne et al. (2011) 162:133-151 Table 5
        A = 3.139
        B = -29.555
        C = 20.535
    elif Hspeccomp == "ETN-1": # Lesne et al. (2011) 162:133-151 Table 5
        A = 4.128
        B = -45.905
        C = 21.311
    elif Hspeccomp == "PST-9": # Lesne et al. (2011) 162:133-151 Table 5
        A = 2.6
        B = -22.476
        C = 22.295
    elif Hspeccomp == "albite": # Silver & Stolper (1989) J.Pet 30(3)667-709
        A = 0.403
        B = 15.333
        C = 10.894
    
# CO2 + O = CO3
def KCOm(run,PT,melt_wf,setup,species,models): # K = 
    T_K = PT['T']+273.15
    Cspeccomp = models.loc["Cspeccomp","option"]
    if Cspeccomp == "andesite": # eqn-8 from Botcharnikov et al. (2006) Chem. Geol. 229(1-3)125-143
        a = 8665.0
        b = -5.11
        value = gp.exp((a/T_K) + b)  
    elif Cspeccomp == "dacite": # from Botcharnikov et al. (2006) Chem. Geol. 229(1-3)125-143
        a = 9787.0
        b = -7.69
        value = gp.exp((a/T_K) + b)
    elif Cspeccomp == "basalt": # all oxidised carbon is CO32-
        value = "infinite"
    elif Cspeccomp == "rhyolite": # all oxidised carbon is CO2,mol
        value = 0.
    return value

################################################################################################################################# 
##################################################### FUGACITY COEFFICIENTS #####################################################
#################################################################################################################################

# all fugacity coefficients are assumed to equal 1 below 1 bar.

##########################################
### CORK using Holland & Powell (1991) ###
##########################################

def CORK(PT,p0,a,b,c,d):
    P = PT['P']
    T_K = PT['T']+273.15
    def MRK(P_kb,VMRK,R,T_K,a,b): # MRK volume equation rearranged to equal 0
        return P_kb*pow(VMRK,3.0) - R*T_K*pow(VMRK,2.0) - (b*R*T_K + pow(b,2.0)*P_kb - a*pow(T_K,-0.5))*VMRK - (a*b)*pow(T_K,-0.5)

    def dMRK(P_kb,VMRK,R,T_K,a,b): # derivative of above
        return 3.0*P_kb*pow(VMRK,2.0) - 2.0*R*T_K*VMRK - (b*R*T_K + pow(b,2.0)*P_kb - a*pow(T_K,-0.5))

    def dVMRK(MRK,P_kb,VMRK,R,T_K,a,b):
        return abs(0-MRK(P_kb,VMRK,R,T_K,a,b))

    def NR_VMRK(MRK, dMRK, VMRK0, e1, P_kb,R,T_K,a,b):
        delta1 = dVMRK(MRK,P_kb,VMRK0,R,T_K,a,b)
        while delta1 > e1:
            VMRK0 = VMRK0 - MRK(P_kb,VMRK0,R,T_K,a,b)/dMRK(P_kb,VMRK0,R,T_K,a,b)
            delta1 = dVMRK(MRK,P_kb,VMRK0,R,T_K,a,b)
        return VMRK0
    
    R = 8.314e-3 # in kJ/mol/K
    P_kb = P/1000.0
    
    Vi = ((R*T_K)/P_kb) + b
        
    VMRK = NR_VMRK(MRK, dMRK, Vi, 1E20, P_kb,R,T_K,a,b)
        
    if P_kb > p0:
        V = VMRK + c*pow((P_kb-p0),0.5) + d*(P_kb-p0)
        ln_y_virial = (1/(R*T_K))*((2./3.)*c*pow((P_kb-p0),1.5) + (d/2.0)*pow((P_kb-p0),2.0))
    else:
        V = VMRK
        ln_y_virial = 0.0
        
    z = (P_kb*V)/(R*T_K)
    A = a/(b*R*pow(T_K,1.5))
    B = (b*P_kb)/(R*T_K)
        
    ln_y = z - 1.0 - gp.log(z-B) - A*gp.log(1.0 + (B/z)) + ln_y_virial
    return gp.exp(ln_y)
    
###########################
### Shi & Saxena (1992) ###
###########################

def lny_SS(PT,Pcr,Tcr):
    P = PT['P']
    T_K = PT['T']+273.15
    Tr = T_K/Tcr
    A, B, C, D, P0, integral0 = Q_SS(PT,Tr,Pcr)
    Pr = P/Pcr
    P0r = P0/Pcr
    integral = A*gp.log(Pr/P0r) + B*(Pr - P0r) + (C/2.0)*(pow(Pr,2.0) - pow(P0r,2.0)) + (D/3.0)*(pow(Pr,3.0) - pow(P0r,3.0))
    integral_total = integral + integral0
    return integral_total

def Q_SS(PT,Tr,Pcr):
    P = PT['P']
    def Q1000(Pcr):
        Pr_ = 1000.0/Pcr
        P0r_ = 1.0/Pcr
        A0 = 1.0
        B0 = 0.9827e-1*pow(Tr,-1.0) + -0.2709*pow(Tr,-3.0)
        C0 = -0.1030e-2*pow(Tr,-1.5) + 0.1427e-1*pow(Tr,-4.0)
        D0 = 0.0
        return A0*gp.log(Pr_/P0r_) + B0*(Pr_ - P0r_) + (C0/2.0)*(pow(Pr_,2.0) - pow(P0r_,2.0)) + (D0/3.0)*(pow(Pr_,3.0) - pow(P0r_,3.0))
    def Q5000(Pcr):
        Pr_ = 5000.0/Pcr
        P0r_ = 1000.0/Pcr
        A0 = 1.0 + -5.917e-1*pow(Tr,-2.0)
        B0 = 9.122e-2*pow(Tr,-1.0)
        C0 = -1.416e-4*pow(Tr,-2.0) + -2.835e-6*gp.log(Tr)
        D0 = 0.0
        return A0*gp.log(Pr_/P0r_) + B0*(Pr_ - P0r_) + (C0/2.0)*(pow(Pr_,2.0) - pow(P0r_,2.0)) + (D0/3.0)*(pow(Pr_,3.0) - pow(P0r_,3.0))
    if P > 5000.0:
        A = 2.0614 + -2.235*pow(Tr,-2.0) + -3.941e-1*gp.log(Tr)
        B = 5.513e-2*pow(Tr,-1.0) + 3.934e-2*pow(Tr,-2.0)
        C = -1.894e-6*pow(Tr,-1.0) + -1.109e-5*pow(Tr,-2.0) + -2.189e-5*pow(Tr,-3.0)
        D = 5.053e-11*pow(Tr,-1.0) + -6.303e-21*pow(Tr,3.0)
        P0 = 5000.0
        integral0 = Q1000(Pcr) + Q5000(Pcr)
        return A, B, C, D, P0, integral0
    elif P == 5000.0:
        A = 0
        B = 0
        C = 0
        D = 0
        P0 = 5000.0
        integral0 = Q1000(Pcr) + Q5000(Pcr)
        return A, B, C, D, P0, integral0
    elif P > 1000.0 and P < 5000.0:
        A = 1.0 + -5.917e-1*pow(Tr,-2.0)
        B = 9.122e-2*pow(Tr,-1.0)
        C = -1.416e-4*pow(Tr,-2.0) + -2.835e-6*gp.log(Tr)
        D = 0.0
        P0 = 1000.0
        integral0 = Q1000(Pcr)
        return A, B, C, D, P0, integral0
    elif P == 1000.0:
        A = 0
        B = 0
        C = 0
        D = 0.0
        P0 = 1000.0
        integral0 = Q1000(Pcr)
        return A, B, C, D, P0, integral0
    else:
        A = 1.0
        B = 0.9827e-1*pow(Tr,-1.0) + -0.2709*pow(Tr,-3.0)
        C = -0.1030e-2*pow(Tr,-1.5) + 0.1427e-1*pow(Tr,-4.0)
        D = 0.0
        P0 = 1.0
        integral0 = 0.0
        return A, B, C, D, P0, integral0
    
def y_SS(gas_species,PT,species,models):
    P = PT['P']
    T_K = PT['T']+273.15
    ideal_gas = models.loc["ideal_gas","option"]
    if ideal_gas == "yes":
        return 1.0
    elif P < 1.: # ideal gas below 1 bar
        return 1.
    else:    
        Tcr = species.loc[gas_species,"Tcr"]
        Pcr = species.loc[gas_species,"Pcr"]
        return gp.exp(lny_SS(PT,Pcr,Tcr))/P    

##############################
### for each vapor species ###    
##############################

def y_H2(PT,species,models):
    P = PT['P']
    T_K = PT['T']+273.15
    ideal_gas = models.loc["ideal_gas","option"]
    if ideal_gas == "yes":
        return 1.0
    elif P < 1.: # ideal gas below 1 bar
        return 1.
    elif models.loc["y_H2","option"] == "SW64": # Shaw & Wones (1964)
        SW1 = gp.exp(-3.8402*pow(T_K,0.125)+0.5410)
        SW2 = gp.exp(-0.1263*pow(T_K,0.5)-15.980)
        SW3 = 300*gp.exp((-0.011901*T_K)-5.941) # NB used a value of -0.011901 instead of -0.11901 as reported to match data in Table 2
        P_atm = 0.986923*P
        ln_y = SW1*P_atm - SW2*pow(P_atm,2.0) + SW3*gp.exp((-P_atm/300.0)-1.0)
        return gp.exp(ln_y)
    elif models.loc["y_H2","option"] == "SS92": # Shi & Saxena (1992) NOT WORKING
        Tcr = 33.25 # critical temperature in K 
        Pcr = 12.9696 # critical temperature in bar
        Tr = T_K/Tcr
        # Q for 1-1000 bar
        Q1_A_LP, Q2_A_LP, Q3_A_LP, Q4_A_LP, Q5_A_LP = 1., 0., 0., 0., 0.
        Q1_B_LP, Q2_B_LP, Q3_B_LP, Q4_B_LP, Q5_B_LP = 0., 0.9827e-1, 0., -0.2709, 0.
        Q1_C_LP, Q2_C_LP, Q3_C_LP, Q4_C_LP, Q5_C_LP = 0., 0., -0.1030e-2, 0., 0.1427e-1
        # Q for 1000-10000 bar
        Q1_A_HP, Q2_A_HP, Q3_A_HP, Q4_A_HP, Q5_A_HP, Q6_A_HP, Q7_A_HP, Q8_A_HP = 2.2615, 0., -6.8712e1, 0., -1.0573e4, 0., 0., -1.6936e-1
        Q1_B_HP, Q2_B_HP, Q3_B_HP, Q4_B_HP, Q5_B_HP, Q6_B_HP, Q7_B_HP, Q8_B_HP = -2.6707e-4, 0., 2.0173e-1, 0., 4.5759, 0., 0., 3.1452e-5
        Q1_C_HP, Q2_C_HP, Q3_C_HP, Q4_C_HP, Q5_C_HP, Q6_C_HP, Q7_C_HP, Q8_C_HP = -2.3376e-9, 0., 3.4091e-7, 0., -1.4188e-3, 0., 0., 3.0117e-10
        Q1_D_HP, Q2_D_HP, Q3_D_HP, Q4_D_HP, Q5_D_HP, Q6_D_HP, Q7_D_HP, Q8_D_HP = -3.2606e-15, 0., 2.4402e-12, 0., -2.4027e-9, 0., 0., 0.
        if P < 1000.:
            A = Q1_A_LP + Q2_A_LP*Tr**(-1.) + Q3_A_LP*Tr**(-1.5) + Q4_A_LP*Tr**(-3.) + Q5_A_LP*Tr**(-4.)
            B = Q1_B_LP + Q2_B_LP*Tr**(-1.) + Q3_B_LP*Tr**(-1.5) + Q4_B_LP*Tr**(-3.) + Q5_B_LP*Tr**(-4.)
            C = Q1_C_LP + Q2_C_LP*Tr**(-1.) + Q3_C_LP*Tr**(-1.5) + Q4_C_LP*Tr**(-3.) + Q5_C_LP*Tr**(-4.)
            D = 0.0
            P0 = 1.0
            integral0 = 0.
        elif P == 1000.:
            A = 0.0
            B = 0.0
            C = 0.0
            D = 0.0
            P0 = 1000.0
            Pr_ = 1000.0/Pcr
            P0r_ = 1.0/Pcr
            A0 = Q1_A_LP + Q2_A_LP*Tr + Q3_A_LP*Tr**(-1.) + Q4_A_LP*Tr**2. + Q5_A_LP*Tr**(-2.)
            B0 = Q1_B_LP + Q2_B_LP*Tr + Q3_B_LP*Tr**(-1.) + Q4_B_LP*Tr**2. + Q5_B_LP*Tr**(-2.)
            C0 = Q1_C_LP + Q2_C_LP*Tr + Q3_C_LP*Tr**(-1.) + Q4_C_LP*Tr**2. + Q5_C_LP*Tr**(-2.)
            D0 = 0.0
            integral0 = A0*gp.log(Pr_/P0r_) + B0*(Pr_ - P0r_) + (C0/2.0)*(pow(Pr_,2.0) - pow(P0r_,2.0)) + (D0/3.0)*(pow(Pr_,3.0) - pow(P0r_,3.0))            
        elif P > 1000.:
            A = Q1_A_HP + Q2_A_HP*Tr + Q3_A_HP*Tr**(-1.) + Q4_A_HP*Tr**2. + Q5_A_HP*Tr**(-2.) + Q6_A_HP*Tr**3. + Q7_A_HP*Tr**(-3.0) + Q8_A_HP*gp.log(Tr)
            B = Q1_B_HP + Q2_B_HP*Tr + Q3_B_HP*Tr**(-1.) + Q4_B_HP*Tr**2. + Q5_B_HP*Tr**(-2.) + Q6_B_HP*Tr**3. + Q7_B_HP*Tr**(-3.0) + Q8_B_HP*gp.log(Tr)
            C = Q1_C_HP + Q2_C_HP*Tr + Q3_C_HP*Tr**(-1.) + Q4_C_HP*Tr**2. + Q5_C_HP*Tr**(-2.) + Q6_C_HP*Tr**3. + Q7_C_HP*Tr**(-3.0) + Q8_C_HP*gp.log(Tr)
            D = Q1_D_HP + Q2_D_HP*Tr + Q3_D_HP*Tr**(-1.) + Q4_D_HP*Tr**2. + Q5_D_HP*Tr**(-2.) + Q6_D_HP*Tr**3. + Q7_D_HP*Tr**(-3.0) + Q8_D_HP*gp.log(Tr)
            P0 = 1000.0
            Pr_ = 1000.0/Pcr
            P0r_ = 1.0/Pcr
            A0 = Q1_A_LP + Q2_A_LP*Tr + Q3_A_LP*Tr**(-1.) + Q4_A_LP*Tr**2. + Q5_A_LP*Tr**(-2.)
            B0 = Q1_B_LP + Q2_B_LP*Tr + Q3_B_LP*Tr**(-1.) + Q4_B_LP*Tr**2. + Q5_B_LP*Tr**(-2.)
            C0 = Q1_C_LP + Q2_C_LP*Tr + Q3_C_LP*Tr**(-1.) + Q4_C_LP*Tr**2. + Q5_C_LP*Tr**(-2.)
            D0 = 0.0
            integral0 = A0*gp.log(Pr_/P0r_) + B0*(Pr_ - P0r_) + (C0/2.0)*(pow(Pr_,2.0) - pow(P0r_,2.0)) + (D0/3.0)*(pow(Pr_,3.0) - pow(P0r_,3.0))
        P0r = P0/Pcr
        Pr = P/Pcr
        integral = A*gp.log(Pr/P0r) + B*(Pr - P0r) + (C/2.0)*(pow(Pr,2.0) - pow(P0r,2.0)) + (D/3.0)*(pow(Pr,3.0) - pow(P0r,3.0))
        return gp.exp(integral + integral0)/P

def y_H2O(PT,species,models):
    P = PT['P']
    T_K = PT['T']+273.15
    ideal_gas = models.loc["ideal_gas","option"]
    if ideal_gas == "yes":
        return 1.
    elif P < 1.: # ideal gas below 1 bar
        return 1.
    if models.loc["y_H2O","option"] == "HP91": 
    # (T > 673 K only) - using Holland & Powell (1991) CORK
        p0 = 2.00 # in kb
        a = 1113.4 + -0.22291*(T_K - 673.0) + -3.8022e-4*pow((T_K-673.0),2.0) + 1.7791e-7*pow((T_K-673.0),3.0)
        b = 1.465
        c = -3.025650e-2 + -5.343144e-6*T_K
        d = -3.2297554e-3 + 2.2215221e-6*T_K
        y = CORK(PT,p0,a,b,c,d)
        return y

def y_CO2(PT,species,models):
    P = PT['P']
    T_K = PT['T']+273.15
    ideal_gas = models.loc["ideal_gas","option"]
    if ideal_gas == "yes":
        return 1.0
    elif P < 1.: # ideal gas below 1 bar
        return 1.
    else:
        if models.loc["y_CO2","option"] == "HP91": # use Holland & Powell (1991)
            p0 = 5.00 # in kb
            a = 741.2 + -0.10891*(T_K) + -3.4203e-4*pow(T_K,2.0)
            b = 3.057
            c = -2.26924e-1 + -7.73793e-5*T_K
            d = 1.33790e-2 + -1.1740e-5*T_K
            y = CORK(PT,p0,a,b,c,d)
        elif models.loc["y_CO2","option"] == "SS92": # use Shi & Saxena (1992)
            gas_species = "CO2"
            y = y_SS(gas_species,PT,species,models)
        return y
    
def y_O2(PT,species,models):
    if models.loc["y_O2","option"] == "SS92":
        gas_species = "O2"
        y = y_SS(gas_species,PT,species,models)
    return y
    
def y_S2(PT,species,models):
    if models.loc["y_S2","option"] == "SS92":
        gas_species = "S2"
        y = y_SS(gas_species,PT,species,models)
    return y

def y_CO(PT,species,models):
    if models.loc["y_CO","option"] == "SS92":
        gas_species = "CO"
        y = y_SS(gas_species,PT,species,models)
    return y
    
def y_CH4(PT,species,models):
    if models.loc["y_CH4","option"] == "SS92":
        gas_species = "CH4"
        y = y_SS(gas_species,PT,species,models)
    return y
    
def y_OCS(PT,species,models):
    if models.loc["y_OCS","option"] == "SS92":
        gas_species = "OCS"
        y = y_SS(gas_species,PT,species,models)
    return y

def y_X(PT,species,models): # species X fugacity coefficient
    if models.loc["y_X","option"] == "ideal":  # ideal gas
        y = 1.
    return y

#################################################################################
### SO2 and H2S from Shi & Saxena (1992) with option to modify below 500 bars ###
#################################################################################

def y_SO2(PT,species,models):
    P = PT['P']
    T_K = PT['T']+273.15
    ideal_gas = models.loc["ideal_gas","option"]
    gas_species = "SO2"
    if ideal_gas == "yes":
        return 1.
    elif P < 1.: # ideal gas below 1 bar
        return 1.
    else: # 1-10000 bar
        Tcr = species.loc[gas_species,"Tcr"] # critical temperature in K
        Pcr = species.loc[gas_species,"Pcr"] # critical temperature in bar
        P0 = 1.0
        P0r = P0/Pcr
        Tr = T_K/Tcr
        Q1_A, Q2_A, Q3_A, Q4_A, Q5_A, Q6_A, Q7_A, Q8_A  = 0.92854, 0.43269e-1, -0.24671, 0., 0.24999, 0., -0.53182, -0.16461e-1
        Q1_B, Q2_B, Q3_B, Q4_B, Q5_B, Q6_B, Q7_B, Q8_B  = 0.84866e-3, -0.18379e-2, 0.66787e-1, 0., -0.29427e-1, 0., 0.29003e-1, 0.54808e-2
        Q1_C, Q2_C, Q3_C, Q4_C, Q5_C, Q6_C, Q7_C, Q8_C  = -0.35456e-3, 0.23316e-4, 0.94159e-3, 0., -0.81653e-3, 0., 0.23154e-3, 0.55542e-4
        A = Q1_A + Q2_A*Tr + Q3_A*Tr**(-1.) + Q4_A*Tr**2. + Q5_A*Tr**(-2.) + Q6_A*Tr**3. + Q7_A*Tr**(-3.0) + Q8_A*gp.log(Tr)
        B = Q1_B + Q2_B*Tr + Q3_B*Tr**(-1.) + Q4_B*Tr**2. + Q5_B*Tr**(-2.) + Q6_B*Tr**3. + Q7_B*Tr**(-3.0) + Q8_B*gp.log(Tr)
        C = Q1_C + Q2_C*Tr + Q3_C*Tr**(-1.) + Q4_C*Tr**2. + Q5_C*Tr**(-2.) + Q6_C*Tr**3. + Q7_C*Tr**(-3.0) + Q8_C*gp.log(Tr)
        D = 0.0
        if P >= 500.: # above 500 bar using Shi and Saxena (1992) as is
            Pr = P/Pcr
            integral = A*gp.log(Pr/P0r) + B*(Pr - P0r) + (C/2.0)*(pow(Pr,2.0) - pow(P0r,2.0)) + (D/3.0)*(pow(Pr,3.0) - pow(P0r,3.0))
            y = (gp.exp(integral))/P
        elif models.loc["y_SO2","option"] == "SS92": # as is Shi and Saxena (1992)
            Pr = P/Pcr
            integral = A*gp.log(Pr/P0r) + B*(Pr - P0r) + (C/2.0)*(pow(Pr,2.0) - pow(P0r,2.0)) + (D/3.0)*(pow(Pr,3.0) - pow(P0r,3.0))
            y = (gp.exp(integral))/P
        elif models.loc["y_SO2","option"] == "SS92_modified": # below 500 bar linear fit between the value at 500 bar and y = 1 at 1 bar to avoid weird behaviour...
            Pr = 500./Pcr # calculate y at 500 bar
            integral = A*gp.log(Pr/P0r) + B*(Pr - P0r) + (C/2.0)*(pow(Pr,2.0) - pow(P0r,2.0)) + (D/3.0)*(pow(Pr,3.0) - pow(P0r,3.0))
            y_500 = (gp.exp(integral))/500.
            y = ((y_500 - 1.)*(P/500.)) + 1. # linear extrapolation to P of interest
        return y       
            
def y_H2S(PT,species,models):
    P = PT['P']
    T_K = PT['T']+273.15
    ideal_gas = models.loc["ideal_gas","option"]
    gas_species = "H2S"
    if ideal_gas == "yes":
        return 1.0
    elif ideal_gas == "no":
        Tcr = species.loc[gas_species,"Tcr"] # critical temperature in K 
        Pcr = species.loc[gas_species,"Pcr"] # critical temperature in bar
        Tr = T_K/Tcr
        # Q for 1-500 bar
        Q1_A_LP, Q2_A_LP, Q3_A_LP, Q4_A_LP, Q5_A_LP, Q6_A_LP, Q7_A_LP, Q8_A_LP = 0.14721e1, 0.11177e1, 0.39657e1, 0., -0.10028e2, 0., 0.45484e1, -0.382e1
        Q1_B_LP, Q2_B_LP, Q3_B_LP, Q4_B_LP, Q5_B_LP, Q6_B_LP, Q7_B_LP, Q8_B_LP = 0.16066, 0.10887, 0.29014, 0., -0.99593, 0., -0.18627, -0.45515
        Q1_C_LP, Q2_C_LP, Q3_C_LP, Q4_C_LP, Q5_C_LP, Q6_C_LP, Q7_C_LP, Q8_C_LP = -0.28933, -0.70522e-1, 0.39828, 0., -0.50533e-1, 0., 0.1176, 0.33972
        # Q for 500-10000 bar
        Q1_A_HP, Q2_A_HP, Q3_A_HP, Q4_A_HP, Q5_A_HP, Q6_A_HP, Q7_A_HP, Q8_A_HP = 0.59941, -0.1557e-2, 0.4525e-1, 0., 0.36687, 0., -0.79248, 0.26058
        Q1_B_HP, Q2_B_HP, Q3_B_HP, Q4_B_HP, Q5_B_HP, Q6_B_HP, Q7_B_HP, Q8_B_HP = 0.22545e-1, 0.17473e-2, 0.48253e-1, 0., -0.1989e-1, 0., 0.32794e-1, -0.10985e-1
        Q1_C_HP, Q2_C_HP, Q3_C_HP, Q4_C_HP, Q5_C_HP, Q6_C_HP, Q7_C_HP, Q8_C_HP = 0.57375e-3, -0.20944e-5, -0.11894e-2, 0., 0.14661e-2, 0., -0.75605e-3, -0.27985e-3
        if P < 1.:
            return 1. # ideal gas below 1 bar
        elif P < 500.:
            if models.loc["y_H2S","option"] == "SS92": # as is Shi and Saxena (1992) 
                A = Q1_A_LP + Q2_A_LP*Tr + Q3_A_LP*Tr**(-1.) + Q4_A_LP*Tr**2. + Q5_A_LP*Tr**(-2.) + Q6_A_LP*Tr**3. + Q7_A_LP*Tr**(-3.0) + Q8_A_LP*gp.log(Tr)
                B = Q1_B_LP + Q2_B_LP*Tr + Q3_B_LP*Tr**(-1.) + Q4_B_LP*Tr**2. + Q5_B_LP*Tr**(-2.) + Q6_B_LP*Tr**3. + Q7_B_LP*Tr**(-3.0) + Q8_B_LP*gp.log(Tr)
                C = Q1_C_LP + Q2_C_LP*Tr + Q3_C_LP*Tr**(-1.) + Q4_C_LP*Tr**2. + Q5_C_LP*Tr**(-2.) + Q6_C_LP*Tr**3. + Q7_C_LP*Tr**(-3.0) + Q8_C_LP*gp.log(Tr)
                D = 0.0
                P0 = 1.0
                integral0 = 0.
            elif models.loc["y_SO2","option"] == "SS92_modified": # below 500 bar linear fit between the value at 500 bar and y = 1 at 1 bar to avoid weird behaviour... 
                P0 = 500.0 # calculate y at 500 bars
                Pr_ = 500.0/Pcr
                P0r_ = 1.0/Pcr
                A0 = Q1_A_LP + Q2_A_LP*Tr + Q3_A_LP*Tr**(-1.) + Q4_A_LP*Tr**2. + Q5_A_LP*Tr**(-2.) + Q6_A_LP*Tr**3. + Q7_A_LP*Tr**(-3.0) + Q8_A_LP*gp.log(Tr)
                B0 = Q1_B_LP + Q2_B_LP*Tr + Q3_B_LP*Tr**(-1.) + Q4_B_LP*Tr**2. + Q5_B_LP*Tr**(-2.) + Q6_B_LP*Tr**3. + Q7_B_LP*Tr**(-3.0) + Q8_B_LP*gp.log(Tr)
                C0 = Q1_C_LP + Q2_C_LP*Tr + Q3_C_LP*Tr**(-1.) + Q4_C_LP*Tr**2. + Q5_C_LP*Tr**(-2.) + Q6_C_LP*Tr**3. + Q7_C_LP*Tr**(-3.0) + Q8_C_LP*gp.log(Tr)
                D0 = 0.0
                integral0 = A0*gp.log(Pr_/P0r_) + B0*(Pr_ - P0r_) + (C0/2.0)*(pow(Pr_,2.0) - pow(P0r_,2.0)) + (D0/3.0)*(pow(Pr_,3.0) - pow(P0r_,3.0))            
                y_500 = gp.exp(integral0)/500.
                y = ((y_500 - 1.)*(P/500.)) + 1. # linear extrapolation to P of interest
                return y
        elif P == 500.:
            A = 0.0
            B = 0.0
            C = 0.0
            D = 0.0
            P0 = 500.0
            Pr_ = 500.0/Pcr
            P0r_ = 1.0/Pcr
            A0 = Q1_A_LP + Q2_A_LP*Tr + Q3_A_LP*Tr**(-1.) + Q4_A_LP*Tr**2. + Q5_A_LP*Tr**(-2.) + Q6_A_LP*Tr**3. + Q7_A_LP*Tr**(-3.0) + Q8_A_LP*gp.log(Tr)
            B0 = Q1_B_LP + Q2_B_LP*Tr + Q3_B_LP*Tr**(-1.) + Q4_B_LP*Tr**2. + Q5_B_LP*Tr**(-2.) + Q6_B_LP*Tr**3. + Q7_B_LP*Tr**(-3.0) + Q8_B_LP*gp.log(Tr)
            C0 = Q1_C_LP + Q2_C_LP*Tr + Q3_C_LP*Tr**(-1.) + Q4_C_LP*Tr**2. + Q5_C_LP*Tr**(-2.) + Q6_C_LP*Tr**3. + Q7_C_LP*Tr**(-3.0) + Q8_C_LP*gp.log(Tr)
            D0 = 0.0
            integral0 = A0*gp.log(Pr_/P0r_) + B0*(Pr_ - P0r_) + (C0/2.0)*(pow(Pr_,2.0) - pow(P0r_,2.0)) + (D0/3.0)*(pow(Pr_,3.0) - pow(P0r_,3.0))            
        elif P > 500.:
            A = Q1_A_HP + Q2_A_HP*Tr + Q3_A_HP*Tr**(-1.) + Q4_A_HP*Tr**2. + Q5_A_HP*Tr**(-2.) + Q6_A_HP*Tr**3. + Q7_A_HP*Tr**(-3.0) + Q8_A_HP*gp.log(Tr)
            B = Q1_B_HP + Q2_B_HP*Tr + Q3_B_HP*Tr**(-1.) + Q4_B_HP*Tr**2. + Q5_B_HP*Tr**(-2.) + Q6_B_HP*Tr**3. + Q7_B_HP*Tr**(-3.0) + Q8_B_HP*gp.log(Tr)
            C = Q1_C_HP + Q2_C_HP*Tr + Q3_C_HP*Tr**(-1.) + Q4_C_HP*Tr**2. + Q5_C_HP*Tr**(-2.) + Q6_C_HP*Tr**3. + Q7_C_HP*Tr**(-3.0) + Q8_C_HP*gp.log(Tr)
            D = 0.0
            P0 = 500.0
            Pr_ = 500.0/Pcr
            P0r_ = 1.0/Pcr
            A0 = Q1_A_LP + Q2_A_LP*Tr + Q3_A_LP*Tr**(-1.) + Q4_A_LP*Tr**2. + Q5_A_LP*Tr**(-2.) + Q6_A_LP*Tr**3. + Q7_A_LP*Tr**(-3.0) + Q8_A_LP*gp.log(Tr)
            B0 = Q1_B_LP + Q2_B_LP*Tr + Q3_B_LP*Tr**(-1.) + Q4_B_LP*Tr**2. + Q5_B_LP*Tr**(-2.) + Q6_B_LP*Tr**3. + Q7_B_LP*Tr**(-3.0) + Q8_B_LP*gp.log(Tr)
            C0 = Q1_C_LP + Q2_C_LP*Tr + Q3_C_LP*Tr**(-1.) + Q4_C_LP*Tr**2. + Q5_C_LP*Tr**(-2.) + Q6_C_LP*Tr**3. + Q7_C_LP*Tr**(-3.0) + Q8_C_LP*gp.log(Tr)
            D0 = 0.0
            integral0 = A0*gp.log(Pr_/P0r_) + B0*(Pr_ - P0r_) + (C0/2.0)*(pow(Pr_,2.0) - pow(P0r_,2.0)) + (D0/3.0)*(pow(Pr_,3.0) - pow(P0r_,3.0))
        P0r = P0/Pcr
        Pr = P/Pcr
        integral = A*gp.log(Pr/P0r) + B*(Pr - P0r) + (C/2.0)*(pow(Pr,2.0) - pow(P0r,2.0)) + (D/3.0)*(pow(Pr,3.0) - pow(P0r,3.0))
        return gp.exp(integral + integral0)/P
    
def y_SO3(PT,species,models):
    return 1.

#######################
### oxygen fugacity ###
#######################

# buffers
def NNO(PT,models):
    P = PT['P']
    T_K = PT["T"]+273.15
    if models.loc["NNObuffer","option"] == "Frost91":
        buffer = (-24930/T_K + 9.36 + 0.046*(P-1.0)/T_K) # Frost (1991)
    return buffer
def FMQ(PT,models):
    P = PT['P']
    T_K = PT["T"]+273.15
    if models.loc["FMQbuffer","option"] == "Frost91":
        buffer = (-25096.3/T_K + 8.735 + 0.11*(P-1.0)/T_K) # Frost (1991)
    elif models.loc["FMQbuffer","option"] == "ONeill87":
        buffer = (8.58 - (25050/T_K)) # O'Neill (1987)
    return buffer


# terms for different equations

def FefO2_KC91_Eq7_terms(run,PT,melt_wf,setup,species,models): # terms for Kress & Carmichael (1991) Equation 7
    # ln(XFe2O3/XFeO) = alnfO2 + (b/T) + c + sum(dX) + e[1 - (T0/T) = ln(T/T0)] + f(P/T) + g(((T-T0)P)/T) + h(P2/T)
    # ln(XFe2O3/XFeO) = alnfO2 + B
    # terms
    a = 0.196
    # sum(dX)
    # mole frations in the melt based on oxide components (all Fe as FeO) with no volatiles
    tot,Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P, H2O, CO2, S, X = mg.melt_mole_fraction(run,melt_wf,setup,species,models,"no","no")
    DAl = -2.243
    DFe = -1.828
    DCa = 3.201
    DNa = 5.854
    DK = 6.215
    D4X = DAl*Al + DFe*FeT + DCa*Ca + DNa*Na + DK*K
    # PT term
    P = PT['P']
    T_K = PT['T']+273.15
    b = 1.1492e4 # K
    c = -6.675
    e = -3.36
    f = -7.01e-7 # K/Pa
    g = -1.54e-10 # /Pa
    h = 3.85e-17 # K/Pa2
    T0 = 1673.0 # K
    P_Pa = P*1.0e5 # converts bars to pascals
    B = (b/T_K) + c + D4X + e*(1.0 - (T0/T_K) - math.log(T_K/T0)) + f*(P_Pa/T_K) + g*(((T_K-T0)*P_Pa)/T_K) + h*((P_Pa**2.0)/T_K) 
    return a, B

def FefO2_KC91_EqA_terms(run,PT,melt_wf,setup,species,models): # terms for Kress & Carmichael (1991) Appendix Equations A1-6
    # XFeO1.5/XFeO = (KD1*fO2**0.25 + 2y*KD2*KD1**2y*fO2**0.5y)/(1 + (1-2y)KD2*KD1**2y*fO2**0.5y)
    KD2 = 0.4
    y = 0.3
    # compositional term
    # mole frations in the melt based on oxide components (all Fe as FeO) with no volatiles
    tot,Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P, H2O, CO2, S, X = mg.melt_mole_fraction(run,melt_wf,setup,species,models,"no","no")
    DWAl = 39.86e3             #J
    DWCa = -62.52e3            #J
    DWNa = -102.0e3            #J
    DWK = -119.0e3             #J
    D4X = DWAl*Al+DWCa*Ca+DWNa*Na+DWK*K
    # KD1
    T_K = PT['T']+273.15
    P = PT['P']
    DH = -106.2e3               #J
    DS = -55.10                 #J/K
    DCp = 31.86                 #J/K
    DV = 7.42e-6                #m3
    DVdot = 1.63e-9             #m3/K
    DVdash = -8.16e-16          #m3/Pa
    T0 = 1673.0                 # K
    P0 = 1.0e5                  # Pa 
    R = 8.3144598               # J/K/mol
    P_Pa = P*1.0e5
    KD1 = math.exp((-DH/(R*T_K)) + (DS/R) - (DCp/R)*(1.0 - (T0/T_K) - gp.log(T_K/T0)) - (1.0/(R*T_K))*D4X - ((DV*(P_Pa-P0))/(R*T_K)) - ((DVdot*(T_K-T0)*(P_Pa-P0))/(R*T_K)) - (DVdash/(2.0*R*T_K))*pow((P_Pa-P0),2.0))
    return KD1, KD2, y

def FefO2_ONeill18_terms(run,PT,melt_wf,setup,species):
    # O'Neill et al. (2018) EPSL 504:152-162
    # 1n(Fe3Fe2) = a*DFMQ + B
    a = 0.125
    # mole fractions on a single cation basis in the melt based on oxide components (all Fe as FeO) with no volatiles
    tot,Si, Ti, Al, FeT, Fe2, Fe3, Mg, Mn, Ca, Na, K, P, H2O, CO2, S, X = mg.melt_cation_proportion(run,melt_wf,setup,species,"volatiles","Fe speciation")
    B = - 1.36 + 2.4*Ca + 2.0*Na + 3.7*K - 2.4*P
    # FMQ
    T_K = PT['T']+273.15
    FMQ = 8.58 - (25050/T_K) # O'Neill (1987)
    return a, B, FMQ

def FefO2_Borisov18_terms(run,PT,melt_wf,setup,species,models):
    T_K = PT['T']+273.15
    # Borisov et al. (2018) CMP 173
    a = 0.207
    # melt mole fraction with no volatiles and all Fe as FeOT
    tot,Si, Ti, Al, FeOT, FeO, Fe2O3, Mg, Mn, Ca, Na, K, P, H2O, CO2, S, X = mg.melt_mole_fraction(run,melt_wf,setup,species,models,"no","no")  
    B = (4633.3/T_K -0.445*Si - 0.900*Ti + 1.532*Mg + 0.314*Ca + 2.030*Na + 3.355*K - 4.851*P - 3.081*Si*Al -  4.370*Si*Mg - 1.852)
    return a, B

def fO22Fe3FeT(fO2,run,PT,melt_wf,setup,species,models): # converting fO2 to Fe3/FeT
    model = models.loc["fO2","option"]
    T_K = PT['T']+273.15
    
    if model == "Kress91":
        a, PTterm = FefO2_KC91_Eq7_terms(run,PT,melt_wf,setup,species,models)
        lnXFe2O3XFeO = a*gp.log(fO2) + PTterm
        XFe2O3XFeO = gp.exp(lnXFe2O3XFeO)
        return (2.0*XFe2O3XFeO)/((2.0*XFe2O3XFeO)+1.0)
    
    elif model == "Kress91A": 
        kd1, KD2, y = FefO2_KC91_EqA_terms(run,PT,melt_wf,setup,species,models)
        XFeO15XFeO = ((kd1*fO2**0.25)+(2.0*y*KD2*(kd1**(2.0*y))*(fO2**(0.5*y))))/(1.0 + (1.0 - 2.0*y)*KD2*(kd1**(2.0*y))*(fO2**(0.5*y)))
        return XFeO15XFeO/(XFeO15XFeO+1.0)  
    
    elif model == "ONeill18": # O'Neill et al. (2018) EPSL 504:152-162
        a,B,FMQ = FefO2_ONeill18_terms(run,PT,melt_wf,setup,species)
        DQFM = gp.log10(fO2) - FMQ
        lnFe3Fe2 = a*DQFM + B
        Fe3Fe2 =  gp.exp(lnFe3Fe2)
        return Fe3Fe2/(Fe3Fe2 + 1.0)
    
    elif model == "Borisov18": # Borisov et al. (2018) CMP 173:
        a,B = FefO2_Borisov18_terms(run,PT,melt_wf,setup,species,models)
        Fe3Fe2 = 10.**(a*gp.log10(fO2) + B)
        return Fe3Fe2/(Fe3Fe2 + 1.0)

def f_O2(run,PT,melt_wf,setup,species,models):
    
    model = models.loc["fO2","option"]
    
    def KC91(run,PT,melt_wf,setup,species,models):
        a, PTterm = FefO2_KC91_Eq7_terms(run,PT,melt_wf,setup,species,models)
        F = 0.5*mg.Fe3Fe2(melt_wf) # XFe2O3/XFeO
        alnfO2 = math.log(F) - PTterm
        fO2 = math.exp(alnfO2/a)
        return fO2
    
    if model == "yes":
        return 10.0**(setup.loc[run,"logfO2"]) 
    
    elif model == "Kress91":
        fO2 = KC91(run,PT,melt_wf,setup,species,models)
        return fO2
    
    elif model == "Kress91A": 
        F = mg.Fe3Fe2(melt_wf) # XFeO1.5/XFeO
        kd1, KD2, y = FefO2_KC91_EqA_terms(run,PT,melt_wf,setup,species,models)
            
        def f(y,F,KD2,kd1,x): # KC91A rearranged to equal 0
            f = ((2.0*y - F + 2.0*y*F)*KD2*kd1**(2.0*y)*x**(0.5*y) + kd1*x**0.25 - F)
            return f

        def df(y,F,KD2,kd1,x): # derivative of above
            df = (0.5*y)*(2.0*y - F +2.0*y*F)*KD2*kd1**(2.0*y)*x**((0.5*y)-1.0) + 0.25*kd1*x**-0.75
            return df

        def dx(x):
            diff = abs(0-f(y,F,KD2,kd1,x))
            return diff
 
        def nr(x0, e1):
            delta1 = dx(x0)
            while delta1 > e1:
                x0 = x0 - f(y,F,KD2,kd1,x0)/df(y,F,KD2,kd1,x0)
                delta1 = dx(x0)
            return x0
            
        x0 = KC91(run,PT,melt_wf,setup,species,models)
    
        fO2 = nr(x0, 1.e-15)
        return fO2
        
    elif model == "ONeill18": # O'Neill et al. (2018) EPSL 504:152-162
        F = mg.Fe3Fe2(melt_wf) # Fe3+/Fe2+
        a,B,FMQ = FefO2_ONeill18_terms(run,PT,melt_wf,setup,species)
        DQFM = (math.log(F) - B)/a
        logfO2 = DQFM + FMQ
        return 10.0**logfO2
    
    elif model == "S6ST": # remove?!?!
        S6T = melt_wf['S6ST']
        S62 = mg.overtotal2ratio(S6T)
        fO2 = mg.S6S2_2_fO2(S62,melt_wf,run,PT,setup,species,models)
        return fO2
    
    elif model == "Borisov18": # Borisov et al. (2018) CMP 173
        F = mg.Fe3Fe2(melt_wf)
        a,B = FefO2_Borisov18_terms(run,PT,melt_wf,setup,species,models)
        fO2 = 10.**((gp.log10(F) - B)/a)
        return fO2
    
def S_Nash19_terms(PT): # Nash et al. 2019
    T_K = PT['T']+273.15
    A = 8.
    B = ((8.7436e6)/pow(T_K,2.0)) - (27703.0/T_K) + 20.273
    return A, B

# density of the melt in g/cm3 using DensityX (Iacovino & Till 2019 Volcanica 2(1))
def melt_density(run,PT,melt_wf,setup,species):
    SiO2, TiO2, Al2O3, FeOT, FeO, Fe2O3, MgO, CaO, Na2O, K2O, P2O5, H2O, CO2, S, X = melt_normalise_wf(run,melt_wf,setup,species,"water","yes")
    P = PT["P"]
    T = PT["T"]
    melt_dx = pd.DataFrame([[setup.loc[run,"Sample"],SiO2,TiO2,Al2O3,FeO,Fe2O3,MgO,CaO,Na2O,K2O,H2O,P,T]])
    melt_dx.columns = ["Sample_ID","SiO2","TiO2","Al2O3","FeO","Fe2O3","MgO","CaO","Na2O","K2O","H2O","P","T"]
    output = dx.Density(melt_dx)
    density = output.loc[0,"Density_g_per_cm3"]
    return density