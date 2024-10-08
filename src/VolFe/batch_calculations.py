# batch_calculations.py

import pandas as pd
from datetime import date
import numpy as np
import datetime
import math as math
import warnings as w

import VolFe.melt_gas as mg
import VolFe.equilibrium_equations as eq
import VolFe.isotopes as iso
import VolFe.model_dependent_variables as mdv
import VolFe.calculations as c

################
### Contents ###
################
# building results tables
# options from setup file
# calculate the pressure of vapor saturation
# calculate de/regassing paths
# calculate isobars
# calculate solubility constants
# calculate fugacity coefficients
# Use melt S oxybarometer
# measured parameters within error
# Below this: in development

###############################
### building results tables ###
###############################
# outputing sample name
def results_table_sample_name(setup,run):
    results_headers = pd.DataFrame([["sample"]])
    results_values = pd.DataFrame([[setup.loc[run,"Sample"]]])
    return results_headers, results_values
# outputting melt composition, T, P
def results_table_melt_comp_etc(PT,melt_comp,conc,frac,melt_wf):
    results_headers = pd.DataFrame([["T_C","P_bar",
        "SiO2_wtpc", "TiO2_wtpc", "Al2O3_wtpc", "FeOT_wtpc", "MnO_wtpc", "MgO_wtpc", "CaO_wtpc", "Na2O_wtpc", "K2O_wtpc", "P2O5_wtpc",
        "H2OT_wtpc","OH_wtpc","H2Omol_wtpc","H2_ppmw","CH4_ppmw","CO2T_ppmw","CO2mol_ppmw","CO2carb_ppmw","CO_ppmw","S2-_ppmw","S6+_ppmw","H2S_ppmw",
        "H_H2OT/HT", "H_H2/HT", "H_CH4/HT", "H_H2S/HT", "C_CO2T/CT", "C_CO/CT", "C_CH4/CT", "S2-/ST", "S6+/ST", "H2S/ST", "Fe3+/FeT","sulf_XFe","sulf_XCu","sulf_XNi"]])
    if "sulf_XFe" in melt_wf:
        melt_wf
    else:
        melt_wf["sulf_XFe"] = 1.
    if "sulf_XCu" in melt_wf:
        melt_wf
    else:
        melt_wf["sulf_XCu"] = 0.
    if "sulf_XNi" in melt_wf:
        melt_wf
    else:
        melt_wf["sulf_XNi"] = 0.
    results_values = pd.DataFrame([[PT["T"],PT["P"],
                melt_comp["SiO2"]*100., melt_comp["TiO2"]*100., melt_comp["Al2O3"]*100., melt_comp["FeOT"]*100., melt_comp["MnO"]*100., melt_comp["MgO"]*100., melt_comp["CaO"]*100., melt_comp["Na2O"]*100., melt_comp["K2O"]*100., melt_comp["P2O5"]*100.,
                conc["wm_H2O"]*100.,conc["wm_OH"]*100,conc["wm_H2Omol"]*100.,conc["wm_H2"]*1000000.,conc["wm_CH4"]*1000000.,conc["wm_CO2"]*1000000.,conc["wm_CO2mol"]*1000000,conc["wm_CO2carb"]*1000000,conc["wm_CO"]*1000000.,conc["wm_S2m"]*1000000.,conc["wm_S6p"]*1000000.,conc["wm_H2S"]*1000000.,
                frac["H2O_HT"], frac["H2_HT"], frac["CH4_HT"], frac["H2S_HT"], frac["CO2_CT"], frac["CO_CT"], frac["CH4_CT"], frac["S2m_ST"], frac["S6p_ST"], frac["H2S_ST"],melt_wf["Fe3FeT"],melt_wf["sulf_XFe"],melt_wf["sulf_XCu"],melt_wf["sulf_XNi"]]])
    return results_headers, results_values
def results_table_melt_vol():
    results_headers = pd.DataFrame([["H2OT-eq_wtpc","CO2T-eq_ppmw","ST_ppmw","X_ppmw"]])
    return results_headers
# outputting model options used in the calculation
def results_table_model_options(models): 
    results_headers = pd.DataFrame([["setup opt","COH_species opt","H2S_m opt","species X opt","Hspeciation opt",
                 "fO2 opt","NNObuffer opt","FMQbuffer opt",
                 "carbon dioxide opt","water opt","hydrogen opt","sulfide opt","sulfate opt","hydrogen sulfide opt","methane opt","carbon monoxide opt","species X solubility opt","Cspeccomp opt","Hspeccomp opt",
                 "SCSS opt","SCAS opt","sulfur_saturation opt","sulfur_is_sat opt","graphite_saturation opt","ideal_gas opt",
                 "y_CO2 opt","y_SO2 opt","y_H2S opt","y_H2 opt","y_O2 opt","y_S2 opt","y_CO opt","y_CH4 opt","y_H2O opt","y_OCS opt","y_X opt",
                 "KHOg opt","KHOSg opt","KOSg opt","KOSg2 opt","KCOg opt","KCOHg opt","KOCSg opt","KCOs opt","carbonylsulfide opt",
                 "density opt","Date"]])
    results_values = pd.DataFrame([[models.loc["setup","option"],models.loc["COH_species","option"], models.loc["H2S_m","option"], models.loc["species X","option"],models.loc["Hspeciation","option"], 
                models.loc["fO2","option"], models.loc["NNObuffer","option"], models.loc["FMQbuffer","option"],
                 models.loc["carbon dioxide","option"], models.loc["water","option"], models.loc["hydrogen","option"], models.loc["sulfide","option"], models.loc["sulfate","option"], models.loc["hydrogen sulfide","option"], models.loc["methane","option"], models.loc["carbon monoxide","option"], models.loc["species X solubility","option"], models.loc["Cspeccomp","option"], models.loc["Hspeccomp","option"],
                 models.loc["SCSS","option"], models.loc["SCAS","option"], models.loc["sulfur_saturation","option"], models.loc["sulfur_is_sat","option"], models.loc["graphite_saturation","option"], models.loc["ideal_gas","option"],
                 models.loc["y_CO2","option"], models.loc["y_SO2","option"], models.loc["y_H2S","option"], models.loc["y_H2","option"], models.loc["y_O2","option"], models.loc["y_S2","option"], models.loc["y_CO","option"], models.loc["y_CH4","option"], models.loc["y_H2O","option"],models.loc["y_OCS","option"], models.loc["y_X","option"],
                 models.loc["KHOg","option"], models.loc["KHOSg","option"], models.loc["KOSg","option"], models.loc["KOSg2","option"], models.loc["KCOg","option"], models.loc["KCOHg","option"],models.loc["KOCSg","option"], models.loc["KCOs","option"],models.loc["carbonylsulfide","option"],
                 models.loc["density","option"],datetime.datetime.now()]])
    return results_headers, results_values
# outputting fugacities, partial pressures, gas mole fraction, fugacity coefficients, molecular masses, solubility constants, equilibrium constants, melt density
def results_table_f_p_xg_y_M_C_K_d(PT,melt_wf,models): 
    results_headers = pd.DataFrame([["fO2_DNNO","fO2_DFMQ",
                "fO2_bar","fH2_bar","fH2O_bar","fS2_bar","fSO2_bar","fH2S_bar","fCO2_bar","fCO_bar","fCH4_bar","fOCS_bar","fX_bar",
                "pO2_bar","pH2_bar","pH2O_bar","pS2_bar","pSO2_bar","pH2S_bar","pCO2_bar","pCO_bar","pCH4_bar","pOCS_bar","pX_bar",
                "xgO2_mf","xgH2_mf","xgH2O_mf","xgS2_mf","xgSO2_mf","xgH2S_mf","xgCO2_mf","xgCO_mf","xgCH4_mf","xgOCS_mf","xgX_mf","xgC_S_mf",
                "yO2","yH2","yH2O","yS2","ySO2","yH2S","yCO2","yCO","yCH4","yOCS","yX",
                "M_m_SO","M_m_ox",
                "C_H2O_mf_bar","C_H2_ppm_bar","C_CO2T_mf_bar","C_CO_ppm_bar","C_CH4_ppm_bar","C_S_ppm","C_SO4_ppm_bar","C_H2S_ppm_bar","C_X_ppm_bar",
                "KHOg","KHOSg","KCOg","KCOHg","KOCSg","KSOg","KSOg2","KHOm","KCOm","KCOs",
                "density_gcm3"]])
    results_values = pd.DataFrame([[mg.fO22Dbuffer(PT,mdv.f_O2(PT,melt_wf,models),"NNO",models),mg.fO22Dbuffer(PT,mdv.f_O2(PT,melt_wf,models),"FMQ",models),
                mdv.f_O2(PT,melt_wf,models),mg.f_H2(PT,melt_wf,models),mg.f_H2O(PT,melt_wf,models),mg.f_S2(PT,melt_wf,models),mg.f_SO2(PT,melt_wf,models),mg.f_H2S(PT,melt_wf,models),mg.f_CO2(PT,melt_wf,models),mg.f_CO(PT,melt_wf,models),mg.f_CH4(PT,melt_wf,models),mg.f_OCS(PT,melt_wf,models),mg.f_X(PT,melt_wf,models),
                mg.p_O2(PT,melt_wf,models),mg.p_H2(PT,melt_wf,models),mg.p_H2O(PT,melt_wf,models),mg.p_S2(PT,melt_wf,models),mg.p_SO2(PT,melt_wf,models),mg.p_H2S(PT,melt_wf,models),mg.p_CO2(PT,melt_wf,models),mg.p_CO(PT,melt_wf,models),mg.p_CH4(PT,melt_wf,models),mg.p_OCS(PT,melt_wf,models),mg.p_X(PT,melt_wf,models),
                mg.xg_O2(PT,melt_wf,models),mg.xg_H2(PT,melt_wf,models),mg.xg_H2O(PT,melt_wf,models),mg.xg_S2(PT,melt_wf,models),mg.xg_SO2(PT,melt_wf,models),mg.xg_H2S(PT,melt_wf,models),mg.xg_CO2(PT,melt_wf,models),mg.xg_CO(PT,melt_wf,models),mg.xg_CH4(PT,melt_wf,models),mg.xg_OCS(PT,melt_wf,models),mg.xg_X(PT,melt_wf,models),mg.gas_CS(PT,melt_wf,models),
                mdv.y_O2(PT,models),mdv.y_H2(PT,models),mdv.y_H2O(PT,models),mdv.y_S2(PT,models),mdv.y_SO2(PT,models),mdv.y_H2S(PT,models),mdv.y_CO2(PT,models),mdv.y_CO(PT,models),mdv.y_CH4(PT,models),mdv.y_OCS(PT,models),mdv.y_X(PT,models),
                mg.M_m_SO(melt_wf),mg.M_m_ox(melt_wf,models),
                mdv.C_H2O(PT,melt_wf,models),mdv.C_H2(PT,melt_wf,models),mdv.C_CO3(PT,melt_wf,models),mdv.C_CO(PT,melt_wf,models),mdv.C_CH4(PT,melt_wf,models),mdv.C_S(PT,melt_wf,models),mdv.C_SO4(PT,melt_wf,models),mdv.C_H2S(PT,melt_wf,models),mdv.C_X(PT,melt_wf,models),
                mdv.KHOg(PT,models),mdv.KHOSg(PT,models),mdv.KCOg(PT,models),mdv.KCOHg(PT,models),mdv.KOCSg(PT,models),mdv.KOSg(PT,models),mdv.KOSg2(PT,models),mdv.KHOm(PT,melt_wf,models),mdv.KCOm(PT,melt_wf,models),mdv.KCOs(PT,models),
                mdv.melt_density(PT,melt_wf,models)]])
    return results_headers, results_values
# headers for open system degassing all gas
def results_table_open_all_gas():
    results_headers = pd.DataFrame([["xgO2_all_mf","xgH2_all_mf","xgH2O_all_mf","xgS2_all_mf","xgSO2_all_mf","xgH2S_all_mf","xgCO2_all_mf","xgCO_all_mf","xgCH4_all_mf","xgOCS_all_mf","xgX_all_mf","xgC_S_all_mf"]])
    return results_headers
# saturation conditions
def results_table_sat(sulf_sat_result,PT,melt_wf,models):
    results_headers = pd.DataFrame([["SCSS_ppm","sulfide saturated","SCAS_ppm","anhydrite saturated","ST melt if sat","graphite saturated"]])
    results_values = pd.DataFrame([[sulf_sat_result["SCSS"],sulf_sat_result["sulfide_sat"],sulf_sat_result["SCAS"],sulf_sat_result["sulfate_sat"],sulf_sat_result["ST"],c.graphite_saturation(PT,melt_wf,models)]])
    return results_headers, results_values
# isotopes
def results_table_isotope_R(R,R_all_species_S,R_m_g_S,R_all_species_C,R_m_g_C,R_all_species_H,R_m_g_H):
    headers = pd.DataFrame([["R_ST","R_S_m","R_S_g","R_S_S2-","R_S_S2","R_S_OCS","R_S_H2S","R_S_SO2","R_S_S6+","R_S_H2Smol","a_S_g_m",
                            "R_CT","R_C_m","R_C_g","R_C_CO2","R_C_CO","R_C_CH4",'R_C_OCS',"R_C_COmol","R_C_CH4mol","R_C_CO2mol","R_C_CO32-","a_C_g_m",
                            "R_HT","R_H_m","R_H_g","R_H_H2O","R_H_H2","R_H_CH4","R_H_H2S","R_H_H2mol","R_H_CH4mol","R_H_H2Smol","R_H_H2Omol","R_H_OH-","a_H_g_m"]])
    values = pd.DataFrame([[R['S'],R_m_g_S["R_m"],R_m_g_S["R_g"],R_all_species_S["A"],R_all_species_S["B"],R_all_species_S["C"],R_all_species_S["D"],R_all_species_S["E"],R_all_species_S["F"],R_all_species_S["G"],R_m_g_S["R_g"]/R_m_g_S["R_m"],
                           R['C'],R_m_g_C["R_m"],R_m_g_C["R_g"],R_all_species_C["A"],R_all_species_C["B"],R_all_species_C["C"],R_all_species_C["D"],R_all_species_C["E"],R_all_species_C["F"],R_all_species_C["G"],R_all_species_C["H"],R_m_g_C["R_g"]/R_m_g_C["R_m"],
                           R['H'],R_m_g_H["R_m"],R_m_g_H["R_g"],R_all_species_H["A"],R_all_species_H["B"],R_all_species_H["C"],R_all_species_H["D"],R_all_species_H["E"],R_all_species_H["F"],R_all_species_H["G"],R_all_species_H["H"],R_all_species_H["I"],R_m_g_H["R_g"]/R_m_g_H["R_m"]]])
    return headers, values
#def results_table_isotope_a_D():
#    return headers, values
def results_table_isotope_d(R,R_all_species_S,R_m_g_S,R_all_species_C,R_m_g_C,R_all_species_H,R_m_g_H):
    headers = pd.DataFrame([["d_ST","d_S_m","d_S_g","d_S_S2-","d_S_S2","d_S_OCS","d_S_H2S","d_S_SO2","d_S_S6+","d_S_H2Smol","D_S_g_m",
                            "d_CT","d_C_m","d_C_g","d_C_CO2","d_C_CO","d_C_CH4",'d_C_OCS',"d_C_COmol","d_C_CH4mol","d_C_CO2mol","d_C_CO32-","D_C_g_m",
                            "d_HT","d_H_m","d_H_g","d_H_H2O","d_H_H2","d_H_CH4","d_H_H2S","d_H_H2mol","d_H_CH4mol","d_H_H2Smol","d_H_H2Omol","d_H_OH-","D_H_g_m"]])
    values = pd.DataFrame([[iso.ratio2delta("VCDT",34,'S',R['S']),iso.ratio2delta("VCDT",34,'S',R_m_g_S["R_m"]),iso.ratio2delta("VCDT",34,'S',R_m_g_S["R_g"]),iso.ratio2delta("VCDT",34,'S',R_all_species_S["A"]),iso.ratio2delta("VCDT",34,'S',R_all_species_S["B"]),iso.ratio2delta("VCDT",34,'S',R_all_species_S["C"]),iso.ratio2delta("VCDT",34,'S',R_all_species_S["D"]),iso.ratio2delta("VCDT",34,'S',R_all_species_S["E"]),iso.ratio2delta("VCDT",34,'S',R_all_species_S["F"]),iso.ratio2delta("VCDT",34,'S',R_all_species_S["G"]),iso.alpha2Delta((R_m_g_S["R_g"]/R_m_g_S["R_m"])),
                            iso.ratio2delta("VPDB",13,'C',R['C']),iso.ratio2delta("VPDB",13,'C',R_m_g_C["R_m"]),iso.ratio2delta("VPDB",13,'C',R_m_g_C["R_g"]),iso.ratio2delta("VPDB",13,'C',R_all_species_C["A"]),iso.ratio2delta("VPDB",13,'C',R_all_species_C["B"]),iso.ratio2delta("VPDB",13,'C',R_all_species_C["C"]),iso.ratio2delta("VPDB",13,'C',R_all_species_C["D"]),iso.ratio2delta("VPDB",13,'C',R_all_species_C["E"]),iso.ratio2delta("VPDB",13,'C',R_all_species_C["F"]),iso.ratio2delta("VPDB",13,'C',R_all_species_C["G"]),iso.ratio2delta("VPDB",13,'C',R_all_species_C["H"]),iso.alpha2Delta((R_m_g_C["R_g"]/R_m_g_C["R_m"])),
                            iso.ratio2delta("VSMOW",2,'H',R['H']),iso.ratio2delta("VSMOW",2,'H',R_m_g_H["R_m"]),iso.ratio2delta("VSMOW",2,'H',R_m_g_H["R_g"]),iso.ratio2delta("VSMOW",2,'H',R_all_species_H["A"]),iso.ratio2delta("VSMOW",2,'H',R_all_species_H["B"]),iso.ratio2delta("VSMOW",2,'H',R_all_species_H["C"]),iso.ratio2delta("VSMOW",2,'H',R_all_species_H["D"]),iso.ratio2delta("VSMOW",2,'H',R_all_species_H["E"]),iso.ratio2delta("VSMOW",2,'H',R_all_species_H["F"]),iso.ratio2delta("VSMOW",2,'H',R_all_species_H["G"]),iso.ratio2delta("VSMOW",2,'H',R_all_species_H["H"]),iso.ratio2delta("VSMOW",2,'H',R_all_species_H["I"]),iso.alpha2Delta((R_m_g_H["R_g"]/R_m_g_H["R_m"]))]])
    return headers, values


###############################
### options from setup file ###
###############################
def options_from_setup(run,models,setup):
    """ 
    Allows model options to be read from the setup file rather than models file.


    Parameters
    ----------
    run: float
        Integer of the row in the setup file to read from (note the first row under the headers is row 0).   
    setup: pandas.DataFrame
        Dataframe with melt compositions to be used, require header using the same labels as row labels from models file if you want to use that option.
    models: pandas.DataFrame
        Dataframe of models.csv file.

    Returns
    -------
    results: pandas.DataFrame

    """
    if models.loc["setup","option"] == "False":
        return models
    elif models.loc["setup","option"] == "True":
        # species
        if models.loc["COH_species","option"] == "setup":
            models.loc["COH_species","option"] = setup.loc[run,"COH_species"]
        if models.loc["H2S_m","option"] == "setup":
            models.loc["H2S_m","option"] = setup.loc[run,"H2S_m"]
        if models.loc["species X","option"] == "setup":
            models.loc["species X","option"] = setup.loc[run,"species X"]
        if models.loc["Hspeciation","option"] == "setup":
            models.loc["Hspeciation","option"] = setup.loc[run,"Hspeciation"]
        # oxygen fugacity
        if models.loc["fO2","option"] == "setup":
            models.loc["fO2","option"] = setup.loc[run,"fO2"]
        if models.loc["NNObuffer","option"] == "setup":
            models.loc["NNObuffer","option"] = setup.loc[run,"NNObuffer"]
        if models.loc["FMQbuffer","option"] == "setup":
            models.loc["FMQbuffer","option"] = setup.loc[run,"FMQbuffer"]
        # solubility constants
        if models.loc["carbon dioxide","option"] == "setup":
            models.loc["carbon dioxide","option"] = setup.loc[run,"carbon dioxide"]
        if models.loc["water","option"] == "setup":
            models.loc["water","option"] = setup.loc[run,"water"]
        if models.loc["hydrogen","option"] == "setup":
            models.loc["hydrogen","option"] = setup.loc[run,"hydrogen"]
        if models.loc["sulfide","option"] == "setup":
            models.loc["sulfide","option"] = setup.loc[run,"sulfide"]
        if models.loc["sulfate","option"] == "setup":
            models.loc["sulfate","option"] = setup.loc[run,"sulfate"]
        if models.loc["hydrogen sulfide","option"] == "setup":
            models.loc["hydrogen sulfide","option"] = setup.loc[run,"hydrogen sulfide"]
        if models.loc["methane","option"] == "setup":
            models.loc["methane","option"] = setup.loc[run,"methane"]
        if models.loc["carbon monoxide","option"] == "setup":
            models.loc["carbon monoxide","option"] = setup.loc[run,"carbon monoxide"]
        if models.loc["species X solubility","option"] == "setup":
            models.loc["species X solubility","option"] = setup.loc[run,"species X solubility"]
        if models.loc["Cspeccomp","option"] == "setup":
            models.loc["Cspeccomp","option"] = setup.loc[run,"Cspeccomp"]
        if models.loc["Hspeccomp","option"] == "setup":
            models.loc["Hspeccomp","option"] = setup.loc[run,"Hspeccomp"]
        # saturation conditions
        if models.loc["SCSS","option"] == "setup":
            models.loc["SCSS","option"] = setup.loc[run,"SCSS"]
        if models.loc["SCAS","option"] == "setup":
            models.loc["SCAS","option"] = setup.loc[run,"SCAS"]
        if models.loc["sulfur_saturation","option"] == "setup":
            models.loc["sulfur_saturation","option"] = setup.loc[run,"sulfur_saturation"]
        if models.loc["sulfur_is_sat","option"] == "setup":
            models.loc["sulfur_is_sat","option"] = setup.loc[run,"sulfur_is_sat"]
        if models.loc["graphite_saturation","option"] == "setup":
            models.loc["graphite_saturation","option"] = setup.loc[run,"graphite_saturation"]
        # fugacity coefficients
        if models.loc["ideal_gas","option"] == "setup":
            models.loc["ideal_gas","option"] = setup.loc[run,"ideal_gas"]
        if models.loc["y_CO2","option"] == "setup":
            models.loc["y_CO2","option"] = setup.loc[run,"y_CO2","option"]
        if models.loc["y_SO2","option"] == "setup":
            models.loc["y_SO2","option"] = setup.loc[run,"y_SO2","option"]
        if models.loc["y_H2S","option"] == "setup":
            models.loc["y_H2S","option"] = setup.loc[run,"y_H2S","option"]
        if models.loc["y_H2","option"] == "setup":
            models.loc["y_H2","option"] = setup.loc[run,"y_H2","option"]
        if models.loc["y_O2","option"] == "setup":
            models.loc["y_O2","option"] = setup.loc[run,"y_O2","option"]
        if models.loc["y_S2","option"] == "setup":
            models.loc["y_S2","option"] = setup.loc[run,"y_S2","option"]
        if models.loc["y_CO","option"] == "setup":
            models.loc["y_CO","option"] = setup.loc[run,"y_CO","option"]
        if models.loc["y_CH4","option"] == "setup":
            models.loc["y_CH4","option"] = setup.loc[run,"y_CH4","option"]
        if models.loc["y_H2O","option"] == "setup":
            models.loc["y_H2O","option"] = setup.loc[run,"y_H2O","option"]
        if models.loc["y_OCS","option"] == "setup":
            models.loc["y_OCS","option"] = setup.loc[run,"y_OCS","option"]
        if models.loc["y_X","option"] == "setup":
            models.loc["y_X","option"] = setup.loc[run,"y_X","option"]
        # equilibrium constants
        if models.loc["KHOg","option"] == "setup":
            models.loc["KHOg","option"] = setup.loc[run,"KHOg","option"]
        if models.loc["KHOSg","option"] == "setup":
            models.loc["KHOSg","option"] = setup.loc[run,"KHOSg","option"]
        if models.loc["KOSg","option"] == "setup":
            models.loc["KOSg","option"], = setup.loc[run,"KOSg","option"]
        if models.loc["KOSg2","option"] == "setup":
            models.loc["KOSg2","option"] = setup.loc[run,"KOSg2","option"]
        if models.loc["KCOg","option"] == "setup":
            models.loc["KCOg","option"] = setup.loc[run,"KCOg","option"]
        if models.loc["KCOHg","option"] == "setup":
            models.loc["KCOHg","option"] = setup.loc[run,"KCOHg","option"]
        if models.loc["KOCSg","option"] == "setup":
            models.loc["KOCSg","option"] = setup.loc[run,"KOCSg","option"]
        if models.loc["KCOs","option"] == "setup":
            models.loc["KCOs","option"] = setup.loc[run,"KCOs","option"]
        if models.loc["carbonylsulfide","option"] == "setup":
            models.loc["carbonylsulfide","option"] = setup.loc[run,"carbonylsulfide","option"]
        # other
        if models.loc["density","option"] == "setup":
            models.loc["density","option"] = setup.loc[run,"density","option"]
        return models

##################################################
### calculate the pressure of vapor saturation ###
##################################################
def calc_Pvsat(setup,models=mdv.default_models,first_row=0,last_row=None,p_tol=1.e-1,nr_step=1.,nr_tol=1.e-9):
    
    """ 
    Calculates the pressure of vapor saturation for multiple melt compositions given volatile-free melt composition, volatile content, temperature, and an fO2 estimate.


    Parameters
    ----------
    setup: pandas.DataFrame
        Dataframe with melt compositions to be used, requires following headers: 
        Sample, T_C, 
        DNNO or DFMQ or logfO2 or (Fe2O3 and FeO) or Fe3FeT or S6ST
        SiO2, TiO2, Al2O3, (Fe2O3T or FeOT unless Fe2O3 and FeO given), MnO, MgO, CaO, Na2O, K2O, P2O5, 
        H2O and/or CO2ppm and/or STppm and/or Xppm
        Note: concentrations (unless otherwise stated) are in wt%
    
    Optional:
    models: pandas.DataFrame
        Dataframe of options for different models.
    first_row: float
        Integer of the first row in the setup file to run (note the first row under the headers is row 0). Default = 0  
    last_row: float
        Integer of the last row in the setup file to run (note the first row under the headers is row 0). Default = length of setup
    p_tol: float
        Required tolerance for convergence of Pvsat in bars. Default = 1.e-1
    nr_step: float
        Step size for Newton-Raphson solver for melt speciation (this can be made smaller if there are problems with convergence.). Default = 1
    nr_tol: float
        Tolerance for the Newton-Raphson solver for melt speciation in weight fraction (this can be made larger if there are problems with convergence). Default = 1.e-9

    Returns
    -------
    results: pandas.DataFrame

    Outputs
    -------
    results_saturation_pressures: csv file (if output csv = yes in models)

    """
    if last_row == None:
        last_row = len(setup)

    for n in range(first_row,last_row,1): # n is number of rows of data in conditions file
        run = n
        PT={"T":setup.loc[run,"T_C"]}
        melt_wf=mg.melt_comp(run,setup)
        melt_wf['CO2'] = setup.loc[run,"CO2ppm"]/1000000.
        melt_wf["H2OT"] = setup.loc[run,"H2O"]/100.
        if "sulf_XFe" in setup:
            melt_wf["sulf_XFe"] = setup.loc[run,"sulf_XFe"]
        if "sulf_XCu" in setup:
            melt_wf["sulf_XCu"] = setup.loc[run,"sulf_XCu"]
        if "sulf_XNi" in setup:
            melt_wf["sulf_XNi"] = setup.loc[run,"sulf_XNi"]

        # check if any options need to be read from the setup file rather than the models file
        models = options_from_setup(run,models,setup)
 
        # calculate Pvsat assuming only H2O CO2 in vapour and melt
        #if setup.loc[run,"Fe3FeT"] > 0.:
        #    melt_wf['Fe3FeT'] = setup.loc[run,"Fe3FeT"]
        #else:
        #    melt_wf['Fe3FeT'] = 0.
        P_sat_H2O_CO2_only, P_sat_H2O_CO2_result = c.P_sat_H2O_CO2(PT,melt_wf,models,p_tol,nr_step,nr_tol)

        if models.loc["calc_sat","option"] == "fO2_fX":
            P_sat_fO2_fS2_result = c.P_sat_fO2_fS2(PT,melt_wf,models,p_tol)
            PT["P"] = P_sat_fO2_fS2_result["P_tot"]
        else:
            wm_ST = setup.loc[run,"STppm"]/1000000.
        melt_wf['ST'] = wm_ST
        melt_wf['CT'] = (melt_wf['CO2']/mdv.species.loc['CO2','M'])*mdv.species.loc['C','M']
        melt_wf['HT'] = (melt_wf['H2OT']/mdv.species.loc['H2O','M'])*(2.*mdv.species.loc['H','M'])
        wm_X = setup.loc[run,"Xppm"]/1000000.
        melt_wf['XT'] = wm_X
        if models.loc["bulk_composition","option"] == "melt-only":
            bulk_wf = {"H":(2.*mdv.species.loc["H","M"]*melt_wf["H2OT"])/mdv.species.loc["H2O","M"],"C":(mdv.species.loc["C","M"]*melt_wf["CO2"])/mdv.species.loc["CO2","M"],"S":wm_ST, "X":wm_X}
        else:
            raise TypeError('This is not currently possible')
        if models.loc["sulfur_is_sat","option"] == "yes":
            if melt_wf["XT"] > 0.:
                raise TypeError('This is not currently possible')
            P_sat_, conc, frac  = c.fO2_P_VSA(PT,melt_wf,models,nr_step,nr_tol,p_tol)
        elif models.loc["sulfur_saturation","option"] == "False":
            P_sat_, conc, frac = c.P_sat(PT,melt_wf,models,p_tol,nr_step,nr_tol)
        elif models.loc["sulfur_saturation","option"] == "True":
            if melt_wf["XT"] > 0.:
                raise TypeError('This is not currently possible')
            P_sat_, conc, frac = c.P_VSA(PT,melt_wf,models,nr_step,nr_tol,p_tol)
        PT["P"] = P_sat_
        melt_wf["H2OT"] = conc["wm_H2O"]
        melt_wf["CO2"] = conc["wm_CO2"]
        melt_wf["S2-"] = conc["wm_S2m"]
        melt_wf["Fe3FeT"] = conc["Fe3FeT"]
        #if models.loc["sulfur_is_sat","option"] == "yes":
        #    melt_wf["Fe3FeT"] = frac["Fe3FeT"]
        #else:
        #    melt_wf["Fe3FeT"] = mg.Fe3FeT_i(PT,melt_wf,models)
        
        sulf_sat_result = c.sulfur_saturation(PT,melt_wf,models)
        # gas_mf = {"O2":mg.xg_O2(PT,melt_wf,models),"CO":mg.xg_CO(PT,melt_wf,models),"CO2":mg.xg_CO2(PT,melt_wf,models),"H2":mg.xg_H2(PT,melt_wf,models),"H2O":mg.xg_H2O(PT,melt_wf,models),"CH4":mg.xg_CH4(PT,melt_wf,models),"S2":mg.xg_S2(PT,melt_wf,models),"SO2":mg.xg_SO2(PT,melt_wf,models),"H2S":mg.xg_H2S(PT,melt_wf,models),"OCS":mg.xg_OCS(PT,melt_wf,models),"X":mg.xg_X(PT,melt_wf,models),"Xg_t":mg.Xg_tot(PT,melt_wf,models),"wt_g":0.}     
        melt_comp = mg.melt_normalise_wf(melt_wf,"yes","no")  
        
        # create results
        results_headers_table_sample_name, results_values_table_sample_name = results_table_sample_name(setup,run)
        results_headers_table_melt_comp_etc, results_values_table_melt_comp_etc = results_table_melt_comp_etc(PT,melt_comp,conc,frac,melt_wf)
        results_headers_table_model_options, results_values_table_model_options = results_table_model_options(models)    
        results_headers_table_f_p_xg_y_M_C_K_d, results_values_table_f_p_xg_y_M_C_K_d = results_table_f_p_xg_y_M_C_K_d(PT,melt_wf,models)
        results_headers_table_sat, results_values_table_sat = results_table_sat(sulf_sat_result,PT,melt_wf,models)
        results_headers_table_melt_vol = results_table_melt_vol() # "H2OT-eq_wtpc","CO2T-eq_ppmw","ST_ppmw","X_ppmw"
        results_values_table_melt_vol = pd.DataFrame([[setup.loc[run,"H2O"],setup.loc[run,"CO2ppm"],setup.loc[run,"STppm"],setup.loc[run,"Xppm"]]])
        results_headers_table_H2OCO2only = pd.DataFrame([["Pvsat (H2O CO2 only)", "xg_H2O (H2O CO2 only)", "xg_CO2 (H2O CO2 only)","f_H2O (H2O CO2 only)", "f_CO2 (H2O CO2 only)","p_H2O (H2O CO2 only)", "p_CO2 (H2O CO2 only)", "Pvsat_diff_bar"]])
        results_values_table_H2OCO2only = pd.DataFrame([[P_sat_H2O_CO2_only, P_sat_H2O_CO2_result["xg_H2O"], P_sat_H2O_CO2_result["xg_CO2"], P_sat_H2O_CO2_result["f_H2O"], P_sat_H2O_CO2_result["f_CO2"], P_sat_H2O_CO2_result["p_H2O"], P_sat_H2O_CO2_result["p_CO2"], (P_sat_H2O_CO2_only-PT["P"])]])
        results_headers = pd.concat([results_headers_table_sample_name,results_headers_table_melt_comp_etc,results_headers_table_melt_vol,results_headers_table_sat,results_headers_table_H2OCO2only,results_headers_table_f_p_xg_y_M_C_K_d,results_headers_table_model_options],axis=1)
        results1 = pd.concat([results_values_table_sample_name,results_values_table_melt_comp_etc,results_values_table_melt_vol,results_values_table_sat,results_values_table_H2OCO2only,results_values_table_f_p_xg_y_M_C_K_d,results_values_table_model_options],axis=1)
    
        if n == first_row:
            results = pd.concat([results_headers, results1])
        else:                         
            results = pd.concat([results, results1])
        
        if models.loc["print status","option"] == "True":
            print(n, setup.loc[run,"Sample"],PT["P"])
    
    results.columns = results.iloc[0]
    results = results[1:]  
    if models.loc["output csv","option"] == "True":
        results.to_csv('results_saturation_pressures.csv', index=False, header=True)
    
    return results

###################################
### cacluate re/degassing paths ###
###################################
def calc_gassing(setup,models=mdv.default_models,run=0,nr_step=1.,nr_tol=1.e-9,dp_step="auto",psat_tol=0.1,dwtg=1.e-6,i_nr_step=1.e-1,i_nr_tol=1.-9,nr_step_eq=1.):
     
    """ 
    Calculates the pressure of vapor saturation for multiple melt compositions given volatile-free melt composition, volatile content, temperature, and an fO2 estimate.


    Parameters
    ----------
    setup: pandas.DataFrame
        Dataframe with melt composition to be used, requires following headers (notes in [] are not part of the headers): 
        Sample, T_C, 
        DNNO or DFMQ or logfO2 or (Fe2O3 and FeO) or Fe3FeT or S6ST, [at initial pressure]
        SiO2, TiO2, Al2O3, (Fe2O3T or FeOT unless Fe2O3 and FeO given), MnO, MgO, CaO, Na2O, K2O, P2O5, [concentrations are in wt%]
        (H2O and/or CO2ppm and/or STppm and/or Xppm) [concentration of H2O in wt%]
        P_bar [IF starting from a given pressure]
        final_P [IF regassing, pressure calculation stops at in bars]
        wt_g [IF starting from given pressure and gas is present, can specifiy the gas present in wt%]
        initial_CO2wtpc [IF starting from given pressure and gas is present, can specifiy initial composition using initial CO2 dissolved in the melt in wt%]
        xg_O2, xg_CO, xg_H2, xg_S2, xg_X [IF starting from a given pressure, need initial guesses for mole fraction of gas species]
    species: pandas.DataFrame
        Dataframe of species.csv file.
    models: pandas.DataFrame
        Dataframe of models.csv file.

    Optional:
    run: float
        Integer of the row in the setup file to run (note the first row under the headers is row 0). Default = 0
    nr_step: float
        Step size for Newton-Raphson solver for melt speciation (typically 1 is fine, but this can be made smaller if there are problems with convergence).
    nr_tol: float
        Tolerance for the Newton-Raphson solver for melt speciation in weight fraction (can be increased if there are problems with convergence). Default = 1.e-6
    dp_step: float
        Pressure step size for gassing calculation in bars. Default = 10    
    psat_tol: float
        Required tolerance for convergence of Pvsat in bars. Default = 0.1
    dwtg: float
        Amount of gas to add at each step if regassing in an open-system in wt fraction total system. Default = 1.e-7
    i_nr_step: float
        Step-size for newton-raphson convergence for isotopes (can be increased if there are problems with convergence). Default = 1e.-1
    i_nr_tol: float
        Tolerance for newton-raphson convergence for isotopes (can be increased if there are problems with convergence). Default = 1.e-9

    Returns
    -------
    results: pandas.DataFrame

    Outputs
    -------
    If output csv = yes in models
    results_gassing_chemistry: csv file

    """

    if models.loc["print status","option"] == "True":
        print(setup.loc[run,"Sample"])

    # check if any options need to be read from the setup file rather than the models file
    models = options_from_setup(run,models,setup)

    if models.loc["fO2","option"] != "Kress91A":
        raise TypeError("Change 'fO2' option in models to 'Kress91A' (other fO2 options are not currently supported)")

    # set T, volatile composition of the melt, and tolerances
    PT={"T":setup.loc[run,"T_C"]}
    melt_wf = mg.melt_comp(run,setup)
    melt_wf['CO2'] = setup.loc[run,"CO2ppm"]/1000000.
    melt_wf["H2OT"] = setup.loc[run,"H2O"]/100.
    melt_wf["ST"] = setup.loc[run,"STppm"]/1000000.
    melt_wf["H2"] = 0.
    melt_wf["XT"] = setup.loc[run,"Xppm"]/1000000.
    melt_wf["CT"] = (melt_wf["CO2"]/mdv.species.loc["CO2","M"])*mdv.species.loc["C","M"]
    melt_wf["HT"] = (2.*melt_wf["H2OT"]/mdv.species.loc["H2O","M"])*mdv.species.loc["H","M"]
    melt_wf["ST"] = melt_wf["ST"]
    if "S6ST" in setup:
        melt_wf["S6ST"] = setup.loc[run,"S6ST"]
    if "sulf_XFe" in setup:
        melt_wf["sulf_XFe"] = setup.loc[run,"sulf_XFe"]
    if "sulf_XCu" in setup:
        melt_wf["sulf_XCu"] = setup.loc[run,"sulf_XCu"]
    if "sulf_XNi" in setup:
        melt_wf["sulf_XNi"] = setup.loc[run,"sulf_XNi"]

    # Calculate saturation pressure for composition given in setup file
    if models.loc["COH_species","option"] == "H2O-CO2 only":  
        P_sat_, P_sat_H2O_CO2_result = c.P_sat_H2O_CO2(PT,melt_wf,models,psat_tol,nr_step,nr_tol)
        conc = {"wm_H2O":P_sat_H2O_CO2_result["wm_H2O"], "wm_CO2":P_sat_H2O_CO2_result["wm_CO2"], "wm_H2":0., "wm_CO":0., "wm_CH4":0., "wm_H2S":0., "wm_S2m":0., "wm_S6p":0., "ST": 0.}
        frac = c.melt_species_ratios(conc)
    else:
        P_sat_, conc, frac = c.P_sat(PT,melt_wf,models,psat_tol,nr_step,nr_tol)
    PT["P"] = P_sat_
    if models.loc["print status","option"] == "True":
        print("T=",PT["T"],"P=",PT["P"],datetime.datetime.now())

    # update melt composition at saturation pressure, check for sulfur saturation, and calculate some things
    melt_wf["H2OT"] = conc["wm_H2O"]
    melt_wf["CO2"] = conc["wm_CO2"]
    melt_wf["CO"] = conc["wm_CO"]
    melt_wf["CH4"] = conc["wm_CH4"]
    melt_wf["H2"] = conc["wm_H2"]
    melt_wf["S2-"] = conc["wm_S2m"]
    melt_wf["S6+"] = conc["wm_S6p"]
    melt_wf["H2S"] = conc["wm_H2S"]
    melt_wf["Fe3FeT"] = conc['Fe3FeT']
    melt_wf["S6ST"] = mg.S6ST(PT,melt_wf,models)
    sulf_sat_result = c.sulfur_saturation(PT,melt_wf,models)    
    wm_CO2eq, wm_H2Oeq = mg.melt_H2O_CO2_eq(melt_wf)
    melt_comp = mg.melt_normalise_wf(melt_wf,"yes","no")
    
    # Set bulk composition
    bulk_comp = c.bulk_composition(run,PT,melt_wf,setup,models)
    bulk_wf = {"C":bulk_comp["wt_C"],"H":bulk_comp["wt_H"],"O":bulk_comp["wt_O"],"S":bulk_comp["wt_S"],"Fe":bulk_comp["wt_Fe"],"Wt":bulk_comp["Wt"],"X":bulk_comp["wt_X"]}

    # set system and initial guesses
    system = eq.set_system(melt_wf,models)
    guesses = eq.initial_guesses(run,PT,melt_wf,setup,models,system)

    # create results
    results_headers_table_sample_name, results_values_table_sample_name = results_table_sample_name(setup,run)
    results_headers_table_melt_comp_etc, results_values_table_melt_comp_etc = results_table_melt_comp_etc(PT,melt_comp,conc,frac,melt_wf)
    results_headers_table_model_options, results_values_table_model_options = results_table_model_options(models)    
    results_headers_table_f_p_xg_y_M_C_K_d, results_values_table_f_p_xg_y_M_C_K_d = results_table_f_p_xg_y_M_C_K_d(PT,melt_wf,models)
    results_headers_table_sat, results_values_table_sat = results_table_sat(sulf_sat_result,PT,melt_wf,models)
    results_headers_table_melt_vol = results_table_melt_vol() # "H2OT-eq_wtpc","CO2T-eq_ppmw","ST_ppmw","X_ppmw"
    results_values_table_melt_vol = pd.DataFrame([[wm_H2Oeq*100.,wm_CO2eq*1000000.,conc["wm_ST"]*1000000.,melt_wf["XT"]*1000000.]])
    results_headers_table_wtg_etc = pd.DataFrame([["wt_g_wtpc","wt_g_O_wtf","wt_g_C_wtf","wt_g_H_wtf","wt_g_S_wtf","wt_g_X_wtf","wt_O_wtpc","wt_C_wtpc","wt_H_wtpc","wt_S_wtpc","wt_X_wtpc","Solving species",'mass balance C','mass balance O','mass balance H','mass balance S']])
    results_values_table_wtg_etc = pd.DataFrame([[bulk_comp["wt_g"]*100.,"","","","","",bulk_wf["O"]*100.,bulk_wf["C"]*100.,bulk_wf["H"]*100.,bulk_wf["S"]*100.,bulk_wf["X"]*100.,"","","","",""]])
    if models.loc["gassing_style","option"] == "open" and models.loc["gassing_direction","option"] == "degas":
        results_headers_table_open_all_gas = results_table_open_all_gas()
        results_values_table_open_all_gas = pd.DataFrame([[mg.xg_O2(PT,melt_wf,models),mg.xg_H2(PT,melt_wf,models),mg.xg_H2O(PT,melt_wf,models),mg.xg_S2(PT,melt_wf,models),mg.xg_SO2(PT,melt_wf,models),mg.xg_H2S(PT,melt_wf,models),mg.xg_CO2(PT,melt_wf,models),mg.xg_CO(PT,melt_wf,models),mg.xg_CH4(PT,melt_wf,models),mg.xg_OCS(PT,melt_wf,models),mg.xg_X(PT,melt_wf,models),mg.gas_CS(PT,melt_wf,models)]])
        results_headers = pd.concat([results_headers_table_sample_name,results_headers_table_melt_comp_etc,results_headers_table_melt_vol,results_headers_table_sat,results_headers_table_f_p_xg_y_M_C_K_d,results_headers_table_wtg_etc,results_headers_table_open_all_gas,results_headers_table_model_options],axis=1)
        results1 = pd.concat([results_values_table_sample_name,results_values_table_melt_comp_etc,results_values_table_melt_vol,results_values_table_sat,results_values_table_f_p_xg_y_M_C_K_d,results_values_table_wtg_etc,results_values_table_open_all_gas,results_values_table_model_options],axis=1)
    else:    
        results_headers = pd.concat([results_headers_table_sample_name,results_headers_table_melt_comp_etc,results_headers_table_melt_vol,results_headers_table_sat,results_headers_table_f_p_xg_y_M_C_K_d,results_headers_table_wtg_etc,results_headers_table_model_options],axis=1)
        results1 = pd.concat([results_values_table_sample_name,results_values_table_melt_comp_etc,results_values_table_melt_vol,results_values_table_sat,results_values_table_f_p_xg_y_M_C_K_d,results_values_table_wtg_etc,results_values_table_model_options],axis=1)
    results = pd.concat([results_headers, results1])
    
    # results for isotope calculations...
    if models.loc["isotopes","option"] == "yes":
        raise TypeError("This is not currently supported")
        a_H2S_S_,a_SO4_S_,a_S2_S_,a_SO2_S_,a_OCS_S_ = iso.i2s6_S_alphas(PT)
        results_isotopes1 = pd.DataFrame([["P","T_C","xg_O2","xg_CO","xg_CO2","xg_H2","xg_H2O","xg_CH4","xg_S2","xg_SO2","xg_SO3","xg_H2S","xg_OCS","wt_g",
                        "wm_CO2","wm_H2O","wm_H2","wm_S","wm_SO3","wm_ST","Fe3T","S6T",
                         "DFMQ","DNNO","SCSS","sulfide sat?","SCAS","sulfate sat?",
                         "RS_S2-","RS_SO42-","RS_H2S","RS_SO2","RS_S2","R_OCS","R_m","R_g",
                         "dS_S2-","dS_SO42-","dS_H2S","dS_SO2","dS_S2","dS_OCS","dS_m","dS_g",
                         "a_H2S_S2-","a_SO42-_S2-","a_S2_S2-","a_SO2_S2-","a_OCS_S2-","a_g_m"]])
        results_isotopes = results_header.append(results_isotopes1, ignore_index=True)
        results1 = pd.DataFrame([[PT["P"],PT["T"],mg.xg_O2(PT,melt_wf,models),mg.xg_CO(PT,melt_wf,models),mg.xg_CO2(PT,melt_wf,models),mg.xg_H2(PT,melt_wf,models),mg.xg_H2O(PT,melt_wf,models),mg.xg_CH4(PT,melt_wf,models),mg.xg_S2(PT,melt_wf,models),mg.xg_SO2(PT,melt_wf,models),mg.xg_H2S(PT,melt_wf,models),mg.xg_OCS(PT,melt_wf,models),wt_g_,
melt_wf["CO2"],melt_wf["H2OT"],0,(mg.wm_S(PT,melt_wf,models)/100),(mg.wm_SO3(PT,melt_wf,models)/100),melt_wf["ST"],melt_wf["Fe3FeT"],mg.S6ST(PT,melt_wf,models),
mg.fO22Dbuffer(PT,mdv.f_O2(PT,melt_wf,models),"FMQ"),mg.fO22Dbuffer(PT,mdv.f_O2(PT,melt_wf,models),"NNO"),SCSS_,sulfide_sat,SCAS_,sulfate_sat,
R_S_S2_,R_S_SO4_,"","","","",R_i["S"],"",ratio2delta("VCDT",R_S_S2_),ratio2delta("VCDT",R_S_SO4_),"","","","",ratio2delta("VCDT",R_i["S"]),"",
a_H2S_S_,a_SO4_S_,a_S2_S_,a_SO2_S_,a_OCS_S_,""]])
        results_isotopes = pd.concat([results_isotopes, results1], ignore_index=True) 
        if models.loc["output csv","option"] == "True":
            results_isotopes.to_csv('results_gassing_isotopes.csv', index=False, header=False)
    
    if dp_step == "auto":
        dp_step_choice = "auto"
        if models.loc["gassing_style","option"] == "open":
            dp_step = 1.
        else:
            if PT["P"] > 5000.:
                dp_step = 500.
            elif PT["P"] > 200.:
                dp_step = 100.
            elif PT["P"] > 50.:
                dp_step = 10.
            else:
                dp_step = 1.
    else:
        dp_step_choice = "user"

    if models.loc["P_variation","option"] == "polybaric":
        # pressure ranges and options
        starting_P = models.loc["starting_P","option"]
        if starting_P == "set":
            initial = int(setup.loc[run,"P_bar"])
        else:
            if models.loc["gassing_direction","option"] == "degas":
                answer = PT["P"]/dp_step
                answer = round(answer)
                initial = round(answer*dp_step)
            elif models.loc["gassing_direction","option"] == "regas":
                answer = PT["P"]/dp_step
                answer = round(answer)
                answer = round(answer*dp_step)
                initial = round(answer+dp_step)
        if models.loc["gassing_direction","option"] == "degas":
            #step = int(-1*dp_step) # pressure step in bars
            final = 0
        elif models.loc["gassing_direction","option"] == "regas":
            #step = int(dp_step)
            final = int(setup.loc[run,"final_P"])
    elif models.loc["T_variation","option"] == "polythermal": # temperature ranges and options
        PT["P"] = setup.loc[run,"P_bar"]
        final = int(setup.loc[run,"final_T"])
        if setup.loc[run,"final_T"] > setup.loc[run,"T_C"]:
            initial = int(round(PT["T"])) 
            #step = int(dp_step) # temperature step in 'C
        elif setup.loc[run,"final_T"] < setup.loc[run,"T_C"]:
            initial = int(round(PT["T"]))
            #step = int(-1.*dp_step) # temperature step in 'C
    
    # add some gas to the system if doing open-system regassing
    if models.loc["gassing_direction","option"] == "regas" and models.loc["gassing_style","option"] == "open":
        gas_mf = {"O2":mg.xg_O2(PT,melt_wf,models),"CO":mg.xg_CO(PT,melt_wf,models),"CO2":mg.xg_CO2(PT,melt_wf,models),"H2":mg.xg_H2(PT,melt_wf,models),"H2O":mg.xg_H2O(PT,melt_wf,models),"CH4":mg.xg_CH4(PT,melt_wf,models),"S2":mg.xg_S2(PT,melt_wf,models),"SO2":mg.xg_SO2(PT,melt_wf,models),"H2S":mg.xg_H2S(PT,melt_wf,models),"OCS":mg.xg_OCS(PT,melt_wf,models),"X":mg.xg_X(PT,melt_wf,models),"Xg_t":mg.Xg_tot(PT,melt_wf,models),"wt_g":0.}
        new_comp = c.new_bulk_regas_open(PT,melt_wf,bulk_wf,gas_mf,dwtg,models)
        bulk_wf = {"C":new_comp['wt_C'],"H":new_comp['wt_H'],"O":new_comp['wt_O'],"S":new_comp['wt_S'],"Fe":new_comp['wt_Fe'],"X":new_comp['wt_X'],"Wt":new_comp['Wt']}
    
    # run over different pressures #
    number_of_step = 0.
    
    PT['P'] = initial
    while PT["P"] > 1.:
    #for i in range(initial,final,step): # P is pressure in bars or T is temperature in 'C
        number_of_step = number_of_step + 1.
        eq_Fe = models.loc["eq_Fe","option"]
        guesses_original = guesses # store original guesses in case the calculation needs to be restarted

        if dp_step_choice == "auto":
            if models.loc["gassing_style","option"] == "open":
                dp_step = 1.
            else:
                if PT["P"] > 5000.:
                    dp_step = 500.
                elif PT["P"] > 200.:
                    dp_step = 100.
                elif PT["P"] > 50.:
                    dp_step = 10.
                else:
                    dp_step = 1.
        
        if models.loc["P_variation","option"] == "polybaric": 
            #P = i - dp_step
            P = PT["P"] - dp_step
            if P < dp_step or P < 1.:
                P = 1.
            PT["P"] = P
        elif models.loc["T_variation","option"] == "polythermal":
            T = i - dp_step
            PT["T"] = T
        
        if models.loc["gassing_style","option"] == "open": # check melt is still vapor-saturated
            PT_ = {'P':PT['P'],'T':PT['T']}
            if models.loc["COH_species","option"] == "H2O-CO2 only":  
                P_sat_, P_sat_H2O_CO2_result = c.P_sat_H2O_CO2(PT_,melt_wf,models,psat_tol,nr_step,nr_tol)
                conc = {"wm_H2O":P_sat_H2O_CO2_result["wm_H2O"], "wm_CO2":P_sat_H2O_CO2_result["wm_CO2"], "wm_H2":0., "wm_CO":0., "wm_CH4":0., "wm_H2S":0., "wm_S2m":0., "wm_S6p":0., "ST": 0.}
                frac = c.melt_species_ratios(conc)
            else:
                P_sat_, conc, frac = c.P_sat(PT_,melt_wf,models,psat_tol,nr_step,nr_tol)
            checkingP = PT['P']
            while P_sat_ < checkingP:
                checkingP = checkingP - dp_step
                PT_['P'] = checkingP
                if models.loc["COH_species","option"] == "H2O-CO2 only":  
                    P_sat_, P_sat_H2O_CO2_result = c.P_sat_H2O_CO2(PT_,melt_wf,models,psat_tol,nr_step,nr_tol)
                    conc = {"wm_H2O":P_sat_H2O_CO2_result["wm_H2O"], "wm_CO2":P_sat_H2O_CO2_result["wm_CO2"], "wm_H2":0., "wm_CO":0., "wm_CH4":0., "wm_H2S":0., "wm_S2m":0., "wm_S6p":0., "ST": 0.}
                    frac = c.melt_species_ratios(conc)
                else:
                    P_sat_, conc, frac = c.P_sat(PT_,melt_wf,models,psat_tol,nr_step,nr_tol)
            PT['P'] = checkingP
    
        if P_sat_ > PT["P"] or models.loc["gassing_direction","option"] == "regas":  
            # work out equilibrium partitioning between melt and gas phase
            xg, conc, melt_and_gas, guesses, new_models, solve_species, mass_balance = eq.mg_equilibrium(PT,melt_wf,bulk_wf,models,nr_step_eq,nr_tol,guesses)
            models = new_models
            if xg["xg_O2"] == 1.0:
                print('tried resetting guesses')
                guesses = eq.initial_guesses(run,PT,melt_wf,setup,models,system)
                xg, conc, melt_and_gas, guesses, new_models, solve_species, mass_balance = eq.mg_equilibrium(PT,melt_wf,bulk_wf,models,nr_step_eq,nr_tol,guesses)
                models = new_models
            if models.loc["gassing_style","option"] == "closed":
                if xg["xg_O2"] == 1.0:
                    guesses = guesses_original
                    oldP = P + dp_step
                    if dp_step < 1. or dp_step == 1.:
                        print('solver failed, increasing step size by factor 10')
                        dp_step = dp_step*10.
                    else:
                        print('solver failed, decreasing step size by factor 10')
                        dp_step = dp_step/10.
                    newP = oldP - dp_step
                    if newP < 1.:
                        newP = 1.
                    PT["P"] = newP
                    xg, conc, melt_and_gas, guesses, new_models, solve_species, mass_balance = eq.mg_equilibrium(PT,melt_wf,bulk_wf,models,nr_step_eq,nr_tol,guesses)
                    models = new_models
            if xg["xg_O2"] == 1.0:
                results.columns = results.iloc[0]
                results = results[1:]  
                results.reset_index(drop=True,inplace=True)
                if models.loc["output csv","option"] == "True":
                    results.to_csv('results_gassing_chemistry.csv', index=False, header=True)
                print("solver failed, calculation aborted at P = ", PT["P"], datetime.datetime.now())
                return results
            # gas composition
            gas_mf = {"O2":xg["xg_O2"],"CO":xg["xg_CO"],"S2":xg["xg_S2"],"CO2":xg["xg_CO2"],"H2O":xg["xg_H2O"],"H2":xg["xg_H2"],"CH4":xg["xg_CH4"],"SO2":xg["xg_SO2"],"H2S":xg["xg_H2S"],"OCS":xg["xg_OCS"],"X":xg["xg_X"],"Xg_t":xg["Xg_t"],"wt_g":melt_and_gas["wt_g"]}
        #else: # NEEDS SORTING ###
            #conc = eq.melt_speciation(PT,melt_wf,models,nr_step,nr_tol)
            #frac = c.melt_species_ratios(conc)
            #wm_ST_ = wm_S_ + wm_S6p_
            #S62 = S6T/S2m_ST
            #Fe3T = melt_wf["Fe3FeT"]
            #Fe32 = mg.overtotal2ratio(Fe3T)
            #xg = {"xg_O2":0., "xg_H2":0., "xg_S2":0., "xg_H2O":0., "xg_CO":0., "xg_CO2":0., "xg_SO2":0., "xg_CH4":0., "xg_H2S":0., "xg_OCS":0., "xg_X":0., "Xg_t":0.}
            #if number_of_step == 1:
            #    melt_and_gas = {}
            #melt_and_gas["wt_g_O"],melt_and_gas["wt_g_C"],melt_and_gas["wt_g_H"],melt_and_gas["wt_g_S"],melt_and_gas["wt_g_X"],melt_and_gas["wt_g"] = 0.,0.,0.,0.,0.
            #guesses = eq.initial_guesses(run,PT,melt_wf,setup,models,system)
            #solve_species = "na"
            #gas_mf = {"O2":xg["xg_O2"],"CO":xg["xg_CO"],"S2":xg["xg_S2"],"CO2":xg["xg_CO2"],"H2O":xg["xg_H2O"],"H2":xg["xg_H2"],"CH4":xg["xg_CH4"],"SO2":xg["xg_SO2"],"H2S":xg["xg_H2S"],"OCS":xg["xg_OCS"],"X":xg["xg_X"],"Xg_t":xg["Xg_t"],"wt_g":melt_and_gas["wt_g"]}
        
        if P_sat_ > PT["P"] or models.loc["gassing_direction","option"] == "regas": 
            if models.loc["gassing_style","option"] == "open" and models.loc["gassing_direction","option"] == "degas": 
                if number_of_step == 1:
                    gas_mf_all = gas_mf
                else:
                    gas_mf_all = c.gas_comp_all_open(gas_mf,gas_mf_all,models)
            if models.loc["COH_species","option"] == "H2O-CO2 only":
                Fe3T = melt_wf["Fe3FeT"]
                Fe32 = mg.overtotal2ratio(Fe3T)

        # set melt composition for forward calculation
        melt_wf["CO2"] = conc["wm_CO2"]
        melt_wf["H2OT"] = conc["wm_H2O"]
        melt_wf["H2"] = conc["wm_H2"]
        melt_wf["CO"] = conc["wm_CO"]
        melt_wf["CH4"] = conc["wm_CH4"]
        melt_wf["H2S"] = conc["wm_H2S"]
        melt_wf["S6+"] = (conc["wm_SO3"]/mdv.species.loc["SO3","M"])*mdv.species.loc["S","M"]
        melt_wf["S2-"] = conc["wm_S2m"]
        melt_wf["ST"] = conc["wm_ST"]
        melt_wf["XT"] = conc["wm_X"]
        melt_wf["Fe3FeT"] = conc["Fe3T"]
        if P_sat_ < PT["P"]:  
            bulk_comp = c.bulk_composition(run,PT,melt_wf,setup,models)
    
        # check for sulfur saturation and display warning in outputs
        sulf_sat_result = c.sulfur_saturation(PT,melt_wf,models)
        if sulf_sat_result["sulfide_sat"] == "yes":
            warning = "WARNING: sulfide-saturated"
        elif sulf_sat_result["sulfate_sat"] == "yes":
            warning = "WARNING: sulfate-saturated"
        else:
            warning = ""
        
        # calculate fO2
        if eq_Fe == "yes":
            fO2_ = mdv.f_O2(PT,melt_wf,models)
        elif eq_Fe == "no":
            fO2_ = (xg_O2_*mdv.y_O2(PT,models)*PT["P"])
        
        wm_CO2eq, wm_H2Oeq = mg.melt_H2O_CO2_eq(melt_wf)
        melt_comp = mg.melt_normalise_wf(melt_wf,"yes","no")
        frac = c.melt_species_ratios(conc)

        # store results
        results_headers_table_sample_name, results_values_table_sample_name = results_table_sample_name(setup,run)
        results_headers_table_melt_comp_etc, results_values_table_melt_comp_etc = results_table_melt_comp_etc(PT,melt_comp,conc,frac,melt_wf)
        results_headers_table_model_options, results_values_table_model_options = results_table_model_options(models)    
        results_headers_table_f_p_xg_y_M_C_K_d, results_values_table_f_p_xg_y_M_C_K_d = results_table_f_p_xg_y_M_C_K_d(PT,melt_wf,models)
        results_headers_table_sat, results_values_table_sat = results_table_sat(sulf_sat_result,PT,melt_wf,models)
        results_values_table_melt_vol = pd.DataFrame([[wm_H2Oeq*100.,wm_CO2eq*1000000.,conc["wm_ST"]*1000000.,melt_wf["XT"]*1000000.]])
        results_values_table_wtg_etc = pd.DataFrame([[melt_and_gas["wt_g"]*100.,melt_and_gas["wt_g_O"],melt_and_gas["wt_g_C"],melt_and_gas["wt_g_H"],melt_and_gas["wt_g_S"],melt_and_gas["wt_g_X"],melt_and_gas["wt_O"]*100.,melt_and_gas["wt_C"]*100.,melt_and_gas["wt_H"]*100.,melt_and_gas["wt_S"]*100.,melt_and_gas["wt_X"]*100.,solve_species,mass_balance['C'],mass_balance['O'],mass_balance['H'],mass_balance['S']]])
        if models.loc["gassing_style","option"] == "open" and models.loc["gassing_direction","option"] == "degas":
            results_values_table_open_all_gas = pd.DataFrame([[gas_mf_all["O2"],gas_mf_all["H2"],gas_mf_all["H2O"],gas_mf_all["S2"],gas_mf_all["SO2"],gas_mf_all["H2S"],gas_mf_all["CO2"],gas_mf_all["CO"],gas_mf_all["CH4"],gas_mf_all["OCS"],gas_mf_all["X"],mg.gas_CS_alt(gas_mf_all)]])
            results1 = pd.concat([results_values_table_sample_name,results_values_table_melt_comp_etc,results_values_table_melt_vol,results_values_table_sat,results_values_table_f_p_xg_y_M_C_K_d,results_values_table_wtg_etc,results_values_table_open_all_gas,results_values_table_model_options],axis=1)
        else:
            results1 = pd.concat([results_values_table_sample_name,results_values_table_melt_comp_etc,results_values_table_melt_vol,results_values_table_sat,results_values_table_f_p_xg_y_M_C_K_d,results_values_table_wtg_etc,results_values_table_model_options],axis=1)
        results = pd.concat([results, results1])
        
        # equilibrium isotope fractionation
        if models.loc["isotopes", "option"] == "yes":
            raise TypeError("This is not currently supported")
            if models.loc["H2S","option"] == "yes":
                print("not currently possible")
            A, B = iso.i2s6("S",PT,R_i,melt_wf,gas_mf,i_nr_step,i_nr_tol,guessx)
            RS_Sm, RS_H2S, RS_SO4, RS_S2, RS_SO2, RS_OCS = A
            RS_m, RS_g = B
            a_H2S_S_,a_SO4_S_,a_S2_S_,a_SO2_S_,a_OCS_S_ = iso.i2s6_S_alphas(PT)
            xg_SO3_ = 0.
            results2 = pd.DataFrame([[PT["P"],PT["T"],xg_O2_,xg_CO_,xg_CO2_,xg_H2_,xg_H2O_,xg_CH4_,xg_S2_,xg_SO2_,xg_SO3_,xg_H2S_,xg_OCS_,wt_g,
                        wm_CO2_,wm_H2O_,wm_H2_,wm_S_,wm_SO3_,wm_ST_,Fe3T,S6T,
                        mg.fO22Dbuffer(PT,fO2_,"FMQ"),mg.fO22Dbuffer(PT,fO2_,"NNO"),SCSS_,sulfide_sat,SCAS_,sulfate_sat,
                        RS_Sm, RS_SO4, RS_H2S, RS_SO2, RS_S2, RS_OCS, RS_m, RS_g, ratio2delta("VCDT",RS_Sm),ratio2delta("VCDT",RS_SO4),ratio2delta("VCDT",RS_H2S),ratio2delta("VCDT",RS_SO2),ratio2delta("VCDT",RS_S2),ratio2delta("VCDT",RS_OCS),ratio2delta("VCDT",RS_m),ratio2delta("VCDT",RS_g),a_H2S_S_,a_SO4_S_,a_S2_S_,a_SO2_S_,a_OCS_S_,RS_g/RS_m]])
            results_isotopes = pd.concat([results_isotopes, results2], ignore_index=True)
            if models.loc["output csv","option"] == "True":
                results_isotopes.to_csv('results_gassing_isotopes.csv', index=False, header=False)
        
        if models.loc["print status","option"] == "True":
            if(number_of_step % 100==0):
                print(PT["T"],PT["P"],mg.fO22Dbuffer(PT,fO2_,"FMQ",models),warning,datetime.datetime.now())

        # recalculate bulk composition if needed
        if models.loc["gassing_style","option"] == "open":
            results_me = mg.melt_elements(PT,melt_wf,bulk_wf,gas_mf,models)
            if models.loc["gassing_direction","option"] == "degas":
                Wt_ = bulk_wf['Wt']
                if results_me["wm_C"] < 1.e-6: # 1 ppm C
                    results_me["wm_C"] = 0.
                if results_me["wm_H"] < 1.e-6: # 1 ppm H
                    results_me["wm_H"] = 0.
                if results_me["wm_S"] < 1.e-6: # 1 ppm S
                    results_me["wm_S"] = 0.
                if results_me["wm_X"] < 1.e-6: # 1 ppm X
                    results_me["wm_X"] = 0.
                bulk_wf = {"C":results_me["wm_C"],"H":results_me["wm_H"],"O":results_me["wm_O"],"S":results_me["wm_S"],"X":results_me["wm_X"],"Fe":results_me["wm_Fe"],"Wt":(Wt_*(1. - melt_and_gas["wt_g"]))}
                melt_wf["CT"] = results_me["wm_C"]
                melt_wf["HT"] = results_me["wm_H"]
                melt_wf["ST"] = results_me["wm_S"]
                melt_wf["XT"] = results_me["wm_X"]
                system = eq.set_system(melt_wf,models)
            elif models.loc["gassing_direction","option"] == "regas":
                results_nbro = c.new_bulk_regas_open(PT,melt_wf,bulk_wf,gas_mf,dwtg,models)
                bulk_wf = {"C":results_nbro["wt_C"],"H":results_nbro["wt_H"],"O":results_nbro["wt_O"],"S":results_nbro["wt_S"],"X":results_nbro["wt_X"],"Fe":results_nbro["wt_Fe"],"Wt":results_nbro["Wt"]}
                #melt_wf["CT"] = results_nbro["wm_C"]
                #melt_wf["HT"] = results_nbro["wm_H"]
                #melt_wf["ST"] = results_nbro["wm_S"]
                #melt_wf["XT"] = results_nbro["wm_X"]
        if models.loc["crystallisation","option"] == "yes":
            wt_C_ = bulk_wf["C"]
            wt_H_ = bulk_wf["H"]
            wt_O_ = bulk_wf["O"]
            wt_S_ = bulk_wf["S"]
            wt_X_ = bulk_wf["X"]
            wt_Fe_ = bulk_wf["Fe"]
            wt_ = bulk_wf["Wt"]
            Xst = setup.loc[run,"crystallisation_pc"]/100.
            bulk_wf = {"C":wt_C_*(1./(1.-Xst)),"H":wt_H_*(1./(1.-Xst)),"O":wt_O_*(1./(1.-Xst)),"S":wt_S_*(1./(1.-Xst)),"X":wt_X_*(1./(1.-Xst)),"Fe":wt_Fe_*(1./(1.-Xst)),"Wt":wt_*(1.-Xst)}
    
    results.columns = results.iloc[0]
    results = results[1:]
    results.reset_index(drop=True,inplace=True)  
    if models.loc["output csv","option"] == "True":
        results.to_csv('results_gassing_chemistry.csv', index=False, header=True)
    
    if models.loc["print status","option"] == "True":
        print("done", datetime.datetime.now())

    return results

#########################
### calculate isobars ###
#########################
def calc_isobar(setup,run=0,models=mdv.default_models,initial_P=1000.,final_P=10000.,step_P=1000.):
    
    if models.loc["COH_species","option"] == "H2O-CO2 only":
        PT={"T":setup.loc[run,"T_C"]}
        
        # check if any options need to be read from the setup file rather than the models file
        models = options_from_setup(run,models,setup)

        # set up results table
        results = pd.DataFrame([["P_bar","H2O_wtpc","CO2_ppm"]])
    
        initial_P = int(initial_P)
        final_P = int(final_P+1)
        step_P = int(step_P)
        melt_wf=mg.melt_comp(run,setup)

        for n in range(initial_P,final_P,step_P):
            PT["P"] = n # pressure in bars
            results1 = c.calc_isobar_CO2H2O(PT,melt_wf,models)
            results = pd.concat([results, results1], ignore_index=True)
            if models.loc["print status","option"] == "True":
                print(setup.loc[run,"Sample"],n)
        results.columns = results.iloc[0]
        results = results[1:]

    else:
        raise TypeError("COH_species option must be H2O-CO2 only")
    if models.loc["output csv","option"] == "True":
        results.to_csv('results_isobars.csv', index=False, header=False)

    return results

#################################
### calculate pure solubility ###
#################################   
def calc_pure_solubility(setup,run=0,models=mdv.default_models,initial_P=5000.):
    if models.loc["print status","option"] == "True":
        print(setup.loc[run,"Sample"],initial_P)
    PT={"T":setup.loc[run,"T_C"]}

    # check if any options need to be read from the setup file rather than the models file
    models = options_from_setup(run,models,setup)

    # set up results table
    results = pd.DataFrame([["P_bar","H2O_wtpc","CO2_ppmw"]])
    
    initial_P = int(initial_P)
        
    for n in range(initial_P,1,-1):
        PT["P"] = n # pressure in bars
        melt_wf=mg.melt_comp(run,setup)
        results1 = c.calc_pure_solubility(PT,melt_wf,models)
        results = pd.concat([results, results1], ignore_index=True)
    
    results.columns = results.iloc[0]
    results = results[1:]
    if models.loc["output csv","option"] == "True":    
        results.to_csv('results_pure_solubility.csv', index=False, header=False)
    if models.loc["print status","option"] == "True":
        print("done")

    return results

######################################
### calculate solubility constants ###
######################################
# print capacities for multiple melt compositions in input file
def calc_sol_consts(setup,first_row=0,last_row=None,models=mdv.default_models):
    
    # set up results table
    results_headers_models = pd.DataFrame([["species X opt","Hspeciation opt",
                 "fO2 opt","NNObuffer opt","FMQbuffer opt",
                 "carbon dioxide opt","water opt","hydrogen opt","sulfide opt","sulfate opt","hydrogen sulfide opt","methane opt","carbon monoxide opt","species X solubility opt","Cspeccomp opt","Hspeccomp opt","Date"]])
    results_headers_values = pd.DataFrame([["Sample","Pressure (bar)","T ('C)","SiO2","TiO2","Al2O3","FeOT","MnO","MgO","CaO","Na2O","K2O","P2O5",
                "H2O","CO2 (ppm)","ST (ppm)","Fe3+/FeT","fO2 DFMQ","ln[C_CO2T]","ln[C_H2OT]","ln[C_S2-]","ln[C_S6+]","ln[C_H2S]","ln[C_H2]","ln[C_CO]","ln[C_CH4]","ln[C_X]","M_m_SO"]])
    results_headers = pd.concat([results_headers_values,results_headers_models],axis=1)
    
    if last_row == None:
        last_row = len(setup)
    
    for n in range(first_row,last_row,1): # n is number of rows of data in conditions file
        run = n
        
        # check if any options need to be read from the setup file rather than the models file
        models = options_from_setup(run,models,setup)

        PT={"T":setup.loc[run,"T_C"]}
        melt_wf=mg.melt_comp(run,setup)
        CO2 = setup.loc[run,"CO2ppm"]/1000000.
        CT = (CO2/mdv.species.loc["CO2","M"])*mdv.species.loc["C","M"]
        H2O = setup.loc[run,"H2O"]/100.
        HT = (H2O/mdv.species.loc["H2O","M"])*mdv.species.loc["H2","M"]
        XT = setup.loc[run,"Xppm"]/1000000.
        ST = setup.loc[run,"STppm"]/1000000.
        melt_wf['CO2']=CO2
        melt_wf["H2OT"]=H2O
        melt_wf["ST"]=ST
        melt_wf["X"]=XT
        melt_wf["XT"]=XT
        melt_wf["HT"]=HT
        melt_wf["CT"]=CT
        PT["P"] = setup.loc[run,"P_bar"]
        melt_wf["Fe3FeT"] = mg.Fe3FeT_i(PT,melt_wf,models)
        C_CO32 = mdv.C_CO3(PT,melt_wf,models)
        C_H2OT = mdv.C_H2O(PT,melt_wf,models)
        C_S2 = mdv.C_S(PT,melt_wf,models)
        C_S6 = mdv.C_SO4(PT,melt_wf,models)
        C_H2S = mdv.C_H2S(PT,melt_wf,models)
        C_H2 = mdv.C_H2(PT,melt_wf,models)
        C_CO = mdv.C_CO(PT,melt_wf,models)
        C_CH4 = mdv.C_CH4(PT,melt_wf,models)
        C_X = mdv.C_X(PT,melt_wf,models)
        fO2_ = mg.fO22Dbuffer(PT,mdv.f_O2(PT,melt_wf,models),"FMQ",models)
        M_m = mg.M_m_SO(melt_wf)
        melt_comp = mg.melt_normalise_wf(melt_wf,"yes","no")
                
        ### store results ###
        results_values_models = pd.DataFrame([[models.loc["species X","option"],models.loc["Hspeciation","option"], 
                models.loc["fO2","option"], models.loc["NNObuffer","option"], models.loc["FMQbuffer","option"],
                 models.loc["carbon dioxide","option"], models.loc["water","option"], models.loc["hydrogen","option"], models.loc["sulfide","option"], models.loc["sulfate","option"], models.loc["hydrogen sulfide","option"], models.loc["methane","option"], models.loc["carbon monoxide","option"], models.loc["species X solubility","option"], models.loc["Cspeccomp","option"], models.loc["Hspeccomp","option"],datetime.datetime.now()]])
        results_values_values = pd.DataFrame([[setup.loc[run,"Sample"],PT["P"],PT["T"],melt_comp["SiO2"]*100., melt_comp["TiO2"]*100., melt_comp["Al2O3"]*100., melt_comp["FeOT"]*100., melt_comp["MnO"]*100., melt_comp["MgO"]*100., melt_comp["CaO"]*100., melt_comp["Na2O"]*100., melt_comp["K2O"]*100., melt_comp["P2O5"]*100.,setup.loc[run,"H2O"],setup.loc[run,"CO2ppm"],setup.loc[run,"STppm"],melt_wf["Fe3FeT"],fO2_,math.log(C_CO32),math.log(C_H2OT),math.log(C_S2),math.log(C_S6),math.log(C_H2S),math.log(C_H2),math.log(C_CO),math.log(C_CH4),math.log(C_X),M_m]])
        results1 = pd.concat([results_values_values,results_values_models],axis=1)
    
        if n == first_row:
            results = pd.concat([results_headers, results1])
        else:                         
            results = pd.concat([results, results1])
        
        if models.loc["print status","option"] == "True":
            print(n, setup.loc[run,"Sample"],math.log(C_CO32),math.log(C_H2OT),math.log(C_S2),math.log(C_S6),math.log(C_H2S),math.log(C_H2),math.log(C_CO),math.log(C_CH4),M_m)
    
    results.columns = results.iloc[0]
    results = results[1:]
                  
    if models.loc["output csv","option"] == "True":
        results.to_csv('capacities.csv', index=False, header=False)

    return results

#######################################      
### calculate fugacity coefficients ###
#######################################
def calc_fugacity_coefficients(setup,first_row=0,last_row=None,models=mdv.default_models):

    # set up results table
    results_headers_models = pd.DataFrame([["y_CO2 opt","y_SO2 opt","y_H2S opt","y_H2 opt","y_O2 opt","y_S2 opt","y_CO opt","y_CH4 opt","y_H2O opt","y_OCS opt","y_X opt","Date"]])
    results_headers_values = pd.DataFrame([["Sample","P_bar","T_C","yO2","yH2","yH2O","yS2","ySO2","yH2S","yCO2","yCO","yCH4","yOCS","yX"]])
    results_headers = pd.concat([results_headers_values,results_headers_models],axis=1)
    
    if last_row == None:
        last_row = len(setup)

    for n in range(first_row,last_row,1): # n is number of rows of data in conditions file
        run = n
        
        # check if any options need to be read from the setup file rather than the models file
        models = options_from_setup(run,models,setup)

        PT={"T":setup.loc[run,"T_C"]}
        PT["P"] = setup.loc[run,"P_bar"]
        
        ### store results ###
        results_values_models = pd.DataFrame([[models.loc["y_CO2","option"], models.loc["y_SO2","option"], models.loc["y_H2S","option"], models.loc["y_H2","option"], models.loc["y_O2","option"], models.loc["y_S2","option"], models.loc["y_CO","option"], models.loc["y_CH4","option"], models.loc["y_H2O","option"],models.loc["y_OCS","option"], models.loc["y_X","option"],datetime.datetime.now()]])
        results_values_values = pd.DataFrame([[setup.loc[run,"Sample"],PT["P"],PT["T"],mdv.y_O2(PT,models),mdv.y_H2(PT,models),mdv.y_H2O(PT,models),mdv.y_S2(PT,models),mdv.y_SO2(PT,models),mdv.y_H2S(PT,models),mdv.y_CO2(PT,models),mdv.y_CO(PT,models),mdv.y_CH4(PT,models),mdv.y_OCS(PT,models),mdv.y_X(PT,models)]])
        results1 = pd.concat([results_values_values,results_values_models],axis=1)
    
        if n == first_row:
            results = pd.concat([results_headers, results1])
        else:                         
            results = pd.concat([results, results1])
        
        if models.loc["print status","option"] == "True":
            print(n, setup.loc[run,"Sample"],PT["P"])
    
    results.columns = results.iloc[0]
    results = results[1:]  
    
    if models.loc["output csv","option"] == "True":
        results.to_csv('results_fugacity_coefficients.csv', index=False, header=True)

    return results

###############################               
### Use melt S oxybarometer ###
###############################        
def calc_melt_S_oxybarometer(setup,first_row=0,last_row=None,models=mdv.default_models,p_tol=0.1,nr_step=1.,nr_tol=1.e-9):
    """ 
    Calculates the range in oxygen fugacity based on the melt sulfur content for multiple melt compositions given volatile-free melt composition, volatile content, temperature, and either pressure or assumes Pvsat.


    Parameters
    ----------
    setup: pandas.DataFrame
        Dataframe with melt compositions to be used, requires following headers: 
        Sample, T_C, 
        SiO2, TiO2, Al2O3, (Fe2O3T or FeOT unless Fe2O3 and FeO given), MnO, MgO, CaO, Na2O, K2O, P2O5, 
        H2O and/or CO2ppm and/or STppm and/or Xppm
        Note: concentrations (unless otherwise stated) are in wt%
        Optional
        P_bar is pressure is given (otherwise calculation is at Pvsat)
        Fe3FeT is P_bar is specified
    
    Optional:
    models: pandas.DataFrame
        Dataframe of options for different models.
    first_row: float
        Integer of the first row in the setup file to run (note the first row under the headers is row 0). Default = 0  
    last_row: float
        Integer of the last row in the setup file to run (note the first row under the headers is row 0). Default = length of setup
    p_tol: float
        Required tolerance for convergence of Pvsat in bars. Default = 1.e-1
    nr_step: float
        Step size for Newton-Raphson solver for melt speciation (this can be made smaller if there are problems with convergence.). Default = 1
    nr_tol: float
        Tolerance for the Newton-Raphson solver for melt speciation in weight fraction (this can be made larger if there are problems with convergence). Default = 1.e-9

    Returns
    -------
    results: pandas.DataFrame

    Outputs
    -------
    fO2_range_from_S: csv file (if output csv = yes in models)

    """

    if last_row == None:
        last_row = len(setup)

    # run over rows in file
    for n in range(first_row,last_row,1): # number of rows in the table
   
        # Select run conditions
        run = n # row number
        
        # check if any options need to be read from the setup file rather than the models file
        models = options_from_setup(run,models,setup)

        PT = {"T":setup.loc[run,"T_C"]}
        melt_wf=mg.melt_comp(run,setup)
        melt_wf["H2OT"] = (setup.loc[run, "H2O"]/100.)
        melt_wf["CO2"] = setup.loc[run, "CO2ppm"]/1000000.
        melt_wf["HT"] = ((setup.loc[run, "H2O"]/100.)/mdv.species.loc["H2O","M"])*mdv.species.loc["H2","M"]
        melt_wf["ST"] = setup.loc[run, "STppm"]/1000000.
        melt_wf["XT"] = setup.loc[run, "Xppm"]/1000000.
        melt_wf["CT"] = ((setup.loc[run, "CO2ppm"]/1000000.)/mdv.species.loc["CO2","M"])*mdv.species.loc["C","M"]
        if "sulf_XFe" in setup:
            melt_wf["sulf_XFe"] = setup.loc[run,"sulf_XFe"]
        if "sulf_XCu" in setup:
            melt_wf["sulf_XCu"] = setup.loc[run,"sulf_XCu"]
        if "sulf_XNi" in setup:
            melt_wf["sulf_XNi"] = setup.loc[run,"sulf_XNi"]

        if 'P_bar' in setup:    
            if setup.loc[run,"P_bar"] > 0.:
                PT["P"] = setup.loc[run,"P_bar"]
                melt_wf["Fe3FeT"] = setup.loc[run, "Fe3FeT"]
                sulfsat_results = c.fO2_range_from_S(PT,melt_wf,models)
                sulfsat_results["P_sat_sulf"] = setup.loc[run,"P_bar"]
                sulfsat_results["P_sat_anh"] = setup.loc[run,"P_bar"]
            else: 
                sulfsat_results = c.P_sat_sulf_anh(PT,melt_wf,models,p_tol,nr_step,nr_tol)
        else:
            sulfsat_results = c.P_sat_sulf_anh(PT,melt_wf,models,p_tol,nr_step,nr_tol)

        # create results
        results_headers_table_sample_name, results_values_table_sample_name = results_table_sample_name(setup,run)
        results_headers_table_model_options, results_values_table_model_options = results_table_model_options(models)  
        results_headers_T, results_values_T = pd.DataFrame([["T ('C)"]]), pd.DataFrame([[PT["T"]]])
        results_headers_table_melt_vol = results_table_melt_vol() # "H2OT-eq_wtpc","CO2T-eq_ppmw","ST_ppmw","X_ppmw"
        results_values_table_melt_vol = pd.DataFrame([[setup.loc[run,"H2O"],setup.loc[run,"CO2ppm"],setup.loc[run,"STppm"],setup.loc[run,"Xppm"]]])
        results_headers_table_sulfsat = pd.DataFrame([["P (bar) sulf","S2- SCSS","sulfide saturated?","DFMQ-sulfide","fO2-sulfide","Fe3FeT-sulfide","S6ST-sulfide","P (bar) anh","S6+ SCAS","sulfate saturated?","DFMQ-sulfate","fO2-sulfate","Fe3FeT-sulfate","S6ST-sulfate"]])
        results_values_table_sulfsat = pd.DataFrame([[sulfsat_results["P_sat_sulf"],sulfsat_results["SCSS"],sulfsat_results["sulf_sat"],sulfsat_results["DFMQ_sulf"],sulfsat_results["fO2_sulf"],sulfsat_results["Fe3T_sulf"],sulfsat_results["S6T_sulf"],sulfsat_results["P_sat_anh"],sulfsat_results["SCAS"],sulfsat_results["anh_sat"],sulfsat_results["DFMQ_anh"],sulfsat_results["fO2_anh"],sulfsat_results["Fe3T_anh"],sulfsat_results["S6T_anh"]]])
        results_headers = pd.concat([results_headers_table_sample_name,results_headers_T,results_headers_table_melt_vol,results_headers_table_sulfsat,results_headers_table_model_options],axis=1)
        results1 = pd.concat([results_values_table_sample_name,results_values_T,results_values_table_melt_vol,results_values_table_sulfsat,results_values_table_model_options],axis=1)
    
        if n == first_row:
            results = pd.concat([results_headers, results1])
        else:                         
            results = pd.concat([results, results1])
        
        if models.loc["print status","option"] == "True":
            print(n, setup.loc[run,"Sample"],sulfsat_results["sulf_sat"],sulfsat_results["anh_sat"])
    
    results.columns = results.iloc[0]
    results = results[1:]  
        
    if models.loc["output csv","option"] == "True":
        results.to_csv('fO2_range_from_S.csv', index=False, header=True)

    return results

########################################
### measured parameters within error ### 
########################################
def calc_comp_error(setup,run,iterations,models=mdv.default_models):
    
    # set up results table
    results = pd.DataFrame([["Sample","T_C",
                  "SiO2","TiO2","Al2O3","FeOT","MnO","MgO","CaO","Na2O","K2O","P2O5",
                "H2O","CO2ppm","Xppm","STppm","Fe3FeT"]])
    results1 = pd.DataFrame([[setup.loc[run,"Sample"],setup.loc[run,"T_C"],setup.loc[run,"SiO2"],setup.loc[run,"TiO2"],setup.loc[run,"Al2O3"],setup.loc[run,"FeOT"],setup.loc[run,"MnO"],setup.loc[run,"MgO"],setup.loc[run,"CaO"],setup.loc[run,"Na2O"],setup.loc[run,"K2O"],setup.loc[run,"P2O5"],
                setup.loc[run,"H2O"],setup.loc[run,"CO2ppm"],setup.loc[run,"Xppm"],setup.loc[run,"STppm"], setup.loc[run,"Fe3FeT"]]])
                             
    results = pd.concat([results, results1], ignore_index=True)
    results1 = pd.DataFrame([["sds","",setup.loc[run,"SiO2_sd"],setup.loc[run,"TiO2_sd"],setup.loc[run,"Al2O3_sd"],setup.loc[run,"FeOT_sd"],setup.loc[run,"MnO_sd"],setup.loc[run,"MgO_sd"],setup.loc[run,"CaO_sd"],setup.loc[run,"Na2O_sd"],setup.loc[run,"K2O_sd"],setup.loc[run,"P2O5_sd"],
                setup.loc[run,"H2O_sd"],setup.loc[run,"CO2ppm_sd"],setup.loc[run,"Xppm_sd"],setup.loc[run,"STppm_sd"], setup.loc[run,"Fe3FeT_sd"]]])
                             
    results = pd.concat([results, results1], ignore_index=True)
    results1 = pd.DataFrame([["sd types","",setup.loc[run,"SiO2_sd_type"],setup.loc[run,"TiO2_sd_type"],setup.loc[run,"Al2O3_sd_type"],setup.loc[run,"FeOT_sd_type"],setup.loc[run,"MnO_sd_type"],setup.loc[run,"MgO_sd_type"],setup.loc[run,"CaO_sd_type"],setup.loc[run,"Na2O_sd_type"],setup.loc[run,"K2O_sd_type"],setup.loc[run,"P2O5_sd_type"],
                setup.loc[run,"H2O_sd_type"],setup.loc[run,"CO2ppm_sd_type"],setup.loc[run,"Xppm_sd_type"],setup.loc[run,"STppm_sd_type"], setup.loc[run,"Fe3FeT_sd_type"]]])
                             
    results = pd.concat([results, results1], ignore_index=True)
    for n in range(0,iterations,1): # n is number of rows of data in conditions file
        results1 = c.compositions_within_error(run,setup)
        results1 = pd.DataFrame([[run,setup.loc[run,"T_C"],results1["SiO2"],results1["TiO2"],results1["Al2O3"],results1["FeOT"],results1["MnO"],results1["MgO"],results1["CaO"],results1["Na2O"],results1["K2O"],results1["P2O5"],results1["H2O"],results1["CO2ppm"],results1["Xppm"],results1["STppm"],results1["Fe3FeT"]]])
        results = pd.concat([results, results1], ignore_index=True)
    
    results.columns = results.iloc[0]
    results = results[1:]
    if models.loc["output csv","option"] == "True":
        results.to_csv('random_compositions.csv', index=False, header=False)
    if models.loc["print status","option"] == "True":
        print(n, setup.loc[run,"Sample"],SiO2)
    
    return results

################
### isotopes ###
################

def calc_isotopes_gassing(comp,R_i,models=mdv.default_models,nr_step=1.,nr_tol=1.e-9):
    
    # initial composition
    R = {}
    # for sulfur
    if "bulk 34S/32S" in R_i:
        R["S"] = R_i["bulk 34S/32S"]
    elif "bulk d34S" in R_i:
        R["S"] = iso.delta2ratio("VCDT",34,"S",R_i["bulk d34S"])
    # for carbon
    if "bulk 13C/12C" in R_i:
        R['C'] = R_i["bulk 13C/12C"]
    elif "bulk d13C" in R_i:
        R['C'] = iso.delta2ratio("VPDB",13,"C",R_i["bulk d13C"])
    # for hydrogen
    if "bulk D/H" in R_i:
        R['H'] = R_i["bulk D/H"]
    elif "bulk dD" in R_i:
        R['H'] = iso.delta2ratio("VSMOW",2,"H",R_i["bulk dD"])

    guesses = {"C":iso.iso_initial_guesses("C",R,comp),"H":iso.iso_initial_guesses("H",R,comp),"S":iso.iso_initial_guesses("S",R,comp)}        

    for i in range(0,len(comp),1):
        PT = {"T":comp.loc[i,"T_C"],"P":comp.loc[i,"P_bar"]}
        R_all_species_S,R_m_g_S,R_all_species_C,R_m_g_C,R_all_species_H,R_m_g_H = c.calc_isotopes(PT,comp,R,models,guesses,nr_step,nr_tol,run=i)  
        # store results
        results_headers_table_isotopes_d, results_values_table_isotopes_d = results_table_isotope_d(R,R_all_species_S,R_m_g_S,R_all_species_C,R_m_g_C,R_all_species_H,R_m_g_H)
        results_headers_table_isotopes_R, results_values_table_isotopes_R = results_table_isotope_R(R,R_all_species_S,R_m_g_S,R_all_species_C,R_m_g_C,R_all_species_H,R_m_g_H)
        results_values = pd.concat([results_values_table_isotopes_R,results_values_table_isotopes_d],axis=1)
        if i == 0:
            results_headers = pd.concat([results_headers_table_isotopes_R,results_headers_table_isotopes_d],axis=1)
            results = pd.concat([results_headers, results_values])
        else:
            results = pd.concat([results, results_values])

    results.columns = results.iloc[0]
    results = results[1:]  
    if models.loc["output csv","option"] == "True":
        results.to_csv('results_gassing_isotope.csv', index=False, header=True)
    
    if models.loc["print status","option"] == "True":
        print("done", datetime.datetime.now())

    results1 = results.reset_index(drop=True)
    comp1 = comp.reset_index(drop=True)

    results_ = pd.concat([results1,comp1],axis=1)

    return results_

    # new bulk composition for open vs. closed.
        


#############################################################################################################################
#############################################################################################################################
################################################# IN DEVELOPMENT BELOW HERE #################################################
#############################################################################################################################
#############################################################################################################################

# function to calculate SO2/H2S, S6+/ST, S2-CSS, S6+CAS, STCSS, STCAS, and ST with variable fO2
def calc_sulfur_vfO2(fO2_start,fO2_end,setup,step_size=0.1,models=mdv.default_models):
    PT = {"T":setup["T_C"],"P":setup["P_bar"]}
    P = int(PT["P"])
    T = int(PT["T"])
    K1 = vf.KHOSg(PT)
    K2 = vf.KOSg(PT)
    melt_wf=vf.melt_comp(0.,setup)
    melt_wf['CO2'] = setup.loc[0.,"CO2ppm"]/1000000.
    melt_wf["H2OT"] = setup.loc[0.,"H2O"]/100.
    melt_wf['CT'] = (melt_wf['CO2']/vf.species.loc['CO2','M'])*vf.species.loc['C','M']
    melt_wf['HT'] = (melt_wf['H2OT']/vf.species.loc['H2O','M'])*(2.*vf.species.loc['H','M'])
    fH2O = vf.f_H2O(PT,melt_wf,models)
    end = int(((abs(fO2_end) + abs(fO2_start))/step_size)+1.)
    for n in range(0,end,1):
        fO2_FMQ = fO2_start+(n*step_size)
        fO2 = vf.Dbuffer2fO2(PT,fO2_FMQ,"FMQ",models)
        melt_wf['Fe3FeT'] = vf.fO22Fe3FeT(fO2,PT,melt_wf,models)
        SO2_H2S = (K2*fO2**1.5)/(K1*fH2O)
        SO2_ST = float(SO2_H2S/(SO2_H2S+1.))
        CSO4 = vf.C_SO4(PT,melt_wf,models)
        CS = vf.C_S(PT,melt_wf,models)
        if models.loc["H2S_m","option"] == "False":
            S6S2 = float((CSO4/CS)*fO2**2.)
        elif models.loc["H2S_m","option"] == "True":
            KHS = vf.KHOSg(PT,models)
            CH2S = vf.C_H2S(PT,melt_wf,models)
            CH2OT = vf.C_H2O(PT,melt_wf,models)
            xmH2O = vf.xm_H2OT_so(melt_wf)
            S6S2 = float((CSO4/((KHS*CH2S*(xmH2O**2./CH2OT)) + CS))*fO2**2.)
        S6pST = S6S2/(S6S2+1.)
        SCSS = vf.SCSS(PT,melt_wf,models)
        SCAS = vf.SCAS(PT,melt_wf,models)
        STCSS = SCSS/(1.-S6pST)
        STCAS = SCAS/S6pST
        if STCSS < STCAS:
            ST = STCSS
        else:
            ST =  STCAS
        ST_s2 = ST*(1.-S6pST)
        ST_s6 =ST*(S6pST)
        results1 = pd.DataFrame([[P,T,fH2O,fO2_FMQ,SO2_ST,S6pST,SCSS,SCAS,STCSS,STCAS,ST,ST_s2,ST_s6]])
        if n == 0.:
            results_headers = pd.DataFrame([["P","T","fH2O","fO2_FMQ","SO2/(SO2+H2S)","S6+/ST","SCSS","SCAS",'STCSS','STCAS','ST','ST_S2-','ST_S6+']])
            results = pd.concat([results_headers, results1])
        else:
            results = pd.concat([results, results1])
    results.columns = results.iloc[0]
    results = results[1:]  
    return results

### NEEDS CHECKING ###        
def P_sat_output_fS2(setup,models,first_row=0,last_row=None,p_tol=1.e-1,nr_step=1.,nr_tol=1.e-9):
    # set up results table
    results = pd.DataFrame([["oxygen fugacity","carbon dioxide solubility","C speciation composition","water solubility","water speciation","water speciation composition","sulfide solubility","sulfate solubility","sulfide saturation","ideal gas","carbonylsulfide","mass_volume","COH_species","Saturation calculation","Date"]])
    results1 = pd.DataFrame([[models.loc["fO2","option"],models.loc["carbon dioxide","option"],models.loc["Cspeccomp","option"],models.loc["water","option"],models.loc["Hspeciation","option"],models.loc["Hspeccomp","option"],models.loc["sulfide","option"],models.loc["sulfate","option"],models.loc["sulfur_saturation","option"],models.loc["ideal_gas","option"],models.loc["carbonylsulfide","option"],models.loc["mass_volume","option"],models.loc['COH_species','option'],models.loc['calc_sat','option'],date.today()]])
    results = pd.concat([results, results1], ignore_index=True)
    results1 = ([["Sample","Pressure (bar)","Saturation pressure (bars)","T ('C)","fO2 (DNNO)","fO2 (DFMQ)",
                  "SiO2 (wt%)","TiO2 (wt%)","Al2O3 (wt%)","FeOT (wt%)","MnO (wt%)","MgO (wt%)","CaO (wt%)","Na2O (wt%)","K2O (wt%)","P2O5 (wt%)","ST (ppm)","S6/ST","Fe3/FeT",
                  "SCSS (ppm)","sulfide saturated","SCAS (ppm)","anhydrite saturated","S melt (ppm)",
                "f-fO2","f-fS2","f-fSO2","f-pO2","f-pS2","f-pSO2","f-xgO2","f-xgS2","f-xgSO2",
                 "b-fO2","b-fS2","b-fSO2","b-pO2","b-pS2","b-pSO2","b-xgO2","b-xgS2","b-xgSO2","ySO2"]])
    results = pd.concat([results, results1], ignore_index=True)
    
    if last_row == None:
        last_row = len(setup)

    for n in range(first_row,last_row,1): # n is number of rows of data in conditions file
        run = n

        PT={"T":setup.loc[run,"T_C"]}
        melt_wf=mg.melt_comp(run,setup)
        melt_wf['CO2'] = 0.
        melt_wf["H2OT"] = 0.

        # check if any options need to be read from the setup file rather than the models file
        models = options_from_setup(run,models,setup)

        P_sat_, wm_ST, fSO2, wm_S2m, wm_S6p, pS2, pO2, pSO2, xgS2, xgO2, xgSO2 = c.P_sat_fO2_fS2(PT,melt_wf,models,p_tol)
        if setup.loc[run,"P_bar"] > 0.:
            PT["P"] = setup.loc[run,"P_bar"]
        else:
            PT["P"] = P_sat_
        melt_wf["ST"] = wm_ST
        melt_wf["S2-"] = wm_S2m
        melt_wf["Fe3FeT"] = mg.Fe3FeT_i(PT,melt_wf,models)
        SCSS_,sulfide_sat,SCAS_,sulfate_sat, ss_ST = c.sulfur_saturation(PT,melt_wf,models)
        gas_mf = {"O2":mg.xg_O2(PT,melt_wf,models),"S2":mg.xg_S2(PT,melt_wf,models),"SO2":mg.xg_SO2(PT,melt_wf,models)}
        
        ### store results ###
        results2 = pd.DataFrame([[setup.loc[run,"Sample"],PT["P"],P_sat_,
                setup.loc[run,"T_C"],mg.fO22Dbuffer(PT,mdv.f_O2(PT,melt_wf,models),"NNO",models),mg.fO22Dbuffer(PT,mdv.f_O2(PT,melt_wf,models),"FMQ",models),setup.loc[run,"SiO2"],setup.loc[run,"TiO2"],setup.loc[run,"Al2O3"],mg.Wm_FeOT(melt_wf),setup.loc[run,"MnO"],setup.loc[run,"MgO"],setup.loc[run,"CaO"],setup.loc[run,"Na2O"],setup.loc[run,"K2O"],setup.loc[run,"P2O5"],wm_ST,mg.S6ST(PT,melt_wf,models),melt_wf["Fe3FeT"],SCSS_,sulfide_sat,SCAS_,sulfate_sat,ss_ST,
                mdv.f_O2(PT,melt_wf,models),setup.loc[run,"fS2"],fSO2, pO2,pS2,pSO2, xgO2,xgS2,xgSO2,mdv.f_O2(PT,melt_wf,models),mg.f_S2(PT,melt_wf,models),mg.f_SO2(PT,melt_wf,models), mg.p_O2(PT,melt_wf,models),mg.p_S2(PT,melt_wf,models),mg.p_SO2(PT,melt_wf,models), mg.xg_O2(PT,melt_wf,models),mg.xg_S2(PT,melt_wf,models),mg.xg_SO2(PT,melt_wf,models),mg.y_SO2(PT,models)]])
                             
        results = pd.concat([results, results1], ignore_index=True)
        if models.loc["output csv","option"] == "True":
            results.to_csv('saturation_pressures_fS2.csv', index=False, header=False)
        if models.loc["print status","option"] == "True":
            print(n, setup.loc[run,"Sample"],PT["P"])


#########################
### Sulfate capacity ###
#########################
# calculate the Csulfate for multiple melt compositions in input file
def Csulfate_output(setup,first_row=0,last_row=None,models=mdv.default_models):
    
    # set up results table
    results = pd.DataFrame([["oxygen fugacity","carbon dioxide solubility","C speciation composition","water solubility","water speciation","water speciation composition","sulfide solubility","sulfate solubility","sulfide saturation","ideal gas","carbonylsulfide","mass_volume","Date"]])
    results1 = pd.DataFrame([[models.loc["fO2","option"],models.loc["carbon dioxide","option"],models.loc["Cspeccomp","option"],models.loc["water","option"],models.loc["Hspeciation","option"],models.loc["Hspeccomp","option"],models.loc["sulfide","option"],models.loc["sulfate","option"],models.loc["sulfur_saturation","option"],models.loc["ideal_gas","option"],models.loc["carbonylsulfide","option"],models.loc["mass_volume","option"],date.today()]])
    results = pd.concat([results, results1], ignore_index=True)
    results1 = ([["Sample","Pressure (bar)","T ('C)","SiO2","TiO2","Al2O3","FeOT","MnO","MgO","CaO","Na2O","K2O","P2O5",
                "H2O","CO2 (ppm)","ST (ppm)","S6/ST","Fe3/FeT","ln[Csulfide]","ln[Csulfate]","fO2","DNNO","DFMQ"]])
    results = pd.concat([results, results1], ignore_index=True)
    
    if last_row == None:
        last_row = len(setup)
    
    for n in range(first_row,last_row,1): # n is number of rows of data in conditions file
        run = n
        
        # check if any options need to be read from the setup file rather than the models file
        models = options_from_setup(run,models,setup)

        PT={"T":setup.loc[run,"T_C"]}
        melt_wf=mg.melt_comp(run,setup)
        melt_wf['CO2'] = setup.loc[run,"CO2ppm"]/1000000.
        melt_wf["H2OT"] = setup.loc[run,"H2O"]/100.
        melt_wf["ST"] = setup.loc[run,"STppm"]/1000000.
        PT["P"] = setup.loc[run,"P_bar"]
        melt_wf["Fe3FeT"] = mg.Fe3FeT_i(PT,melt_wf,models)
        if setup.loc[run,"S6ST"] >= 0.:
            melt_wf["S6ST"] = setup.loc[run,"S6ST"]
        else:
            melt_wf["S6ST"] = ""
        Csulfate_ = mdv.C_SO4(PT,melt_wf,models)
                
        ### store results ###
        results2 = pd.DataFrame([[setup.loc[run,"Sample"],setup.loc[run,"P_bar"],setup.loc[run,"T_C"],setup.loc[run,"SiO2"],setup.loc[run,"TiO2"],setup.loc[run,"Al2O3"],mg.Wm_FeOT(run,setup),setup.loc[run,"MnO"],setup.loc[run,"MgO"],setup.loc[run,"CaO"],setup.loc[run,"Na2O"],setup.loc[run,"K2O"],setup.loc[run,"P2O5"],setup.loc[run,"H2O"],setup.loc[run,"CO2ppm"],setup.loc[run,"STppm"],melt_wf["S6ST"],melt_wf["Fe3FeT"],log(mg.C_S(PT,melt_wf,models)),log(Csulfate_),mdv.f_O2(PT,melt_wf,models),mg.fO22Dbuffer(PT,mdv.f_O2(PT,melt_wf,models),"NNO"),mg.fO22Dbuffer(PT,mdv.f_O2(PT,melt_wf,models),"FMQ")]])
        results = pd.concat([results, results2], ignore_index=True)                     
        if models.loc["output csv","option"] == "True":
            results.to_csv('Csulfate.csv', index=False, header=False)
        if models.loc["print status","option"] == "True":
            print(n, setup.loc[run,"Sample"],log(Csulfate_),log(mg.C_S(PT,melt_wf,models)))
        return results

##########################
### Fe3+/Fe2+ from fO2 ###        
##########################
def Fe3Fe2_output(setup,first_row=0,last_row=None,models=mdv.default_models):
    # set up results table
    results = pd.DataFrame([["oxygen fugacity","carbon dioxide solubility","C speciation composition","water solubility","water speciation","water speciation composition","sulfide solubility","sulfate solubility","sulfide saturation","ideal gas","carbonylsulfide","mass_volume","COH_species","Date"]])
    results1 = pd.DataFrame([[models.loc["fO2","option"],models.loc["carbon dioxide","option"],models.loc["Cspeccomp","option"],models.loc["water","option"],models.loc["Hspeciation","option"],models.loc["Hspeccomp","option"],models.loc["sulfide","option"],models.loc["sulfate","option"],models.loc["sulfur_saturation","option"],models.loc["ideal_gas","option"],models.loc["carbonylsulfide","option"],models.loc["mass_volume","option"],models.loc['COH_species','option'],date.today()]])
    results = pd.concat([results, results1], ignore_index=True)
    results1 = ([["Sample","Pressure (bar)","T ('C)","fO2 (DNNO)","fO2 (DFMQ)",
                  "SiO2 (wt%)","TiO2 (wt%)","Al2O3 (wt%)","FeOT (wt%)","MnO (wt%)","MgO (wt%)","CaO (wt%)","Na2O (wt%)","K2O (wt%)","P2O5 (wt%)","Fe3/FeT"]])
    results = pd.concat([results, results1], ignore_index=True)
    
    if last_row == None:
        last_row = len(setup)

    for n in range(first_row,last_row,1): # n is number of rows of data in conditions file
        run = n
        
        # check if any options need to be read from the setup file rather than the models file
        models = options_from_setup(run,models,setup)

        PT={"T":setup.loc[run,"T_C"]}
        PT["P"] = setup.loc[run,"P_bar"]
        melt_wf=mg.melt_comp(run,setup)
        melt_wf['Fe3FeT'] = mg.Fe3FeT_i(run,PT,melt_wf,setup,models)
      ### store results ###
        results2 = pd.DataFrame([[setup.loc[run,"Sample"],PT["P"],
                setup.loc[run,"T_C"],mg.fO22Dbuffer(PT,mdv.f_O2(PT,melt_wf,models),"NNO"),mg.fO22Dbuffer(PT,mdv.f_O2(PT,melt_wf,models),"FMQ"),setup.loc[run,"SiO2"],setup.loc[run,"TiO2"],setup.loc[run,"Al2O3"],mg.Wm_FeOT(run,setup),setup.loc[run,"MnO"],setup.loc[run,"MgO"],setup.loc[run,"CaO"],setup.loc[run,"Na2O"],setup.loc[run,"K2O"],setup.loc[run,"P2O5"],melt_wf['Fe3FeT']]])
        results = pd.concat([results, results2], ignore_index=True)                     
        if models.loc["output csv","option"] == "True":
            results.to_csv('Fe3FeT_outputs.csv', index=False, header=False)
        if models.loc["print status","option"] == "True":
            print(n, setup.loc[run,"Sample"],melt_wf['Fe3FeT'])
        return results

############################################
### melt-vapour equilibrium at given fO2 ###
############################################

def eq_given_fO2(setup,inputs,models=mdv.default_models): # only S atm
    
    option = inputs["option"]
    
    # set T, volatile composition of the melt, and tolerances
    #nr_step = inputs["nr_step"]
    #nr_tol = inputs["nr_tol"]
    
    if option == "loop":
        run = inputs["run"]
        PT={'T':setup.loc[run,"T_C"]}
        melt_wf=mg.melt_comp(run,setup)
        melt_wf['CO2'] = setup.loc[run,"CO2ppm"]/1000000.
        melt_wf["H2OT"]  = setup.loc[run,"H2O"]/100.
        melt_wf["ST"] = setup.loc[run,"STppm"]/1000000.
        melt_wf["H2"] = 0.
        step = inputs["dfO2_step"]
        initial = inputs["fO2_i"]
        final = inputs["fO2_f"]
        start = 0
        end = inputs["no_steps"]
        difference = (final - initial) + 1
        step_size = difference/end
        # Set bulk composition
        wt_C = (melt_wf["CO2"]/mdv.species.loc["CO2","M"])*mdv.species.loc["C","M"]
        wt_H = (melt_wf["H2OT"]/mdv.species.loc["H2O","M"])*(2.*mdv.species.loc["H","M"])
        wt_S = melt_wf["ST"]
        bulk_wf = {"C":wt_C,"H":wt_H,"S":wt_S}
        system = eq.set_system(bulk_wf,models)
        
    elif option == "spreadsheet":
        start = inputs["first row"]
        end = inputs["last row"]

    # update Fe3+/FeT and water speciation at saturation pressure and check for sulfur saturation
    #melt_wf["Fe3FeT"] = mg.fO22Fe3FeT(10.**initial,run,PT,setup,models)
    #melt_wf["Fe3FeT"] = mg.Fe3FeT_i(run,PT,melt_wf,setup,models)
    #melt_wf["S6ST"] = mg.S6ST(run,PT,melt_wf,setup,models)
    #melt_wf["H2Omol"] = 0. #mg.wm_H2Omol(run,PT,melt_wf,setup,models)
    #melt_wf["OH"] = 0., #mg.wm_OH(run,PT,melt_wf,setup,models)
    #SCSS_,sulfide_sat,SCAS_,sulfate_sat,ST_ = sulfur_saturation(run,PT,melt_wf,setup,models)

        
    # create results table
    results_header1 = pd.DataFrame([["oxygen fugacity","carbon dioxide solubility","C speciation composition","water solubility","water speciation","water speciation composition","sulfide solubility","sulfur speciation","ideal gas","carbonylsulfide","bulk composition","equilibrate Fe","starting pressure","gassing direction","gassing style","mass_volume","crystallisation","isotopes","Date"]])
    results_header2 = pd.DataFrame([[
models.loc["fO2","option"],models.loc["carbon dioxide","option"],models.loc["Cspeccomp","option"],models.loc["water","option"],models.loc["Hspeciation","option"],models.loc["Hspeccomp","option"],models.loc["sulfide","option"],models.loc["sulfate","option"],models.loc["ideal_gas","option"],models.loc["carbonylsulfide","option"],models.loc["bulk_composition","option"],models.loc["eq_Fe","option"],models.loc["starting_P","option"],models.loc["gassing_direction","option"],models.loc["gassing_style","option"],models.loc["mass_volume","option"],models.loc["crystallisation","option"],models.loc["isotopes","option"],date.today()]])
    results_header = pd.concat([results_header1, results_header2], ignore_index=True)
    results_chemistry1 = pd.DataFrame([["P","T('C)","System","run","Sample","H2O (mwf)","CO2 (mwf)","ST (mwf)","Fe3FeT","S6ST","O (twf)","C (twf)","H (wtf)","S (twf)","Fe (twf)",
"SiO2 (wt%)","TiO2 (wt%)","Al2O3 (wt%)","FeOT (wt%)","MnO (wt%)","MgO (wt%)","CaO (wt%)","Na2O (wt%)","K2O (wt%)","P2O5 (wt%)","xg_O2","xg_CO","xg_CO2","xg_H2","xg_H2O","xg_CH4","xg_S2","xg_SO2","xg_SO3","xg_H2S","xg_OCS","Xg_t",
               "xm_CO2","xm_H2O","xm_H2Omol","xm_OH","xm_H2","Xm_t_SO","Xm_t_ox",
               "wm_CO2","wm_H2O","wm_H2Omol","wm_OH","wm_H2","wm_S","wm_SO3","wm_ST","Fe3T","S6T",
               "DFMQ","DNNO","SCSS","sulfide sat?","SCAS","sulfate sat?","wt_g","wt_O","wt_C","wt_H","wt_S",
               "fO2","fH2","fH2O","fS2","fSO2","fSO3","fH2S","fCO2","fCO","fCH4","fOCS",
               "yO2","yH2","yH2O","yS2","ySO2","ySO3","yH2S","yCO2","yCO","yCH4","yOCS",
               "M_m_SO","M_m_ox","C_H2O","C_H2","C_CO3","C_S","C_SO4",
               "KD1","KHOg","KHOm","KHOSg","KCOg","KCOHg","KOCSg","KSOg","KSOg2"]])
    results_chemistry = pd.concat([results_header, results_chemistry1], ignore_index=True)
    
    
    # run over different fO2 #
    for i in range(start,end,1): 
        if option == "loop":
            i_ = (i*step_size)+initial # fO2 in log units 
            fO2_ = 10.**i_
            PT["P"] = inputs["P"]
            if models.loc["print status","option"] == "True":
                print(setup.loc[run,"Sample"],fO2_)
        elif option == "spreadsheet":
            run = i
            PT={'T':setup.loc[run,"T_C"]}
            melt_wf=mg.melt_comp(run,setup)
            melt_wf['CO2'] = setup.loc[run,"CO2ppm"]/1000000.
            melt_wf["H2OT"]  = setup.loc[run,"H2O"]/100.
            melt_wf["ST"] = setup.loc[run,"STppm"]/1000000.
            melt_wf["H2"] = 0.
            PT["P"] = setup.loc[run,"P_bar"]
            melt_wf['Fe3FeT'] = mg.Fe3FeT_i(PT,melt_wf,models)
            fO2_ = mdv.f_O2(PT,melt_wf,models)
            # Set bulk composition
            wt_C = (melt_wf["CO2"]/mdv.species.loc["CO2","M"])*mdv.species.loc["C","M"]
            wt_H = (melt_wf["H2OT"]/mdv.species.loc["H2O","M"])*(2.*mdv.species.loc["H","M"])
            wt_S = melt_wf["ST"]
            bulk_wf = {"C":wt_C,"H":wt_H,"S":wt_S,"CT":wt_C,"HT":wt_H,"ST":wt_S}
            system = eq.set_system(bulk_wf,models)
            if models.loc["print status","option"] == "True":
                print(setup.loc[run,"Sample"],fO2_,PT["P"])
        
        # work out equilibrium partitioning between melt and gas phase
        melt_wf["Fe3FeT"] = mg.fO22Fe3FeT(fO2_,PT,models)
        Fe3T = melt_wf["Fe3FeT"]
        #xg_S2_, result1, result2, result3 = eq.eq_SOFe_fO2(run,PT,10.**i_,bulk_wf,melt_wf,setup,models,nr_step,nr_tol,guessx)
        #xg_SO2_, xg_O2_, Xg_t, Fe32, Fe3T, wm_S_, wm_SO3_, S62, S6T, wm_ST_ = result1
        #wt_g, wt_O_, wt_S_ = result3
        #guessx = xg_S2_
        #xg_O2_, xg_S2_, xg_SO2_, wm_S_, wm_SO3_, wm_ST_, S6T, Xg_t = eq.S_P_fO2_1(run,PT,fO2_,melt_wf,setup,models)
        #wm_CO2_, xm_CO2_, wm_H2O_, xm_H2O_, wm_H2_, xm_H2_, wm_H2Omol_, xm_H2Omol_, wm_OH_, xm_OH_, xg_CO_, xg_CO2_, xg_H2_, xg_H2O_, xg_CH4_, xg_H2S_, xg_OCS_, xg_SO3_, Xm_t, Xm_t_ox, wt_C_, wt_H_, wt_g = 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.
        xg_O2_, xg_S2_, xg_SO2_, xg_SO3_, xg_H2_, xg_H2O_, xg_H2S_, xg_CO_, xg_CO2_, xg_CH4_, xg_OCS_, wm_S_, wm_SO3_, wm_ST_, S6T, wm_H2O_, xm_H2O_, wm_H2_, xm_H2_, wm_H2Omol_, xm_H2Omol_, wm_OH_, xm_OH_, wm_CO2_, xm_CO2_, Xg_t, Xm_t, Xm_t_ox, wt_C_, wt_H_, wt_S_, wt_g = eq.S_P_fO2(PT,fO2_,melt_wf,models)
                
        # set melt composition for forward calculation
        melt_wf = {"CO2":wm_CO2_,"H2OT":wm_H2O_,"ST":wm_ST_,"S6ST":S6T,"Fe3FeT":Fe3T,"H2":wm_H2_,"H2Omol":wm_H2Omol_,"OH":wm_OH_,"S2-":wm_S_}
    
        # check for sulfur saturation and display warning in outputs
        SCSS_,sulfide_sat,SCAS_,sulfate_sat, ST_ = sulfur_saturation(PT,melt_wf,models)
        if sulfide_sat == "yes":
            warning = "WARNING: sulfide-saturated"
        elif sulfate_sat == "yes":
            warning = "WARNING: sulfate-saturated"
        else:
            warning = ""

        # store results
               
        results2 = pd.DataFrame([[PT["P"],PT["T"],system,run,setup.loc[run,"Sample"],melt_wf["H2OT"],melt_wf["CO2"],melt_wf["ST"],melt_wf["Fe3FeT"],"SORT","SORT",bulk_wf["C"],bulk_wf["H"],bulk_wf["S"],"SORT",
setup.loc[run,"SiO2"],setup.loc[run,"TiO2"],setup.loc[run,"Al2O3"],mg.Wm_FeOT(melt_wf),setup.loc[run,"MnO"],setup.loc[run,"MgO"],setup.loc[run,"CaO"],setup.loc[run,"Na2O"],setup.loc[run,"K2O"],setup.loc[run,"P2O5"],xg_O2_,xg_CO_,xg_CO2_,xg_H2_,xg_H2O_,xg_CH4_,xg_S2_,xg_SO2_,xg_SO3_,xg_H2S_,xg_OCS_,Xg_t,
               xm_CO2_,xm_H2O_,xm_H2Omol_,xm_OH_,xm_H2_,Xm_t,Xm_t_ox,
               wm_CO2_,wm_H2O_,wm_H2Omol_,wm_OH_,wm_H2_,wm_S_,wm_SO3_,wm_ST_,Fe3T,S6T,
               mg.fO22Dbuffer(PT,fO2_,"FMQ"),mg.fO22Dbuffer(PT,fO2_,"NNO"),SCSS_,sulfide_sat,SCAS_,sulfate_sat,
               wt_g,"SORT",wt_C,wt_H,wt_S,
fO2_,mg.f_H2(PT,melt_wf,models),mg.f_H2O(PT,melt_wf,models),mg.f_S2(PT,melt_wf,models),mg.f_SO2(PT,melt_wf,models),mg.f_SO3(PT,melt_wf,models),mg.f_H2S(PT,melt_wf,models),mg.f_CO2(PT,melt_wf,models),mg.f_CO(PT,melt_wf,models),mg.f_CH4(PT,melt_wf,models),mg.f_OCS(PT,melt_wf,models),
mg.y_O2(PT,models),mg.y_H2(PT,models),mg.y_H2O(PT,models),mg.y_S2(PT,models),mg.y_SO2(PT,models),mg.y_SO3(PT,models),mdv.y_H2S(PT,models),mg.y_CO2(PT,models),mg.y_CO(PT,models),mg.y_CH4(PT,models),mg.y_OCS(PT,models),
mg.M_m_SO(melt_wf),mg.M_m_ox(melt_wf,models),mg.C_H2O(PT,melt_wf,models),mg.C_H2(PT,melt_wf,models),mdv.C_CO3(PT,melt_wf,models),mg.C_S(PT,melt_wf,models),mg.C_SO4(PT,melt_wf,models),
mg.KD1(PT,melt_wf,models),mg.KHOg(PT,models),mg.KHOm(PT,melt_wf,models),mg.KHOSg(PT,models),mg.KCOg(PT,models),mg.KCOHg(PT,models),mg.KOCSg(PT,models),mg.KOSg(PT,models),mg.KOSg2(PT,models)]])
        results_chemistry = pd.concat([results_chemistry, results2], ignore_index=True)
        if models.loc["output csv","option"] == "True":
            results_chemistry.to_csv('results_fO2_chemistry.csv', index=False, header=False)
        return results_chemistry

##############################################
### fO2 of silm+sulfm+anh at given T and P ###
##############################################

def fO2_SSA_output(setup,first_row=0,last_row=None,models=mdv.default_models):
    # set up results table
    results = pd.DataFrame([["Sample","P (bar)","T ('C)","fO2 (DFMQ)",
                  "SiO2 (wt%)","TiO2 (wt%)","Al2O3 (wt%)","FeOT (wt%)","MnO (wt%)","MgO (wt%)","CaO (wt%)","Na2O (wt%)","K2O (wt%)","P2O5 (wt%)",
                "H2OT (wt%)","CO2 (ppm)","ST (ppm)","SCSS (ppm)","SCAS (ppm)", "S6+/ST","Fe3+/FeT"]])

    if last_row == None:
        last_row = len(setup)

    for n in range(first_row,last_row,1): # n is number of rows of data in conditions file
        run = n
        
        # check if any options need to be read from the setup file rather than the models file
        models = options_from_setup(run,models,setup)

        PT={"T":setup.loc[run,"T_C"], "P":setup.loc[run,"P_bar"]}
        melt_wf = {'CO2':setup.loc[run,"CO2ppm"]/1000000.,"H2OT":setup.loc[run,"H2O"]/100.,"Fe3FeT":0.}
        
        fO2, DFMQ, wmST, S6ST, S6, S2 = c.fO2_silm_sulf_anh(run,PT,melt_wf,setup,models)
        
        Fe3FeT_n0 = melt_wf["Fe3FeT"]
        Fe3FeT_n1 = mdv.fO22Fe3FeT(fO2,run,PT,setup,models)
                            
        if ((Fe3FeT_n0 - Fe3FeT_n1)**2)**0.5 > 0.01:
            melt_wf["Fe3FeT"] = Fe3FeT_n1
            fO2, DFMQ, wmST, S6ST, S6, S2 = c.fO2_silm_sulf_anh(run,PT,melt_wf,setup,models)
            Fe3FeT_n0 = melt_wf["Fe3FeT"]
            Fe3FeT_n1 = mdv.fO22Fe3FeT(fO2,run,PT,setup,models)
       
        ### store results ###
        results2 = pd.DataFrame([[setup.loc[run,"Sample"],PT["P"],setup.loc[run,"T_C"],DFMQ,setup.loc[run,"SiO2"],setup.loc[run,"TiO2"],setup.loc[run,"Al2O3"],mg.Wm_FeOT(run,setup),setup.loc[run,"MnO"],setup.loc[run,"MgO"],setup.loc[run,"CaO"],setup.loc[run,"Na2O"],setup.loc[run,"K2O"],setup.loc[run,"P2O5"],
                setup.loc[run,"H2O"],setup.loc[run,"CO2ppm"],wmST, S2, S6, S6ST, melt_wf["Fe3FeT"]]])
        results = pd.concat([results, results2], ignore_index=True)
        if models.loc["output csv","option"] == "True":
            results.to_csv('fO2_silm_sulf_anh.csv', index=False, header=False)
        if models.loc["print status","option"] == "True":
            print(n, setup.loc[run,"Sample"],PT["P"])
        return results
        
##############################################
### S content at given T, P, fO2, C, and H ###
##############################################
            
def S_given_T_P_fO2_C_H_output(setup,first_row=0,last_row=None,models=mdv.default_models,nr_step=1.,nr_tol=1.e-9):
                
    if models.loc["H2S_m","option"] != "False":
        raise TypeError("This calculation assumes H2S is insoluble in the melt")
    
    if last_row == None:
        last_row = len(setup)

    for n in range(first_row,last_row,1): # n is number of rows of data in conditions file
        run = n
        
        # check if any options need to be read from the setup file rather than the models file
        models = options_from_setup(run,models,setup)

        PT={"T":setup.loc[run,"T_C"], "P":setup.loc[run,"P_bar"]}
        melt_wf=mg.melt_comp(run,setup)
        melt_wf['CO2']= setup.loc[run,"CO2ppm"]/1000000.
        melt_wf["H2OT"] = setup.loc[run,"H2O"]/100.
        melt_wf["XT"] = setup.loc[run,"Xppm"]/1000000.
        melt_wf["ST"] = 0.
        melt_wf["CT"] = (melt_wf["CO2"]*mdv.species.loc['C','M'])/mdv.species.loc['CO2','M']
        melt_wf["HT"] = (melt_wf["H2OT"]*mdv.species.loc['H','M'])/mdv.species.loc['H2O','M']
        melt_wf["Fe3FeT"] = mg.Fe3FeT_i(PT,melt_wf,models)                                              
        
        conc, frac = c.S_given_T_P_fO2_C_H(PT,melt_wf,models,nr_step,nr_tol)
        melt_wf["ST"] = conc["wm_ST"]
        melt_wf["S2-"] = conc["wm_S2m"]
        melt_comp = mg.melt_normalise_wf(melt_wf,"yes","no")
        sulf_sat_result = c.sulfur_saturation(PT,melt_wf,models)

        # create results
        results_headers_table_sample_name, results_values_table_sample_name = results_table_sample_name(setup,run)
        results_headers_table_melt_comp_etc, results_values_table_melt_comp_etc = results_table_melt_comp_etc(PT,melt_comp,conc,frac,melt_wf)
        results_headers_table_model_options, results_values_table_model_options = results_table_model_options(models)    
        results_headers_table_f_p_xg_y_M_C_K_d, results_values_table_f_p_xg_y_M_C_K_d = results_table_f_p_xg_y_M_C_K_d(PT,melt_wf,models)
        results_headers_table_sat, results_values_table_sat = results_table_sat(sulf_sat_result,PT,melt_wf,models)
        results_headers_table_melt_vol = results_table_melt_vol() # "H2OT-eq_wtpc","CO2T-eq_ppmw","ST_ppmw","X_ppmw"
        results_values_table_melt_vol = pd.DataFrame([[setup.loc[run,"H2O"],setup.loc[run,"CO2ppm"],conc["wm_ST"]*1000000.,setup.loc[run,"Xppm"]]])
        results_headers = pd.concat([results_headers_table_sample_name,results_headers_table_melt_comp_etc,results_headers_table_melt_vol,results_headers_table_sat,results_headers_table_f_p_xg_y_M_C_K_d,results_headers_table_model_options],axis=1)
        results1 = pd.concat([results_values_table_sample_name,results_values_table_melt_comp_etc,results_values_table_melt_vol,results_values_table_sat,results_values_table_f_p_xg_y_M_C_K_d,results_values_table_model_options],axis=1)
    
        if n == first_row:
            results = pd.concat([results_headers, results1])
        else:                         
            results = pd.concat([results, results1])
        
        if models.loc["print status","option"] == "True":
            print(n, setup.loc[run,"Sample"],PT["P"])
    
    results.columns = results.iloc[0]
    results = results[1:]  
    if models.loc["output csv","option"] == "True":
        results.to_csv('results_S_given_T_P_fO2_C_H.csv', index=False, header=True)

    return results
        
##################################################################################
### vapor undersaturated cooling for S2-, S6+, Fe3+, Fe2+, H2OT, CO32- cooling ###
##################################################################################

def cooling(run,cooling_inputs,setup,models):
    
    if models.loc["print status","option"] == "True":
        print(setup.loc[run,"Sample"])
    
    # check if any options need to be read from the setup file rather than the models file
    models = options_from_setup(run,models,setup)

    # set T, volatile composition of the melt, and tolerances
    PT={"P":setup.loc[run,"P_bar"]}
    PT["T"]=setup.loc[run,"T_C"]
    melt_wf = {'CO2':setup.loc[run,"CO2ppm"]/1000000.,"H2OT":setup.loc[run,"H2O"]/100.,"H2":0.}
    melt_wf["CT"] = (melt_wf["CO2"]/mdv.species.loc["CO2","M"])*mdv.species.loc["C","M"]
    melt_wf["HT"] = (2.*melt_wf["H2OT"]/mdv.species.loc["H2O","M"])*mdv.species.loc["H","M"]
    nr_step = cooling_inputs["nr_step"]
    nr_tol = cooling_inputs["nr_tol"]
    dt_step = cooling_inputs["dt_step"]
    psat_tol = cooling_inputs["psat_tol"]
        
    # Calculate S and Fe composition at initial T and check for sulfur saturation
    melt_wf["Fe3FeT"] = mg.Fe3FeT_i(run,PT,melt_wf,setup,models)
    Fe3Fe2_ = mg.Fe3Fe2(melt_wf)
    melt_wf["CO"] = 0.
    melt_wf["CH4"] = 0.
    melt_wf["H2S"] = 0. 
    wm_H2_, wm_CH4_, wm_H2S_, wm_CO_ = 0., 0., 0., 0.
    
    if models.loc["bulk_O","option"] == "inc S":
        melt_wf["ST"] = setup.loc[run,"STppm"]/1000000.
        melt_wf["S6ST"] = mg.S6ST(run,PT,melt_wf,setup,models)
        melt_wf["S2-"] = (1.-melt_wf["S6ST"])*melt_wf["ST"]
        melt_wf["S6+"] = melt_wf["S6ST"]*melt_wf["ST"]     
    elif models.loc["bulk_O","option"] == "exc S":
        melt_wf["ST"] = 0.
        melt_wf["S2-"] = 0.
        melt_wf["S6+"] = 0.
    
    SCSS_,sulfide_sat,SCAS_,sulfate_sat,ST_ = c.sulfur_saturation(run,PT,melt_wf,setup,models)
    wm_S2m_ = melt_wf["S2-"]
    wm_S6p_ = melt_wf["S6+"]
    wm_SO3_ = (wm_S6p_/(mdv.species.loc["S","M"]))*(mdv.species.loc["S","M"] + 3.*mdv.species.loc["O","M"])
        
    # Set bulk composition
    wt_C, wt_O, wt_H, wt_S, wt_Fe, wt_g_, Wt_ = c.bulk_composition(run,PT,melt_wf,setup,models)
    
    if models.loc["bulk_O","option"] == "exc S":
        melt_wf["ST"] = setup.loc[run,"STppm"]/1000000.           
        melt_wf["S6ST"] = mg.S6ST(run,PT,melt_wf,setup,models)
        melt_wf["S2-"] = (1.-melt_wf["S6ST"])*melt_wf["ST"]
        melt_wf["S6+"] = melt_wf["S6ST"]*melt_wf["ST"]     
        wt_S = melt_wf["ST"]
    
    bulk_wf = {"C":wt_C,"H":wt_H,"O":wt_O,"S":wt_S,"Fe":wt_Fe,"Wt":Wt_}
        
    # set system and initial guesses
    system = eq.set_system(melt_wf,models)
    guessx = mdv.f_O2(run,PT,melt_wf,setup,models)

    if models.loc["bulk_O","option"] == "exc S":
        fO2_, A, B, C = eq.eq_SOFe_melt(run,PT,bulk_wf,melt_wf,setup,models,nr_step/10.,nr_tol,guessx)
        Fe32, Fe3T, S62, S6T = A
        melt_wf["S6ST"] = S6T
        melt_wf["Fe3FeT"] = Fe3T          
        melt_wf["S2-"] = (1.-melt_wf["S6ST"])*melt_wf["ST"]
        melt_wf["S6+"] = melt_wf["S6ST"]*melt_wf["ST"]
        guessx = mdv.f_O2(run,PT,melt_wf,setup,models)
    
    # create results table
    results_header1 = pd.DataFrame([["System","run","Sample","H2O (mwf)","CO2 (mwf)","ST (mwf)","Fe3FeT","S6ST","O (twf)","C (twf)","H (wtf)","S (twf)","Fe (twf)",
"SiO2 (wt%)","TiO2 (wt%)","Al2O3 (wt%)","FeOT (wt%)","MnO (wt%)","MgO (wt%)","CaO (wt%)","Na2O (wt%)","K2O (wt%)","P2O5 (wt%)",
"oxygen fugacity","carbon dioxide solubility","C speciation composition","water solubility","water speciation","water speciation composition","sulfide solubility","sulfate solubility","ideal gas","carbonylsulfide","bulk composition","equilibrate Fe","starting pressure","gassing direction","gassing style","mass_volume","crystallisation","isotopes","Date"]])
    results_header2 = pd.DataFrame([[system,run,setup.loc[run,"Sample"],melt_wf["H2OT"],melt_wf["CO2"],melt_wf["ST"],melt_wf["Fe3FeT"],"SORT",bulk_wf["O"],bulk_wf["C"],bulk_wf["H"],bulk_wf["S"],bulk_wf["Fe"],
setup.loc[run,"SiO2"],setup.loc[run,"TiO2"],setup.loc[run,"Al2O3"],mg.Wm_FeOT(run,setup),setup.loc[run,"MnO"],setup.loc[run,"MgO"],setup.loc[run,"CaO"],setup.loc[run,"Na2O"],setup.loc[run,"K2O"],setup.loc[run,"P2O5"],
models.loc["fO2","option"],models.loc["carbon dioxide","option"],models.loc["Cspeccomp","option"],models.loc["water","option"],models.loc["Hspeciation","option"],models.loc["Hspeccomp","option"],models.loc["sulfide","option"],models.loc["sulfate","option"],models.loc["ideal_gas","option"],models.loc["carbonylsulfide","option"],models.loc["bulk_composition","option"],models.loc["eq_Fe","option"],models.loc["starting_P","option"],models.loc["gassing_direction","option"],models.loc["gassing_style","option"],models.loc["mass_volume","option"],models.loc["crystallisation","option"],models.loc["isotopes","option"],date.today()]])
    results_header = pd.concat([results_header1, results_header2], ignore_index=True)
    results_chemistry1 = pd.DataFrame([["P","T('C)","xg_O2","xg_CO","xg_CO2","xg_H2","xg_H2O","xg_CH4","xg_S2","xg_SO2","xg_H2S","xg_OCS","Xg_t",
               "xm_CO2","xm_H2O","Xm_t_SO","Xm_t_ox",
               "wm_CO2","wm_H2O","wm_H2","wm_CO","wm_CH4","wm_S","wm_SO3","wm_H2S","wm_ST","Fe32","Fe3T","S62","S6T",
               "DFMQ","DNNO","SCSS","sulfide sat?","SCAS","sulfate sat?","wt_g","wt_g_O","wt_g_C","wt_g_H","wt_g_S","wt_O","wt_C","wt_H","wt_S",
               "fO2","fH2","fH2O","fS2","fSO2","fH2S","fCO2","fCO","fCH4","fOCS",
               "yO2","yH2","yH2O","yS2","ySO2","yH2S","yCO2","yCO","yCH4","yOCS",
               "M_m_SO","M_m_ox","C_H2O","C_H2","C_CO3","C_CO","C_CH4","C_S","C_SO4","C_H2S",
               "KD1","KHOg","KHOm","KHOSg","KCOg","KCOHg","KOCSg","KSOg","KSOg2"]])
    results_chemistry = pd.concat([results_header, results_chemistry1], ignore_index=True)
    results1 = pd.DataFrame([[PT["P"],PT["T"],mg.xg_O2(run,PT,melt_wf,setup,models),mg.xg_CO(run,PT,melt_wf,setup,models),mg.xg_CO2(run,PT,melt_wf,setup,models),mg.xg_H2(run,PT,melt_wf,setup,models),mg.xg_H2O(run,PT,melt_wf,setup,models),mg.xg_CH4(run,PT,melt_wf,setup,models),mg.xg_S2(run,PT,melt_wf,setup,models),mg.xg_SO2(run,PT,melt_wf,setup,models),mg.xg_H2S(run,PT,melt_wf,setup,models),mg.xg_OCS(run,PT,melt_wf,setup,models),mg.Xg_tot(run,PT,melt_wf,setup,models),
mg.xm_CO2_so(run,melt_wf,setup),mg.xm_H2OT_so(run,melt_wf,setup),mg.Xm_t_so(run,melt_wf,setup),mg.Xm_t_ox(run,melt_wf,setup),
melt_wf["CO2"],melt_wf["H2OT"],wm_H2_,wm_CO_,wm_CH4_,wm_S2m_,wm_SO3_,wm_H2S_,melt_wf["ST"],mg.Fe3Fe2(melt_wf),melt_wf["Fe3FeT"],mg.S6S2(run,PT,melt_wf,setup,models),mg.S6ST(run,PT,melt_wf,setup,models),
mg.fO22Dbuffer(PT,mdv.f_O2(run,PT,melt_wf,setup,models),"FMQ",models),mg.fO22Dbuffer(PT,mdv.f_O2(run,PT,melt_wf,setup,models),"NNO",models),SCSS_,sulfide_sat,SCAS_,sulfate_sat,wt_g_,"","","","",
bulk_wf["O"],bulk_wf["C"],bulk_wf["H"],bulk_wf["S"],
mdv.f_O2(run,PT,melt_wf,setup,models),mg.f_H2(run,PT,melt_wf,setup,models),mg.f_H2O(run,PT,melt_wf,setup,models),mg.f_S2(run,PT,melt_wf,setup,models),mg.f_SO2(run,PT,melt_wf,setup,models),mg.f_H2S(run,PT,melt_wf,setup,models),mg.f_CO2(run,PT,melt_wf,setup,models),mg.f_CO(run,PT,melt_wf,setup,models),mg.f_CH4(run,PT,melt_wf,setup,models),mg.f_OCS(run,PT,melt_wf,setup,models),
mdv.y_O2(PT,models),mdv.y_H2(PT,models),mdv.y_H2O(PT,models),mdv.y_S2(PT,models),mdv.y_SO2(PT,models),mdv.y_SO3(PT,models),mdv.y_H2S(PT,models),mdv.y_CO2(PT,models),mdv.y_CO(PT,models),mdv.y_CH4(PT,models),mdv.y_OCS(PT,models),
mg.M_m_SO(run,melt_wf,setup),mg.M_m_ox(run,melt_wf,setup,models),mdv.C_H2O(run,PT,melt_wf,setup,models),mdv.C_H2(run,PT,melt_wf,setup,models),mdv.C_CO3(run,PT,melt_wf,setup,models),mdv.C_CO(run,PT,melt_wf,setup,models),mdv.C_CH4(run,PT,melt_wf,setup,models),mdv.C_S(run,PT,melt_wf,setup,models),mdv.C_SO4(run,PT,melt_wf,setup,models),mdv.C_H2S(run,PT,melt_wf,setup,models),
mg.KD1(run,PT,setup,models),mdv.KHOg(PT,models),mdv.KHOm(run,PT,melt_wf,setup,models),mdv.KHOSg(PT,models),mdv.KCOg(PT,models),mdv.KCOHg(PT,models),mdv.KOCSg(PT,models),mdv.KOSg(PT,models),mdv.KOSg2(PT,models)]])
    results_chemsitry = pd.concat([results_chemistry, results1], ignore_index=True)
    if models.loc["output csv","option"] == "True":
        results_chemistry.to_csv('results_cooling_chemistry.csv', index=False, header=False)
    
    if models.loc["bulk_O","option"] == "inc S":
        if setup.loc[run,"final_T"] > setup.loc[run,"T_C"]:
            initial = int(round(PT["T"])+1) 
            step = 1 # temperature step in 'C
        elif setup.loc[run,"final_T"] < setup.loc[run,"T_C"]:
            initial = int(round(PT["T"])-1)
            final = int(round(setup.loc[run,"final_T"]))
            step = -1 # temperature step in 'C
    elif models.loc["bulk_O","option"] == "exc S":
        initial = 10
        final = 5000
        step = 10
    
    # run over different temperatures #
    for i in range(initial,final,step): # P is pressure in bars or T is temperature in 'C
        eq_Fe = models.loc["eq_Fe","option"]
        if models.loc["bulk_O","option"] == "inc S":
            T = i/dt_step
            PT["T"] = T
        elif models.loc["bulk_O","option"] == "exc S":
            PT["T"] = setup.loc[run,"T_C"]
            melt_wf["ST"]=i/1000000.
            bulk_wf["S"]=i/1000000.
        
        # work out equilibrium partitioning between melt and gas phase
        fO2_, A, B, C = eq.eq_SOFe_melt(run,PT,bulk_wf,melt_wf,setup,models,nr_step,nr_tol,guessx)
        Fe32, Fe3T, S62, S6T = A
        
        # set melt composition for forward calculation
        wm_CO2_ = melt_wf["CO2"]
        wm_H2O_ = melt_wf["H2OT"]
        wm_H2_, wm_CO_, wm_CH4_, wm_H2S_ = "","","","" 
        melt_wf["Fe3FeT"] = Fe3T
        melt_wf["S6ST"] = S6T
        if models.loc["bulk_O","option"] == "inc S":
            wm_ST_ = wt_S
        elif models.loc["bulk_O","option"] == "exc S":
            wm_ST_ = melt_wf["ST"]
            wm_S = wm_ST_
        melt_wf["S2-"] = wt_S*(1.-S6T)    
        wm_S_ = wt_S*(1.-S6T)
        wm_SO3_ = ((wt_S*S6T)/mdv.species.loc["S","M"])*mdv.species.loc["SO3","M"]
    
        # check for sulfur saturation and display warning in outputs
        SCSS_,sulfide_sat,SCAS_,sulfate_sat, ST_ = sulfur_saturation(run,PT,melt_wf,setup,models)
        if sulfide_sat == "yes":
            warning = "WARNING: sulfide-saturated"
        elif sulfate_sat == "yes":
            warning = "WARNING: sulfate-saturated"
        else:
            warning = ""
        
        # calculate fO2
        if eq_Fe == "yes":
            fO2_ = mdv.f_O2(run,PT,melt_wf,setup,models)
        elif eq_Fe == "no":
            fO2_ = (xg_O2_*mg.y_O2(PT,models)*PT["P"])
            
        guessx = fO2_
            
        # volume, density, and mass
        #gas_mf = {"O2":xg_O2_,"CO":xg_CO_,"S2":xg_S2_,"CO2":xg_CO2_,"H2O":xg_H2O_,"H2":xg_H2_,"CH4":xg_CH4_,"SO2":xg_SO2_,"H2S":xg_H2S_,"OCS":xg_OCS_,"Xg_t":Xg_t,"wt_g":wt_g}
        xg_O2_,xg_CO_,xg_CO2_,xg_H2_,xg_H2O_,xg_CH4_,xg_S2_,xg_SO2_,xg_H2S_,xg_OCS_,Xg_t= "","","","","","","","","","",""
        wt_g,wt_g_O,wt_g_C,wt_g_H,wt_g_S  = "","","","",""
        wt_O_,wt_C_,wt_H_,wt_S_ = wt_O, wt_C, wt_H, wt_S
        
        if models.loc["print status","option"] == "True":
            print(i,fO2_)
        
        # store results
        results2 = pd.DataFrame([[PT["P"],PT["T"],xg_O2_,xg_CO_,xg_CO2_,xg_H2_,xg_H2O_,xg_CH4_,xg_S2_,xg_SO2_,xg_H2S_,xg_OCS_,Xg_t,
               "","","","",
               wm_CO2_,wm_H2O_,wm_H2_,wm_CO_,wm_CH4_,wm_S_,wm_SO3_,wm_H2S_,wm_ST_,Fe32,Fe3T,S62,S6T,
               mg.fO22Dbuffer(PT,fO2_,"FMQ",models),mg.fO22Dbuffer(PT,fO2_,"NNO",models),SCSS_,sulfide_sat,SCAS_,sulfate_sat,
               wt_g,wt_g_O,wt_g_C,wt_g_H,wt_g_S,wt_O_,wt_C_,wt_H_,wt_S_,
fO2_,mg.f_H2(run,PT,melt_wf,setup,models),mg.f_H2O(run,PT,melt_wf,setup,models),mg.f_S2(run,PT,melt_wf,setup,models),mg.f_SO2(run,PT,melt_wf,setup,models),mg.f_SO3(run,PT,melt_wf,setup,models),mg.f_H2S(run,PT,melt_wf,setup,models),mg.f_CO2(run,PT,melt_wf,setup,models),mg.f_CO(run,PT,melt_wf,setup,models),mg.f_CH4(run,PT,melt_wf,setup,models),mg.f_OCS(run,PT,melt_wf,setup,models),
mg.y_O2(PT,models),mg.y_H2(PT,models),mg.y_H2O(PT,models),mg.y_S2(PT,models),mg.y_SO2(PT,models),mg.y_SO3(PT,models),mdv.y_H2S(PT,models),mg.y_CO2(PT,models),mg.y_CO(PT,models),mg.y_CH4(PT,models),mg.y_OCS(PT,models),
mg.M_m_SO(run,melt_wf,setup),mg.M_m_ox(run,melt_wf,setup,models),mg.C_H2O(run,PT,melt_wf,setup,models),mg.C_H2(run,PT,melt_wf,setup,models),mdv.C_CO3(run,PT,melt_wf,setup,models),mg.C_CO(run,PT,melt_wf,setup,models),mg.C_CH4(run,PT,melt_wf,setup,models),mg.C_S(run,PT,melt_wf,setup,models),mg.C_SO4(run,PT,melt_wf,setup,models),mg.C_H2S(run,PT,melt_wf,setup,models),
mg.KD1(run,PT,setup,models),mg.KHOg(PT,models),mg.KHOm(run,PT,melt_wf,setup,models),mg.KHOSg(PT,models),mg.KCOg(PT,models),mg.KCOHg(PT,models),mg.KOCSg(PT,models),mg.KOSg(PT,models),mg.KOSg2(PT,models)]])
        results_chemsitry = pd.concat([results_chemsitry, results2], ignore_index=True)
        if models.loc["output csv","option"] == "True":
            results_chemistry.to_csv('results_cooling_chemistry.csv', index=False, header=False)

    return results

def titratingS(run,cooling_inputs,setup,models):
    if models.loc["print status","option"] == "True":
        print(setup.loc[run,"Sample"])
    
    # check if any options need to be read from the setup file rather than the models file
    models = options_from_setup(run,models,setup)

    # set T, volatile composition of the melt, and tolerances
    PT={"P":setup.loc[run,"P_bar"]}
    PT["T"]=setup.loc[run,"T_C"]
    melt_wf = {'CO2':setup.loc[run,"CO2ppm"]/1000000.,"H2OT":setup.loc[run,"H2O"]/100.,"H2":0.}
    melt_wf["CT"] = (melt_wf["CO2"]/mdv.species.loc["CO2","M"])*mdv.species.loc["C","M"]
    melt_wf["HT"] = (2.*melt_wf["H2OT"]/mdv.species.loc["H2O","M"])*mdv.species.loc["H","M"]
    nr_step = cooling_inputs["nr_step"]
    nr_tol = cooling_inputs["nr_tol"]
    dt_step = cooling_inputs["dt_step"]
    psat_tol = cooling_inputs["psat_tol"]
        
    # Calculate S and Fe composition at initial T and check for sulfur saturation
    melt_wf["Fe3FeT"] = mg.Fe3FeT_i(run,PT,melt_wf,setup,models)
    Fe3Fe2_ = mg.Fe3Fe2(melt_wf)
    melt_wf["CO"] = 0.
    melt_wf["CH4"] = 0.
    melt_wf["H2S"] = 0. 
    wm_H2_, wm_CH4_, wm_H2S_, wm_CO_ = 0., 0., 0., 0.
    melt_wf["ST"] = 0.
    melt_wf["S2-"] = 0.
    melt_wf["S6+"] = 0.
    
    SCSS_,sulfide_sat,SCAS_,sulfate_sat,ST_ = sulfur_saturation(run,PT,melt_wf,setup,models)
    wm_S2m_ = melt_wf["S2-"]
    wm_S6p_ = melt_wf["S6+"]
    wm_SO3_ = (wm_S6p_/(mdv.species.loc["S","M"]))*(mdv.species.loc["S","M"] + 3.*mdv.species.loc["O","M"])
        
    # Set bulk composition
    wt_C, wt_O, wt_H, wt_S, wt_Fe, wt_g_, Wt_ = bulk_composition(run,PT,melt_wf,setup,models)
    
    melt_wf["ST"] = setup.loc[run,"STppm"]/1000000.           
    melt_wf["S6ST"] = mg.S6ST(run,PT,melt_wf,setup,models)
    melt_wf["S2-"] = (1.-melt_wf["S6ST"])*melt_wf["ST"]
    melt_wf["S6+"] = melt_wf["S6ST"]*melt_wf["ST"]     
    wt_S = melt_wf["ST"]
    
    bulk_wf = {"C":wt_C,"H":wt_H,"O":wt_O,"S":wt_S,"Fe":wt_Fe,"Wt":Wt_}
    
    P_sat_, wm_H2O_psat, wm_CO2_psat, wm_H2_psat, wm_CO_psat, wm_CH4_psat, wm_S2m_psat, wm_S6p_psat, wm_H2S_psat, H2O_HTpsat, H2_HTpsat, CH4_HTpsat, H2S_HTpsat, CO2_CTpsat, CO_CTpsat, CH4_CTpsat, S6p_STpsat, S2m_STpsat, H2S_STpsat = P_sat(run,PT,melt_wf,setup,models,psat_tol,nr_step,nr_tol)
    PT["P"] = setup.loc[run,"P_bar"]
    if models.loc["print status","option"] == "True":
        print(P_sat_, PT["P"])
        
    # set system and initial guesses
    system = eq.set_system(melt_wf,models)

    if PT["P"] > P_sat_:
        guessx = mdv.f_O2(run,PT,melt_wf,setup,models)
        fO2_, A, B, C = eq.eq_SOFe_melt(run,PT,bulk_wf,melt_wf,setup,models,nr_step/10.,nr_tol,guessx)
        Fe32, Fe3T, S62, S6T = A
        melt_wf["S6ST"] = S6T
        melt_wf["Fe3FeT"] = Fe3T          
        melt_wf["S2-"] = (1.-melt_wf["S6ST"])*melt_wf["ST"]
        melt_wf["S6+"] = melt_wf["S6ST"]*melt_wf["ST"]
        guessx = mdv.f_O2(run,PT,melt_wf,setup,models)
    else:
        #PT["P"] = P_sat_
        #guessx, guessy, guessz = eq.initial_guesses(run,PT,melt_wf,setup,models,system)
        guessx, guessy, guessz = 3.28098558298437E-10,0.0485362525980284,0.
        #PT["P"] = setup.loc[run,"P_bar"]
        xg, melt, melt_and_gas, guesses, models, solve_species, mass_balance = eq.mg_equilibrium(run,PT,melt_wf,bulk_wf,models,nr_step,nr_tol,guesses)
        guessz = 0.00139401157503231
        
    # create results table
    results_header1 = pd.DataFrame([["System","run","Sample","H2O (mwf)","CO2 (mwf)","ST (mwf)","Fe3FeT","S6ST","O (twf)","C (twf)","H (wtf)","S (twf)","Fe (twf)",
"SiO2 (wt%)","TiO2 (wt%)","Al2O3 (wt%)","FeOT (wt%)","MnO (wt%)","MgO (wt%)","CaO (wt%)","Na2O (wt%)","K2O (wt%)","P2O5 (wt%)",
"oxygen fugacity","carbon dioxide solubility","C speciation composition","water solubility","water speciation","water speciation composition","sulfide solubility","sulfate solubility","ideal gas","carbonylsulfide","bulk composition","equilibrate Fe","starting pressure","gassing direction","gassing style","mass_volume","crystallisation","isotopes","Date"]])
    results_header2 = pd.DataFrame([[system,run,setup.loc[run,"Sample"],melt_wf["H2OT"],melt_wf["CO2"],melt_wf["ST"],melt_wf["Fe3FeT"],"SORT",bulk_wf["O"],bulk_wf["C"],bulk_wf["H"],bulk_wf["S"],bulk_wf["Fe"],
setup.loc[run,"SiO2"],setup.loc[run,"TiO2"],setup.loc[run,"Al2O3"],mg.Wm_FeOT(run,setup),setup.loc[run,"MnO"],setup.loc[run,"MgO"],setup.loc[run,"CaO"],setup.loc[run,"Na2O"],setup.loc[run,"K2O"],setup.loc[run,"P2O5"],
models.loc["fO2","option"],models.loc["carbon dioxide","option"],models.loc["Cspeccomp","option"],models.loc["water","option"],models.loc["Hspeciation","option"],models.loc["Hspeccomp","option"],models.loc["sulfide","option"],models.loc["sulfate","option"],models.loc["ideal_gas","option"],models.loc["carbonylsulfide","option"],models.loc["bulk_composition","option"],models.loc["eq_Fe","option"],models.loc["starting_P","option"],models.loc["gassing_direction","option"],models.loc["gassing_style","option"],models.loc["mass_volume","option"],models.loc["crystallisation","option"],models.loc["isotopes","option"],date.today()]])
    results_header = pd.concat([results_header1, results_header2], ignore_index=True)
    results_chemistry1 = pd.DataFrame([["P","T('C)","xg_O2","xg_CO","xg_CO2","xg_H2","xg_H2O","xg_CH4","xg_S2","xg_SO2","xg_H2S","xg_OCS","Xg_t",
               "xm_CO2","xm_H2O","Xm_t_SO","Xm_t_ox",
               "wm_CO2","wm_H2O","wm_H2","wm_CO","wm_CH4","wm_S","wm_SO3","wm_H2S","wm_ST","Fe32","Fe3T","S62","S6T",
               "DFMQ","DNNO","SCSS","sulfide sat?","SCAS","sulfate sat?","wt_g","wt_g_O","wt_g_C","wt_g_H","wt_g_S","wt_O","wt_C","wt_H","wt_S",
               "fO2","fH2","fH2O","fS2","fSO2","fSO3","fH2S","fCO2","fCO","fCH4","fOCS",
               "yO2","yH2","yH2O","yS2","ySO2","ySO3","yH2S","yCO2","yCO","yCH4","yOCS",
               "M_m_SO","M_m_ox","C_H2O","C_H2","C_CO3","C_CO","C_CH4","C_S","C_SO4","C_H2S",
               "KD1","KHOg","KHOm","KHOSg","KCOg","KCOHg","KOCSg","KSOg","KSOg2"]])
    results_chemistry = pd.concat([results_header, results_chemistry1], ignore_index=True)
    results1 = pd.DataFrame([[PT["P"],PT["T"],mg.xg_O2(run,PT,melt_wf,setup,models),mg.xg_CO(run,PT,melt_wf,setup,models),mg.xg_CO2(run,PT,melt_wf,setup,models),mg.xg_H2(run,PT,melt_wf,setup,models),mg.xg_H2O(run,PT,melt_wf,setup,models),mg.xg_CH4(run,PT,melt_wf,setup,models),mg.xg_S2(run,PT,melt_wf,setup,models),mg.xg_SO2(run,PT,melt_wf,setup,models),mg.xg_H2S(run,PT,melt_wf,setup,models),mg.xg_OCS(run,PT,melt_wf,setup,models),mg.Xg_tot(run,PT,melt_wf,setup,models),
mg.xm_CO2_so(run,melt_wf,setup),mg.xm_H2OT_so(run,melt_wf,setup),mg.Xm_t_so(run,melt_wf,setup),mg.Xm_t_ox(run,melt_wf,setup),
melt_wf["CO2"],melt_wf["H2OT"],wm_H2_,wm_CO_,wm_CH4_,wm_S2m_,wm_SO3_,wm_H2S_,melt_wf["ST"],mg.Fe3Fe2(melt_wf),melt_wf["Fe3FeT"],mg.S6S2(run,PT,melt_wf,setup,models),mg.S6ST(run,PT,melt_wf,setup,models),
mg.fO22Dbuffer(PT,mdv.f_O2(run,PT,melt_wf,setup,models),"FMQ",models),mg.fO22Dbuffer(PT,mdv.f_O2(run,PT,melt_wf,setup,models),"NNO",models),SCSS_,sulfide_sat,SCAS_,sulfate_sat,wt_g_,"","","","",
bulk_wf["O"],bulk_wf["C"],bulk_wf["H"],bulk_wf["S"],
mdv.f_O2(run,PT,melt_wf,setup,models),mg.f_H2(run,PT,melt_wf,setup,models),mg.f_H2O(run,PT,melt_wf,setup,models),mg.f_S2(run,PT,melt_wf,setup,models),mg.f_SO2(run,PT,melt_wf,setup,models),mg.f_SO3(run,PT,melt_wf,setup,models),mg.f_H2S(run,PT,melt_wf,setup,models),mg.f_CO2(run,PT,melt_wf,setup,models),mg.f_CO(run,PT,melt_wf,setup,models),mg.f_CH4(run,PT,melt_wf,setup,models),mg.f_OCS(run,PT,melt_wf,setup,models),
mg.y_O2(PT,models),mg.y_H2(PT,models),mg.y_H2O(PT,models),mg.y_S2(PT,models),mg.y_SO2(PT,models),mg.y_SO3(PT,models),mdv.y_H2S(PT,models),mg.y_CO2(PT,models),mg.y_CO(PT,models),mg.y_CH4(PT,models),mg.y_OCS(PT,models),
mg.M_m_SO(run,melt_wf,setup),mg.M_m_ox(run,melt_wf,setup,models),mg.C_H2O(run,PT,melt_wf,setup,models),mg.C_H2(run,PT,melt_wf,setup,models),mdv.C_CO3(run,PT,melt_wf,setup,models),mg.C_CO(run,PT,melt_wf,setup,models),mg.C_CH4(run,PT,melt_wf,setup,models),mg.C_S(run,PT,melt_wf,setup,models),mg.C_SO4(run,PT,melt_wf,setup,models),mg.C_H2S(run,PT,melt_wf,setup,models),
mg.KD1(run,PT,setup,models),mg.KHOg(PT,models),mg.KHOm(run,PT,melt_wf,setup,models),mg.KHOSg(PT,models),mg.KCOg(PT,models),mg.KCOHg(PT,models),mg.KOCSg(PT,models),mg.KOSg(PT,models),mg.KOSg2(PT,models)]])
    results_chemistry = pd.concat([results_chemistry, results1], ignore_index=True)
    if models.loc["output csv","option"] == "True":
        results_chemistry.to_csv('results_titrating_chemistry.csv', index=False, header=False)
    
    initial = 100
    final = 5000
    step = 100
    
    # run over different S concentrations #
    for i in range(initial,final,step): # P is pressure in bars or T is temperature in 'C
        eq_Fe = models.loc["eq_Fe","option"]

        melt_wf["ST"]=i/1000000.
        bulk_wf["S"]=i/1000000.
        
        system = eq.set_system(melt_wf,models)
        P_sat_, wm_H2O_psat, wm_CO2_psat, wm_H2_psat, wm_CO_psat, wm_CH4_psat, wm_S2m_psat, wm_S6p_psat, wm_H2S_psat, H2O_HTpsat, H2_HTpsat, CH4_HTpsat, H2S_HTpsat, CO2_CTpsat, CO_CTpsat, CH4_CTpsat, S6p_STpsat, S2m_STpsat, H2S_STpsat = P_sat(run,PT,melt_wf,setup,models,psat_tol,nr_step,nr_tol)
        PT["P"]=setup.loc[run,"P_bar"]
        
        # work out equilibrium partitioning between melt and gas phase
        if PT["P"] > P_sat_:
            fO2_, A, B, C = eq.eq_SOFe_melt(run,PT,bulk_wf,melt_wf,setup,models,nr_step,nr_tol,guessx)
            Fe32, Fe3T, S62, S6T = A
            wm_CO2_ = melt_wf["CO2"]
            wm_H2O_ = melt_wf["H2OT"]
            wm_H2_, wm_CO_, wm_CH4_, wm_H2S_ = "","","","" 
            melt_wf["Fe3FeT"] = Fe3T
            melt_wf["S6ST"] = S6T
            wm_ST_ = melt_wf["ST"]
            wm_S = wm_ST_
            melt_wf["S2-"] = wt_S*(1.-S6T) 
            wm_S_ = wt_S*(1.-S6T)
            wm_SO3_ = ((wt_S*S6T)/mdv.species.loc["S","M"])*mdv.species.loc["SO3","M"]
            xg_O2_,xg_CO_,xg_CO2_,xg_H2_,xg_H2O_,xg_CH4_,xg_S2_,xg_SO2_,xg_H2S_,xg_OCS_,Xg_t= "","","","","","","","","","",""
            wt_g,wt_g_O,wt_g_C,wt_g_H,wt_g_S  = 0.,"","","",""
            wt_O_,wt_C_,wt_H_,wt_S_ = wt_O, wt_C, wt_H, wt_S
        else:
            xg, melt, melt_and_gas, guesses, models, solve_species, mass_balance = eq.mg_equilibrium(run,PT,melt_wf,bulk_wf,setup,models,nr_step,nr_tol,guessx,guessy,guessz,guessw)
            melt_wf["Fe3FeT"] = Fe3T
        
        # check for sulfur saturation and display warning in outputs
        SCSS_,sulfide_sat,SCAS_,sulfate_sat, ST_ = sulfur_saturation(run,PT,melt_wf,setup,models)
        if sulfide_sat == "yes":
            warning = "WARNING: sulfide-saturated"
        elif sulfate_sat == "yes":
            warning = "WARNING: sulfate-saturated"
        else:
            warning = ""
        
        # calculate fO2
        if eq_Fe == "yes":
            fO2_ = mdv.f_O2(run,PT,melt_wf,setup,models)
        elif eq_Fe == "no":
            fO2_ = (xg_O2_*mg.y_O2(PT,models)*PT["P"])
            
        if PT["P"] > P_sat_:
            guessx = fO2_
            
        if models.loc["print status","option"] == "True":
            print(i,fO2_)
        
        # store results
        results2 = pd.DataFrame([[PT["P"],PT["T"],xg_O2_,xg_CO_,xg_CO2_,xg_H2_,xg_H2O_,xg_CH4_,xg_S2_,xg_SO2_,xg_H2S_,xg_OCS_,Xg_t,
               "","","","",
               wm_CO2_,wm_H2O_,wm_H2_,wm_CO_,wm_CH4_,wm_S_,wm_SO3_,wm_H2S_,wm_ST_,Fe32,Fe3T,S62,S6T,
               mg.fO22Dbuffer(PT,fO2_,"FMQ",models),mg.fO22Dbuffer(PT,fO2_,"NNO",models),SCSS_,sulfide_sat,SCAS_,sulfate_sat,
               wt_g,wt_g_O,wt_g_C,wt_g_H,wt_g_S,wt_O_,wt_C_,wt_H_,wt_S_,
fO2_,mg.f_H2(run,PT,melt_wf,setup,models),mg.f_H2O(run,PT,melt_wf,setup,models),mg.f_S2(run,PT,melt_wf,setup,models),mg.f_SO2(run,PT,melt_wf,setup,models),mg.f_SO3(run,PT,melt_wf,setup,models),mg.f_H2S(run,PT,melt_wf,setup,models),mg.f_CO2(run,PT,melt_wf,setup,models),mg.f_CO(run,PT,melt_wf,setup,models),mg.f_CH4(run,PT,melt_wf,setup,models),mg.f_OCS(run,PT,melt_wf,setup,models),
mg.y_O2(PT,models),mg.y_H2(PT,models),mg.y_H2O(PT,models),mg.y_S2(PT,models),mg.y_SO2(PT,models),mg.y_SO3(PT,models),mdv.y_H2S(PT,models),mg.y_CO2(PT,models),mg.y_CO(PT,models),mg.y_CH4(PT,models),mg.y_OCS(PT,models),
mg.M_m_SO(run,melt_wf,setup),mg.M_m_ox(run,melt_wf,setup,models),mg.C_H2O(run,PT,melt_wf,setup,models),mg.C_H2(run,PT,melt_wf,setup,models),mdv.C_CO3(run,PT,melt_wf,setup,models),mg.C_CO(run,PT,melt_wf,setup,models),mg.C_CH4(run,PT,melt_wf,setup,models),mg.C_S(run,PT,melt_wf,setup,models),mg.C_SO4(run,PT,melt_wf,setup,models),mg.C_H2S(run,PT,melt_wf,setup,models),
mg.KD1(run,PT,setup,models),mg.KHOg(PT,models),mg.KHOm(run,PT,melt_wf,setup,models),mg.KHOSg(PT,models),mg.KCOg(PT,models),mg.KCOHg(PT,models),mg.KOCSg(PT,models),mg.KOSg(PT,models),mg.KOSg2(PT,models)]])
        results_chemistry = pd.concat([results_chemistry, results2], ignore_index=True)
        if models.loc["output csv","option"] == "True":
            results_chemistry.to_csv('results_titrating_chemistry.csv', index=False, header=False)

    return results_chemistry     
        
##########################
### X% sulfur degassed ###
##########################

def Xpc_S_degassed(first_row,last_row,inputs,setup,models):
     
    if models.loc["fO2","option"] != "Kress91A":
        raise TypeError("Kress91A must be used for fO2 option to be used")
    if models.loc["P_variation","option"] == "isobaric":
        raise TypeError("P_variation must be polybaric")

    nr_step = inputs["nr_step"]
    nr_tol = inputs["nr_tol"]
    psat_tol = inputs["psat_tol"]
    dp_step = inputs["dp_step"]
    
    # create results table
    results_header1 = pd.DataFrame([["oxygen fugacity","carbon dioxide solubility","C speciation composition","water solubility","water speciation","water speciation composition","sulfide solubility","sulfate solubility","ideal gas","carbonylsulfide","bulk composition","equilibrate Fe","starting pressure","gassing direction","gassing style","mass_volume","crystallisation","isotopes","Date"]])
    results_header2 = pd.DataFrame([[models.loc["fO2","option"],models.loc["carbon dioxide","option"],models.loc["Cspeccomp","option"],models.loc["water","option"],models.loc["Hspeciation","option"],models.loc["Hspeccomp","option"],models.loc["sulfide","option"],models.loc["sulfate","option"],models.loc["ideal_gas","option"],models.loc["carbonylsulfide","option"],models.loc["bulk_composition","option"],models.loc["eq_Fe","option"],models.loc["starting_P","option"],models.loc["gassing_direction","option"],models.loc["gassing_style","option"],models.loc["mass_volume","option"],models.loc["crystallisation","option"],models.loc["isotopes","option"],date.today()]])
    results_header = pd.concat([results_header1, results_header2], ignore_index=True)
    results_chemistry1 = pd.DataFrame([["run","Sample","% S degassed","initial fO2 (DFMQ)","H2O (wt%)","CO2 (ppm)","ST (ppm)","X (ppm)","Fe3FeT","S6ST","O (twf)","C (twf)","H (wtf)","S (twf)","Fe (twf)","Saturation P (bars)",
"SiO2 (wt%)","TiO2 (wt%)","Al2O3 (wt%)","FeOT (wt%)","MnO (wt%)","MgO (wt%)","CaO (wt%)","Na2O (wt%)","K2O (wt%)","P2O5 (wt%)","P","T('C)","xg_O2","xg_CO","xg_CO2","xg_H2","xg_H2O","xg_CH4","xg_S2","xg_SO2","xg_H2S","xg_OCS","xg_X","Xg_t","xg_CS",
               "xm_CO2","xm_H2O","Xm_t_SO","Xm_t_ox",
               "wm_CO2-eq","wm_H2O-eq","wm_CO2","wm_H2O","wm_H2","wm_CO","wm_CH4","wm_S","wm_SO3","wm_H2S","wm_ST","wm_X","Fe32","Fe3T","S62","S6T",
               "DFMQ","DNNO","wt_g",
               "fO2"]])
    results_chemistry = pd.concat([results_header, results_chemistry1], ignore_index=True)
    
    for n in range(first_row,last_row,1): # n is number of rows of data in conditions file
        run = n
        
        # check if any options need to be read from the setup file rather than the models file
        models = options_from_setup(run,models,setup)

        # set T, volatile composition of the melt, and tolerances
        PT={"T":setup.loc[run,"T_C"]}
        melt_wf = {'CO2':setup.loc[run,"CO2ppm"]/1000000.,"H2OT":setup.loc[run,"H2O"]/100.,"ST":setup.loc[run,"STppm"]/1000000.,"H2":0.,"XT":setup.loc[run,"Xppm"]/1000000.}
        melt_wf["CT"] = (melt_wf["CO2"]/mdv.species.loc["CO2","M"])*mdv.species.loc["C","M"]
        melt_wf["HT"] = (2.*melt_wf["H2OT"]/mdv.species.loc["H2O","M"])*mdv.species.loc["H","M"]
        melt_wf["ST"] = melt_wf["ST"]
        target_S = melt_wf["ST"]*((100.-setup.loc[run,"Xpc"])/100.)
        if models.loc["print status","option"] == "True":
            print(run,setup.loc[run,"Sample"],melt_wf["ST"]*1000000.,target_S*1000000.,datetime.datetime.now())
        
        # Calculate saturation pressure
        P_sat_, wm_H2O_, wm_CO2_, wm_H2_, wm_CO_, wm_CH4_, wm_S2m_, wm_S6p_, wm_H2S_, H2O_HT, H2_HT, CH4_HT, H2S_HT, CO2_CT, CO_CT, CH4_CT, S6p_ST, S2m_ST, H2S_ST = c.P_sat(run,PT,melt_wf,setup,models,psat_tol,nr_step,nr_tol)
        wm_SO3_ = (wm_S6p_*mdv.species.loc["SO3","M"])/mdv.species.loc["S","M"]
        PT["P"] = P_sat_

        # update melt composition at saturation pressure and check for sulfur saturation
        melt_wf["H2OT"] = wm_H2O_
        melt_wf["CO2"] = wm_CO2_
        melt_wf["CO"] = wm_CO_
        melt_wf["CH4"] = wm_CH4_
        melt_wf["H2"] = wm_H2_
        melt_wf["S2-"] = wm_S2m_
        melt_wf["S6+"] = wm_S6p_
        melt_wf["H2S"] = wm_H2S_
        melt_wf["Fe3FeT"] = mg.Fe3FeT_i(run,PT,melt_wf,setup,models)
        melt_wf["S6ST"] = mg.S6ST(run,PT,melt_wf,setup,models)
    
        # Set bulk composition
        wt_C, wt_O, wt_H, wt_S, wt_X, wt_Fe, wt_g_, Wt_ = c.bulk_composition(run,PT,melt_wf,setup,models)
        bulk_wf = {"C":wt_C,"H":wt_H,"O":wt_O,"S":wt_S,"Fe":wt_Fe,"Wt":Wt_,"X":wt_X}
    
        # set system and initial guesses
        system = eq.set_system(melt_wf,models)
        guessx, guessy, guessz, guessw = eq.initial_guesses(run,PT,melt_wf,setup,models,system)
            
        
        if models.loc["P_variation","option"] == "polybaric":
            # pressure ranges and options
            starting_P = models.loc["starting_P","option"]
            if starting_P == "set":
                initial = int(setup.loc[run,"P_bar"])
            else:
                if models.loc["gassing_direction","option"] == "degas":
                    answer = PT["P"]/dp_step
                    answer = round(answer)
                    initial = round(answer*dp_step)
                elif models.loc["gassing_direction","option"] == "regas":
                    initial = round(PT["P"])+1 
            if models.loc["gassing_direction","option"] == "degas":
                step = int(-1*dp_step) # pressure step in bars
                final = 0
            elif models.loc["gassing_direction","option"] == "regas":
                step = int(dp_step)
                final = int(setup.loc[run,"final_P"])
    
        # add some gas to the system if doing open-system regassing
        if models.loc["gassing_direction","option"] == "regas" and models.loc["gassing_style","option"] == "open":
            gas_mf = {"O2":mg.xg_O2(run,PT,melt_wf,setup,models),"CO":mg.xg_CO(run,PT,melt_wf,setup,models),"CO2":mg.xg_CO2(run,PT,melt_wf,setup,models),"H2":mg.xg_H2(run,PT,melt_wf,setup,models),"H2O":mg.xg_H2O(run,PT,melt_wf,setup,models),"CH4":mg.xg_CH4(run,PT,melt_wf,setup,models),"S2":mg.xg_S2(run,PT,melt_wf,setup,models),"SO2":mg.xg_SO2(run,PT,melt_wf,setup,models),"SO3":mg.xg_SO3(run,PT,melt_wf,setup,models),"H2S":mg.xg_H2S(run,PT,melt_wf,setup,models),"OCS":mg.xg_OCS(run,PT,melt_wf,setup,models),"X":mg.xg_X(run,PT,melt_wf,setup,models),"Xg_t":mg.Xg_tot(run,PT,melt_wf,setup,models),"wt_g":0.}
            wt_C, wt_H, wt_S, wt_X, wt_Fe, wt_O, Wt = new_bulk_regas_open(run,PT,melt_wf,bulk_wf,gas_mf,dwtg,setup,models)
            bulk_wf = {"C":wt_C,"H":wt_H,"O":wt_O,"S":wt_S,"Fe":wt_Fe,"X":wt_X,"Wt":Wt}
    
        # run over different pressures #
        number_of_step = 0.
        
        P = initial
        wm_ST_ = melt_wf["ST"]
        while wm_ST_ > target_S: # step size = initial
            eq_Fe = models.loc["eq_Fe","option"]
            if models.loc["gassing_style","option"] == "open": # check melt is still vapor-saturated
                P_sat_, wm_H2O_, wm_CO2_, wm_H2_, wm_CO_, wm_CH4_, wm_S2m_, wm_S6p_, wm_H2S_, H2O_HT, H2_HT, CH4_HT, H2S_HT, CO2_CT, CO_CT, CH4_CT, S6p_ST, S2m_ST, H2S_ST = c.P_sat(run,PT,melt_wf,setup,models,psat_tol,nr_step,nr_tol)
                wm_SO3_ = (wm_S6p_*mdv.species.loc["SO3","M"])/mdv.species.loc["S","M"]
            P_ = P
            wm_ST__ = wm_ST_
            P = P - dp_step
            PT["P"] = P
            if P_sat_ > PT["P"]:  
                # work out equilibrium partitioning between melt and gas phase
                xg, melt, melt_and_gas, guesses, models, solve_species, mass_balance = eq.mg_equilibrium(run,PT,melt_wf,bulk_wf,setup,models,nr_step,nr_tol,guessx,guessy,guessz,guessw)
                # gas composition
                gas_mf = {"O2":xg_O2_,"CO":xg_CO_,"S2":xg_S2_,"CO2":xg_CO2_,"H2O":xg_H2O_,"H2":xg_H2_,"CH4":xg_CH4_,"SO2":xg_SO2_,"H2S":xg_H2S_,"OCS":xg_OCS_,"X":xg_X_,"Xg_t":Xg_t,"wt_g":wt_g}
            
            else:
                conc = eq.melt_speciation(PT,melt_wf,models,nr_step,nr_tol)
                frac = c.melt_species_ratios(conc)
                wm_ST_ = wm_S_ + wm_S6p_
                S62 = S6T/S2m_ST
                Fe3T = melt_wf["Fe3FeT"]
                Fe32 = mg.overtotal2ratio(Fe3T)
                xg_O2_, xg_H2_, xg_S2_, xg_H2O_, xg_CO_, xg_CO2_, xg_SO2_, xg_CH4_, xg_H2S_, xg_OCS_, xg_X, Xg_t, Xm_t, Xm_t_ox, wt_g_O, wt_g_C, wt_g_H, wt_g_S, wt_g = "","","","","","","","","","","","","","",0.,0.,0.,0.,0.
                guessx, guessy, guessz, guessw = eq.initial_guesses(run,PT,melt_wf,setup,models,system)
        
        P = P_
        wm_ST_ = wm_ST__
        while wm_ST_ > target_S: # step size = 1.
            eq_Fe = models.loc["eq_Fe","option"]
            if models.loc["gassing_style","option"] == "open": # check melt is still vapor-saturated
                P_sat_, wm_H2O_, wm_CO2_, wm_H2_, wm_CO_, wm_CH4_, wm_S2m_, wm_S6p_, wm_H2S_, H2O_HT, H2_HT, CH4_HT, H2S_HT, CO2_CT, CO_CT, CH4_CT, S6p_ST, S2m_ST, H2S_ST = c.P_sat(run,PT,melt_wf,setup,models,psat_tol,nr_step,nr_tol)
                wm_SO3_ = (wm_S6p_*mdv.species.loc["SO3","M"])/mdv.species.loc["S","M"]
            P_ = P
            P = P - 1.
            PT["P"] = P
            if P_sat_ > PT["P"]:  
                # work out equilibrium partitioning between melt and gas phase
                xg, melt, melt_and_gas, guesses, models, solve_species, mass_balance = eq.mg_equilibrium(run,PT,melt_wf,bulk_wf,setup,models,nr_step,nr_tol,guessx,guessy,guessz,guessw)
                # gas composition
                gas_mf = {"O2":xg_O2_,"CO":xg_CO_,"S2":xg_S2_,"CO2":xg_CO2_,"H2O":xg_H2O_,"H2":xg_H2_,"CH4":xg_CH4_,"SO2":xg_SO2_,"H2S":xg_H2S_,"OCS":xg_OCS_,"X":xg_X_,"Xg_t":Xg_t,"wt_g":wt_g}
            
            else:
                conc = eq.melt_speciation(PT,melt_wf,models,nr_step,nr_tol)
                frac = c.melt_species_ratios(conc)
                wm_ST_ = wm_S_ + wm_S6p_
                S62 = S6T/S2m_ST
                Fe3T = melt_wf["Fe3FeT"]
                Fe32 = mg.overtotal2ratio(Fe3T)
                xg_O2_, xg_H2_, xg_S2_, xg_H2O_, xg_CO_, xg_CO2_, xg_SO2_, xg_CH4_, xg_H2S_, xg_OCS_, xg_X, Xg_t, Xm_t, Xm_t_ox, wt_g_O, wt_g_C, wt_g_H, wt_g_S, wt_g = "","","","","","","","","","","","","","",0.,0.,0.,0.,0.
                guessx, guessy, guessz, guessw = eq.initial_guesses(run,PT,melt_wf,setup,models,system)

            
        # set melt composition for forward calculation
        melt_wf["CO2"] = wm_CO2_
        melt_wf["H2OT"] = wm_H2O_
        melt_wf["H2"] = wm_H2_
        melt_wf["CO"] = wm_CO_
        melt_wf["CH4"] = wm_CH4_
        melt_wf["H2S"] = wm_H2S_
        melt_wf["S6+"] = wm_S6p_
        melt_wf["S2-"] = wm_S_
        melt_wf["ST"] = wm_ST_
        melt_wf["XT"] = wm_X_
        melt_wf["Fe3FeT"] = Fe3T
                        
        if P_sat_ < PT["P"]:  
            wt_C_, wt_O_, wt_H_, wt_S_, wt_X_, wt_Fe, wt_g_, Wt_ = c.bulk_composition(run,PT,melt_wf,setup,models)
    
        # check for sulfur saturation and display warning in outputs
        SCSS_,sulfide_sat,SCAS_,sulfate_sat, ST_ = c.sulfur_saturation(run,PT,melt_wf,setup,models)
        if sulfide_sat == "yes":
            warning = "WARNING: sulfide-saturated"
        elif sulfate_sat == "yes":
            warning = "WARNING: sulfate-saturated"
        else:
            warning = ""
        
        # calculate fO2
        if eq_Fe == "yes":
            fO2_ = mdv.f_O2(run,PT,melt_wf,setup,models)
        elif eq_Fe == "no":
            fO2_ = (xg_O2_*mdv.y_O2(PT,models)*PT["P"])
        
        xg_CS = mg.gas_CS(run,PT,melt_wf,setup,models)
        wm_CO2eq, wm_H2Oeq = mg.melt_H2O_CO2_eq(melt_wf)
        
        # store results
        results1 = pd.DataFrame([[run,setup.loc[run,"Sample"],setup.loc[run,"Xpc"],setup.loc[run,"DFMQ"],setup.loc[run,"H2O"],setup.loc[run,"CO2ppm"],setup.loc[run,"STppm"],setup.loc[run,"Xppm"],melt_wf["Fe3FeT"],"SORT",bulk_wf["O"],bulk_wf["C"],bulk_wf["H"],bulk_wf["S"],bulk_wf["Fe"],P_sat_,
setup.loc[run,"SiO2"],setup.loc[run,"TiO2"],setup.loc[run,"Al2O3"],mg.Wm_FeOT(run,setup),setup.loc[run,"MnO"],setup.loc[run,"MgO"],setup.loc[run,"CaO"],setup.loc[run,"Na2O"],setup.loc[run,"K2O"],setup.loc[run,"P2O5"],PT["P"],PT["T"],mg.xg_O2(run,PT,melt_wf,setup,models),mg.xg_CO(run,PT,melt_wf,setup,models),mg.xg_CO2(run,PT,melt_wf,setup,models),mg.xg_H2(run,PT,melt_wf,setup,models),mg.xg_H2O(run,PT,melt_wf,setup,models),mg.xg_CH4(run,PT,melt_wf,setup,models),mg.xg_S2(run,PT,melt_wf,setup,models),mg.xg_SO2(run,PT,melt_wf,setup,models),mg.xg_H2S(run,PT,melt_wf,setup,models),mg.xg_OCS(run,PT,melt_wf,setup,models),mg.xg_X(run,PT,melt_wf,setup,models),mg.Xg_tot(run,PT,melt_wf,setup,models),xg_CS,
mg.xm_CO2_so(run,melt_wf,setup),mg.xm_H2OT_so(run,melt_wf,setup),mg.Xm_t_so(run,melt_wf,setup),"",
wm_CO2eq,wm_H2Oeq,melt_wf["CO2"],melt_wf["H2OT"],wm_H2_,wm_CO_,wm_CH4_,wm_S2m_,wm_SO3_,wm_H2S_,melt_wf["ST"],melt_wf["XT"],mg.Fe3Fe2(melt_wf),melt_wf["Fe3FeT"],mg.S6S2(run,PT,melt_wf,setup,models),mg.S6ST(run,PT,melt_wf,setup,models),
mg.fO22Dbuffer(PT,mdv.f_O2(run,PT,melt_wf,setup,models),"FMQ",models),mg.fO22Dbuffer(PT,mdv.f_O2(run,PT,melt_wf,setup,models),"NNO",models),wt_g,
mdv.f_O2(run,PT,melt_wf,setup,models)]])
        results_chemistry = pd.concat([results_chemistry, results1], ignore_index=True)
        if models.loc["output csv","option"] == "True":
            results_chemistry.to_csv('results_XpcSdegasses.csv', index=False, header=False)

    if models.loc["print status","option"] == "True":            
        print("done", datetime.datetime.now())

    return results  
    
####################
### fO2 at 1 bar ###
####################

def fO2_at_1bar(first_row,last_row,inputs,setup,models):
     
    if models.loc["fO2","option"] != "Kress91A":
        raise TypeError("Kress91A must be used for fO2 option")
    if models.loc["P_variation","option"] == "isobaric":
        raise TypeError("P_variation must be polybaric")

    nr_step = inputs["nr_step"]
    nr_tol = inputs["nr_tol"]
    psat_tol = inputs["psat_tol"]
    P1 = inputs["P1"]
    P2 = inputs["P2"]
    dp_step = inputs["dp_step"]
    
    # create results table
    results_header1 = pd.DataFrame([["oxygen fugacity","carbon dioxide solubility","C speciation composition","water solubility","water speciation","water speciation composition","sulfide solubility","sulfate solubility","ideal gas","carbonylsulfide","bulk composition","equilibrate Fe","starting pressure","gassing direction","gassing style","mass_volume","crystallisation","isotopes","Date"]])
    results_header2 = pd.DataFrame([[models.loc["fO2","option"],models.loc["carbon dioxide","option"],models.loc["Cspeccomp","option"],models.loc["water","option"],models.loc["Hspeciation","option"],models.loc["Hspeccomp","option"],models.loc["sulfide","option"],models.loc["sulfate","option"],models.loc["ideal_gas","option"],models.loc["carbonylsulfide","option"],models.loc["bulk_composition","option"],models.loc["eq_Fe","option"],models.loc["starting_P","option"],models.loc["gassing_direction","option"],models.loc["gassing_style","option"],models.loc["mass_volume","option"],models.loc["crystallisation","option"],models.loc["isotopes","option"],date.today()]])
    results_header = pd.concat([results_header1, results_header2], ignore_index=True)
    results_chemistry1 = pd.DataFrame([["run","Sample","initial fO2 (DFMQ)","H2O (wt%)","CO2 (ppm)","ST (ppm)","X (ppm)","Fe3FeT","S6ST","O (twf)","C (twf)","H (wtf)","S (twf)","Fe (twf)","Saturation P (bars)",
"SiO2 (wt%)","TiO2 (wt%)","Al2O3 (wt%)","FeOT (wt%)","MnO (wt%)","MgO (wt%)","CaO (wt%)","Na2O (wt%)","K2O (wt%)","P2O5 (wt%)","P","T('C)","xg_O2","xg_CO","xg_CO2","xg_H2","xg_H2O","xg_CH4","xg_S2","xg_SO2","xg_H2S","xg_OCS","xg_X","Xg_t","xg_CS",
               "xm_CO2","xm_H2O","Xm_t_SO","Xm_t_ox",
               "wm_CO2-eq","wm_H2O-eq","wm_CO2","wm_H2O","wm_H2","wm_CO","wm_CH4","wm_S","wm_SO3","wm_H2S","wm_ST","wm_X","Fe32","Fe3T","S62","S6T",
               "DFMQ","DNNO","wt_g",
               "fO2","D-DFMQ"]])
    results_chemistry1 = pd.concat([results_header, results_chemistry1], ignore_index=True)
    results_chemistry_P1 = pd.concat([results_header, results_chemistry1], ignore_index=True) 
    results_chemistry_P2 = pd.concat([results_header, results_chemistry1], ignore_index=True)
    
    for n in range(first_row,last_row,1): # n is number of rows of data in conditions file
        run = n
        
        # check if any options need to be read from the setup file rather than the models file
        models = options_from_setup(run,models,setup)

        # set T, volatile composition of the melt, and tolerances
        PT={"T":setup.loc[run,"T_C"]}
        melt_wf = {'CO2':setup.loc[run,"CO2ppm"]/1000000.,"H2OT":setup.loc[run,"H2O"]/100.,"ST":setup.loc[run,"STppm"]/1000000.,"H2":0.,"XT":setup.loc[run,"Xppm"]/1000000.}
        melt_wf["CT"] = (melt_wf["CO2"]/mdv.species.loc["CO2","M"])*mdv.species.loc["C","M"]
        melt_wf["HT"] = (2.*melt_wf["H2OT"]/mdv.species.loc["H2O","M"])*mdv.species.loc["H","M"]
        melt_wf["ST"] = melt_wf["ST"]
        target_S = melt_wf["ST"]*((100.-setup.loc[run,"Xpc"])/100.)
        if models.loc["print status","option"] == "True":
            print(run,setup.loc[run,"Sample"],melt_wf["ST"]*1000000.,target_S*1000000.,datetime.datetime.now())
        
        # Calculate saturation pressure
        P_sat_, wm_H2O_, wm_CO2_, wm_H2_, wm_CO_, wm_CH4_, wm_S2m_, wm_S6p_, wm_H2S_, H2O_HT, H2_HT, CH4_HT, H2S_HT, CO2_CT, CO_CT, CH4_CT, S6p_ST, S2m_ST, H2S_ST = c.P_sat(run,PT,melt_wf,setup,models,psat_tol,nr_step,nr_tol)
        wm_SO3_ = (wm_S6p_*mdv.species.loc["SO3","M"])/mdv.species.loc["S","M"]
        PT["P"] = P_sat_

        # update melt composition at saturation pressure and check for sulfur saturation
        melt_wf["H2OT"] = wm_H2O_
        melt_wf["CO2"] = wm_CO2_
        melt_wf["CO"] = wm_CO_
        melt_wf["CH4"] = wm_CH4_
        melt_wf["H2"] = wm_H2_
        melt_wf["S2-"] = wm_S2m_
        melt_wf["S6+"] = wm_S6p_
        melt_wf["H2S"] = wm_H2S_
        melt_wf["Fe3FeT"] = mg.Fe3FeT_i(run,PT,melt_wf,setup,models)
        melt_wf["S6ST"] = mg.S6ST(run,PT,melt_wf,setup,models)
    
        # Set bulk composition
        wt_C, wt_O, wt_H, wt_S, wt_X, wt_Fe, wt_g_, Wt_ = c.bulk_composition(run,PT,melt_wf,setup,models)
        bulk_wf = {"C":wt_C,"H":wt_H,"O":wt_O,"S":wt_S,"Fe":wt_Fe,"Wt":Wt_,"X":wt_X}
    
        # set system and initial guesses
        system = eq.set_system(melt_wf,models)
        guessx, guessy, guessz, guessw = eq.initial_guesses(run,PT,melt_wf,setup,models,system)
            
        
        if models.loc["P_variation","option"] == "polybaric":
            # pressure ranges and options
            starting_P = models.loc["starting_P","option"]
            if starting_P == "set":
                initial = int(setup.loc[run,"P_bar"])
            else:
                if models.loc["gassing_direction","option"] == "degas":
                    answer = PT["P"]/dp_step
                    answer = math.floor(answer)
                    initial = round(answer*dp_step)
                elif models.loc["gassing_direction","option"] == "regas":
                    initial = round(PT["P"])+1 
            if models.loc["gassing_direction","option"] == "degas":
                step = int(-1*dp_step) # pressure step in bars
                final = 0
            elif models.loc["gassing_direction","option"] == "regas":
                step = int(dp_step)
                final = int(setup.loc[run,"final_P"])
    
        # add some gas to the system if doing open-system regassing
        if models.loc["gassing_direction","option"] == "regas" and models.loc["gassing_style","option"] == "open":
            gas_mf = {"O2":mg.xg_O2(run,PT,melt_wf,setup,models),"CO":mg.xg_CO(run,PT,melt_wf,setup,models),"CO2":mg.xg_CO2(run,PT,melt_wf,setup,models),"H2":mg.xg_H2(run,PT,melt_wf,setup,models),"H2O":mg.xg_H2O(run,PT,melt_wf,setup,models),"CH4":mg.xg_CH4(run,PT,melt_wf,setup,models),"S2":mg.xg_S2(run,PT,melt_wf,setup,models),"SO2":mg.xg_SO2(run,PT,melt_wf,setup,models),"SO3":mg.xg_SO3(run,PT,melt_wf,setup,models),"H2S":mg.xg_H2S(run,PT,melt_wf,setup,models),"OCS":mg.xg_OCS(run,PT,melt_wf,setup,models),"X":mg.xg_X(run,PT,melt_wf,setup,models),"Xg_t":mg.Xg_tot(run,PT,melt_wf,setup,models),"wt_g":0.}
            wt_C, wt_H, wt_S, wt_X, wt_Fe, wt_O, Wt = new_bulk_regas_open(run,PT,melt_wf,bulk_wf,gas_mf,dwtg,setup,models)
            bulk_wf = {"C":wt_C,"H":wt_H,"O":wt_O,"S":wt_S,"Fe":wt_Fe,"X":wt_X,"Wt":Wt}
    
        # run over different pressures #
        number_of_step = 0.
        
        P = initial
        wm_ST_ = melt_wf["ST"]
        for i in range(initial,final,step):
            eq_Fe = models.loc["eq_Fe","option"]
            if models.loc["gassing_style","option"] == "open": # check melt is still vapor-saturated
                P_sat_, wm_H2O_, wm_CO2_, wm_H2_, wm_CO_, wm_CH4_, wm_S2m_, wm_S6p_, wm_H2S_, H2O_HT, H2_HT, CH4_HT, H2S_HT, CO2_CT, CO_CT, CH4_CT, S6p_ST, S2m_ST, H2S_ST = c.P_sat(run,PT,melt_wf,setup,models,psat_tol,nr_step,nr_tol)
                wm_SO3_ = (wm_S6p_*mdv.species.loc["SO3","M"])/mdv.species.loc["S","M"]
            P_ = P
            wm_ST__ = wm_ST_
            P = P - dp_step
            if P <= 0.:
                P = 1
            PT["P"] = P
            if P_sat_ > PT["P"]:  
                # work out equilibrium partitioning between melt and gas phase
                xg, melt, melt_and_gas, guesses, models, solve_species, mass_balance = eq.mg_equilibrium(run,PT,melt_wf,bulk_wf,setup,models,nr_step,nr_tol,guessx,guessy,guessz,guessw)
                # gas composition
                gas_mf = {"O2":xg_O2_,"CO":xg_CO_,"S2":xg_S2_,"CO2":xg_CO2_,"H2O":xg_H2O_,"H2":xg_H2_,"CH4":xg_CH4_,"SO2":xg_SO2_,"H2S":xg_H2S_,"OCS":xg_OCS_,"X":xg_X_,"Xg_t":Xg_t,"wt_g":wt_g}
            
            else:
                conc = eq.melt_speciation(PT,melt_wf,models,nr_step,nr_tol)
                frac = c.melt_species_ratios(conc)
                wm_ST_ = wm_S_ + wm_S6p_
                S62 = S6T/S2m_ST
                Fe3T = melt_wf["Fe3FeT"]
                Fe32 = mg.overtotal2ratio(Fe3T)
                xg_O2_, xg_H2_, xg_S2_, xg_H2O_, xg_CO_, xg_CO2_, xg_SO2_, xg_CH4_, xg_H2S_, xg_OCS_, xg_X, Xg_t, Xm_t, Xm_t_ox, wt_g_O, wt_g_C, wt_g_H, wt_g_S, wt_g = "","","","","","","","","","","","","","",0.,0.,0.,0.,0.
                guessx, guessy, guessz, guessw = eq.initial_guesses(run,PT,melt_wf,setup,models,system)
        
            if P == 1 or P == P1 or P == P2:
                # set melt composition for forward calculation
                melt_wf["CO2"] = wm_CO2_
                melt_wf["H2OT"] = wm_H2O_
                melt_wf["H2"] = wm_H2_
                melt_wf["CO"] = wm_CO_
                melt_wf["CH4"] = wm_CH4_
                melt_wf["H2S"] = wm_H2S_
                melt_wf["S6+"] = wm_S6p_
                melt_wf["S2-"] = wm_S_
                melt_wf["ST"] = wm_ST_
                melt_wf["XT"] = wm_X_
                melt_wf["Fe3FeT"] = Fe3T
                        
                if P_sat_ < PT["P"]:  
                    wt_C_, wt_O_, wt_H_, wt_S_, wt_X_, wt_Fe, wt_g_, Wt_ = c.bulk_composition(run,PT,melt_wf,setup,models)
    
                # check for sulfur saturation and display warning in outputs
                SCSS_,sulfide_sat,SCAS_,sulfate_sat, ST_ = c.sulfur_saturation(run,PT,melt_wf,setup,models)
                if sulfide_sat == "yes":
                    warning = "WARNING: sulfide-saturated"
                elif sulfate_sat == "yes":
                    warning = "WARNING: sulfate-saturated"
                else:
                    warning = ""
        
                # calculate fO2
                if eq_Fe == "yes":
                    fO2_ = mdv.f_O2(run,PT,melt_wf,setup,models)
                elif eq_Fe == "no":
                    fO2_ = (xg_O2_*mdv.y_O2(PT,models)*PT["P"])
        
                xg_CS = mg.gas_CS(run,PT,melt_wf,setup,models)
                wm_CO2eq, wm_H2Oeq = mg.melt_H2O_CO2_eq(melt_wf)                
    
                # store results
                results1 = pd.DataFrame([[run,setup.loc[run,"Sample"],setup.loc[run,"DFMQ"],setup.loc[run,"H2O"],setup.loc[run,"CO2ppm"],setup.loc[run,"STppm"],setup.loc[run,"Xppm"],melt_wf["Fe3FeT"],"SORT",bulk_wf["O"],bulk_wf["C"],bulk_wf["H"],bulk_wf["S"],bulk_wf["Fe"],P_sat_,
setup.loc[run,"SiO2"],setup.loc[run,"TiO2"],setup.loc[run,"Al2O3"],mg.Wm_FeOT(run,setup),setup.loc[run,"MnO"],setup.loc[run,"MgO"],setup.loc[run,"CaO"],setup.loc[run,"Na2O"],setup.loc[run,"K2O"],setup.loc[run,"P2O5"],PT["P"],PT["T"],mg.xg_O2(run,PT,melt_wf,setup,models),mg.xg_CO(run,PT,melt_wf,setup,models),mg.xg_CO2(run,PT,melt_wf,setup,models),mg.xg_H2(run,PT,melt_wf,setup,models),mg.xg_H2O(run,PT,melt_wf,setup,models),mg.xg_CH4(run,PT,melt_wf,setup,models),mg.xg_S2(run,PT,melt_wf,setup,models),mg.xg_SO2(run,PT,melt_wf,setup,models),mg.xg_H2S(run,PT,melt_wf,setup,models),mg.xg_OCS(run,PT,melt_wf,setup,models),mg.xg_X(run,PT,melt_wf,setup,models),mg.Xg_tot(run,PT,melt_wf,setup,models),xg_CS,
mg.xm_CO2_so(run,melt_wf,setup),mg.xm_H2OT_so(run,melt_wf,setup),mg.Xm_t_so(run,melt_wf,setup),"",
wm_CO2eq,wm_H2Oeq,melt_wf["CO2"],melt_wf["H2OT"],wm_H2_,wm_CO_,wm_CH4_,wm_S2m_,wm_SO3_,wm_H2S_,melt_wf["ST"],melt_wf["XT"],mg.Fe3Fe2(melt_wf),melt_wf["Fe3FeT"],mg.S6S2(run,PT,melt_wf,setup,models),mg.S6ST(run,PT,melt_wf,setup,models),
mg.fO22Dbuffer(PT,mdv.f_O2(run,PT,melt_wf,setup,models),"FMQ",models),mg.fO22Dbuffer(PT,mdv.f_O2(run,PT,melt_wf,setup,models),"NNO",models),wt_g,
mdv.f_O2(run,PT,melt_wf,setup,models),setup.loc[run,"DFMQ"]-mg.fO22Dbuffer(PT,mdv.f_O2(run,PT,melt_wf,setup,models),"FMQ",models)]])
                
                if P == P1:
                    results_chemistry_P1 = pd.concat([results_chemistry_P1, results1], ignore_index=True)
                    if models.loc["output csv","option"] == "True":
                        results_chemistry_P1.to_csv('results_P1.csv', index=False, header=False)
                if P == P2:
                    results_chemistry_P1 = pd.concat([results_chemistry_P2, results1], ignore_index=True)
                    if models.loc["output csv","option"] == "True":
                        results_chemistry_P2.to_csv('results_P2.csv', index=False, header=False)
                if P == 1:
                    results_chemistry_1 = pd.concat([results_chemistry_1, results1], ignore_index=True)
                    if models.loc["output csv","option"] == "True":
                        results_chemistry_1.to_csv('results_1bar.csv', index=False, header=False)
    if models.loc["print status","option"] == "True":            
        print("done", datetime.datetime.now()) 
    return results_chemistry_P1, results_chemistry_P2, results_chemistry_1