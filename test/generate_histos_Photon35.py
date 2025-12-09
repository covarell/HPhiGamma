import ROOT
import argparse
import math
import numpy as np
import sys
import copy
import tdrstyle, CMS_lumi


#bools
debug = False #Bool for verbose

#Supress the opening of many Canvas's
ROOT.gROOT.SetBatch(True)   

#INPUT and OUTPUT #############################################################################################
#Input
p = argparse.ArgumentParser(description='Select rootfile to plot')
p.add_argument('is_Data', help='Type which kind of sample it is')
p.add_argument('rootfile_name', help='Type rootfile name')
p.add_argument('outputfile_option', help='Provide output file name')

args = p.parse_args()
fInput = ROOT.TFile(args.rootfile_name)
mytree = fInput.Get("HPhiGammaTriggerAnalysis/mytree")

if args.is_Data == "Data":
    CONST_NAME = "Data"
else:
    CONST_NAME = "MC"

#Output
output_filename = args.outputfile_option
fOut = ROOT.TFile(output_filename,"RECREATE")
fOut.cd()

#Normalization for MC dataset ################################################################################
normalization_InputFile = open("rootfiles/latest_production/MC/normalizations/Normalizations_table_Photon30.txt","r")
norm_map = dict()
for line in normalization_InputFile:
    data_norm = line.split()
    norm_map[data_norm[0]] = float(data_norm[1])

normalization_weight = norm_map["DY50"]
print "normalization_weight = ",normalization_weight
luminosity = 57.22 #activity of Photon30 trigger in 2018

#HISTOS ###########################################################################################################
nBins = 10
histo_map = dict()
list_histos = ["h_mass_mumu","h_gamma_eT","h_nPhotonTriggered_eT","h_nPhotonOffline_eT","h_triggerEff_eT","h_mass_mumuGamma"]

histo_map[list_histos[0]]  = ROOT.TH1F(list_histos[0],"M_{#mu#mu} in "+CONST_NAME+" (Photon leg)",100,20.,120.)
histo_map[list_histos[1]]  = ROOT.TH1F(list_histos[1],"E_{T}^{#gamma} in "+CONST_NAME+" (Photon leg)", 100, 38.,160.)
histo_map[list_histos[2]]  = ROOT.TH1F(list_histos[2],"n. events #gamma triggered as function of E_{#gamma} in "+CONST_NAME+" (Photon leg)", nBins, 38.,90.)
histo_map[list_histos[3]]  = ROOT.TH1F(list_histos[3],"n. events #gamma over offline selection as function of E_{#gamma} in "+CONST_NAME+" (Photon leg)", nBins, 38.,90.)
histo_map[list_histos[4]]  = ROOT.TH1F(list_histos[4],"Trigger efficiency as function of E_{#gamma} in "+CONST_NAME+" (Photon leg)", nBins, 38.,90.)
histo_map[list_histos[5]]  = ROOT.TH1F(list_histos[5],"M_{#mu#mu#gamma} in "+CONST_NAME+" (Photon leg)",100,20.,120.)

#VARIABLES INITIALIZATION ##################################################################################################
nEventsIsoMuTrigger    = 0
nEventsPhotonTrigger   = 0
nEventsPhoton35Trigger = 0
nEventsOfflinePhoton   = 0
nEventsGenMatched      = 0
nEventsNotMatched      = 0
nEventsGenMatchedTriggered = 0
nEventsNotMatchedTriggered = 0
nEventsGenIsMuon       = 0
nEventsGenIsElectron   = 0
nEventsGenIsPi0        = 0
nEventsGenIsTau        = 0
nEventsGenIsK0S        = 0
triggerFraction        = 0

#EVENTS LOOP ##################################################################################################################### 
print "This sample has ", mytree.GetEntriesFast(), " events"
nentries = mytree.GetEntriesFast()

for jentry in xrange(nentries):
    ientry = mytree.LoadTree( jentry )
    if ientry < 0:
        break
    nb = mytree.GetEntry(jentry )
    if nb <= 0:
        continue

    #Retrieve variables from the tree and fill the histos
    MuMuMass              = mytree.MuMuMass
    MuMuGammaMass         = mytree.MuMuGammaMass
    gammaEt               = mytree.photon_eT
    isIsoMuTrigger        = mytree.isIsoMuTrigger
    isPhoton30Mu17Trigger = mytree.isPhotonTrigger      
    isPhoton35Trigger     = mytree.isPhoton35Trigger      
    isbestPhotonFound     = mytree.cand_photon_found
    gammaEta              = mytree.photon_eta
    if CONST_NAME == "MC": genID = mytree.genID

    #if not CONST_NAME == "Data" :
     #   eventWeight = luminosity * normalization_weight
    #else:
    eventWeight = 1.
    
    if isbestPhotonFound == 0: continue

    if gammaEt < 38.: continue

    #if (MuMuMass < 20. or MuMuMass > 120.): continue #this is the nominal approach
    if (MuMuGammaMass < 85. or MuMuGammaMass > 95.): continue #this is for the Z->mumugamma approach to remove the most of the fake photons

    if abs(gammaEta) > 2.1: continue
    #if abs(gammaEta) < 1.444: continue #Barrel
    #if abs(gammaEta) < 1.566: continue #Endcap


    if debug:
        print ""
        print "Processing EVENT n.",jentry+1,"================"
        print "isIsoMuTrigger        = ",isIsoMuTrigger
        print "isPhoton30Mu17Trigger = ",isPhoton30Mu17Trigger
        print "isbestPhotonFound     = ",isbestPhotonFound
        print "mumuGamma mass        = ",MuMuGammaMass
    
    if isIsoMuTrigger:
        nEventsIsoMuTrigger    = nEventsIsoMuTrigger  + 1
    if isPhoton30Mu17Trigger:
        nEventsPhotonTrigger   = nEventsPhotonTrigger + 1
    if isPhoton35Trigger:
        nEventsPhoton35Trigger = nEventsPhoton35Trigger + 1
    if isbestPhotonFound:
        nEventsOfflinePhoton   = nEventsOfflinePhoton + 1
        if CONST_NAME == "MC":
            if genID == 22: 
                nEventsGenMatched = nEventsGenMatched + 1
            else: 
                nEventsNotMatched = nEventsNotMatched + 1

            if debug: print "genID = ",genID

    histo_map["h_mass_mumu"].Fill(MuMuMass,eventWeight)
    histo_map["h_mass_mumuGamma"].Fill(MuMuGammaMass,eventWeight)
    histo_map["h_gamma_eT"].Fill(gammaEt)
    #if isPhoton30Mu17Trigger:
    if isPhoton35Trigger:
        histo_map["h_nPhotonTriggered_eT"].Fill(gammaEt)
        histo_map["h_triggerEff_eT"].Fill(gammaEt) #create the histo starting from the numerator
        if CONST_NAME == "MC":
            if genID == 22: 
                nEventsGenMatchedTriggered = nEventsGenMatchedTriggered + 1
            else:
                nEventsNotMatchedTriggered = nEventsNotMatchedTriggered + 1

            if abs(genID) == 13: nEventsGenIsMuon     = nEventsGenIsMuon + 1
            if abs(genID) == 11: nEventsGenIsElectron = nEventsGenIsElectron + 1
            if genID == 111: nEventsGenIsPi0          = nEventsGenIsPi0 + 1
            if abs(genID) == 15: nEventsGenIsTau      = nEventsGenIsTau + 1
            if genID == 310: nEventsGenIsK0S          = nEventsGenIsK0S + 1

    if isbestPhotonFound: histo_map["h_nPhotonOffline_eT"].Fill(gammaEt)

#TRIGGER EFFICIENCY CALCULATION ###################################################################################################
triggerFraction = float(nEventsPhotonTrigger)/float(nEventsOfflinePhoton)

#trigger efficiency as function of photon transverse energy -------------------------------------------------------------
histo_map["h_triggerEff_eT"].Divide(histo_map["h_nPhotonOffline_eT"]) #divide it by the denominator
#histo_map["h_triggerEff_eT"].Scale(100.) #multiply for the percentage

#CALCULATE EFFICIENCY ERRORS ########################################################
print "##########################################"
for bin_index in range(1,nBins):
    
    N = histo_map["h_nPhotonOffline_eT"].GetBinContent(bin_index)
    epsilon = histo_map["h_triggerEff_eT"].GetBinContent(bin_index)
    error = math.sqrt(epsilon * (1 - epsilon) * (1/N))
    
    print "For bin ",bin_index,": N = ",N,", eff = ",epsilon, " and efficiency error = ",error

    histo_map["h_triggerEff_eT"].SetBinError(bin_index,error)
print "##########################################"



print "########################################"
print CONST_NAME + " sample"
print "nEventsPhotonTrigger    = ",nEventsPhotonTrigger
print "nEventsPhoton35Trigger  = ",nEventsPhoton35Trigger
print "nEventsOfflinePhoton    = ",nEventsOfflinePhoton
print ""
if CONST_NAME == "MC":
    print "nEventsGenMatchedTrig   = ",nEventsGenMatchedTriggered
    print "nEventsNotMatchedTrig   = ",nEventsNotMatchedTriggered
    print "Fake phot. ratio trig(%)= ",100*nEventsNotMatchedTriggered/(nEventsGenMatchedTriggered+nEventsNotMatchedTriggered)
    print ""    
    print "nEventsGenMatched       = ",nEventsGenMatched
    print "nEventsNotMatched       = ",nEventsNotMatched
    print "Fake phot. ratio (%)    = ",100*nEventsNotMatched/(nEventsGenMatched+nEventsNotMatched)
    print ""
    print "nEventsGenIsMuon        = ",nEventsGenIsMuon
    print "nEventsGenIsElectron    = ",nEventsGenIsElectron
    print "nEventsGenIsPi0         = ",nEventsGenIsPi0
    print "nEventsGenIsTau         = ",nEventsGenIsTau
    print "nEventsGenIsK0S         = ",nEventsGenIsK0S
print "########################################"

print "Total trigger fraction = ",triggerFraction

#HISTO LABELS #####################################################################################################################
histo_map["h_mass_mumu"].GetXaxis().SetTitle("m_{#mu^{+}#mu^{-}} [GeV]")
histo_map["h_mass_mumuGamma"].GetXaxis().SetTitle("m_{#mu^{+}#mu^{-}#gamma} [GeV]")

histo_map["h_gamma_eT"].GetXaxis().SetTitle("E^{#gamma}_{T} [GeV]")

histo_map["h_nPhotonTriggered_eT"].GetXaxis().SetTitle("E^{#gamma}_{T} [GeV]")
histo_map["h_nPhotonTriggered_eT"].GetYaxis().SetTitle("n. #gamma triggered")

histo_map["h_nPhotonOffline_eT"].GetXaxis().SetTitle("E^{#gamma}_{T} [GeV]")
histo_map["h_nPhotonOffline_eT"].GetYaxis().SetTitle("n. offline #gamma")

histo_map["h_triggerEff_eT"].GetXaxis().SetTitle("E^{#gamma}_{T} [GeV]")
histo_map["h_triggerEff_eT"].GetYaxis().SetTitle("Trigger efficiency")

# HISTOS WRITING #########################################################################
fOut.cd()
for hist_name in list_histos:
    histo_map[hist_name].Write()

c0 = ROOT.TCanvas()
c0.cd()
ROOT.gStyle.SetPaintTextFormat("4.2f %")
ROOT.gStyle.SetOptStat(0)
histo_map["h_mass_mumuGamma"].SetMarkerSize(1.4)
histo_map["h_mass_mumuGamma"].GetXaxis().SetRangeUser(20.,120.)
#histo_map["h_mass_mumuGamma"].GetYaxis().SetRangeUser(0.,30.)
histo_map["h_mass_mumuGamma"].Draw("")
c0.SaveAs("/eos/user/g/gumoret/www/latest_production/trigger_efficiency_latest_production/h_photonLeg_mass_mumuGamma_"+CONST_NAME+".pdf")
c0.SaveAs("/eos/user/g/gumoret/www/latest_production/trigger_efficiency_latest_production/h_photonLeg_mass_mumuGamma_"+CONST_NAME+".png") 

c1 = ROOT.TCanvas()
c1.cd()
ROOT.gStyle.SetPaintTextFormat("4.2f %")
ROOT.gStyle.SetOptStat(0)
histo_map["h_mass_mumu"].SetMarkerSize(1.4)
histo_map["h_mass_mumu"].GetXaxis().SetRangeUser(20.,120.)
#histo_map["h_mass_mumu"].GetYaxis().SetRangeUser(0.,30.)
histo_map["h_mass_mumu"].Draw("")
c1.SaveAs("/eos/user/g/gumoret/www/latest_production/trigger_efficiency_latest_production/h_photonLeg_mass_mumu_"+CONST_NAME+".pdf")
c1.SaveAs("/eos/user/g/gumoret/www/latest_production/trigger_efficiency_latest_production/h_photonLeg_mass_mumu_"+CONST_NAME+".png")  

c2 = ROOT.TCanvas()
c2.cd()
#ROOT.gStyle.SetPaintTextFormat("4.2f %")
#ROOT.gStyle.SetOptStat(0)
#histo_map["h_gamma_eT"].SetMarkerSize(1.4)
histo_map["h_gamma_eT"].GetXaxis().SetRangeUser(20.,120.)
#histo_map["h_gamma_eT"].GetYaxis().SetRangeUser(0.,30.)
histo_map["h_gamma_eT"].Draw("")
c2.SaveAs("/eos/user/g/gumoret/www/latest_production/trigger_efficiency_latest_production/h_gamma_eT_"+CONST_NAME+".png") 
c2.SaveAs("/eos/user/g/gumoret/www/latest_production/trigger_efficiency_latest_production/h_gamma_eT_"+CONST_NAME+".pdf") 

c3 = ROOT.TCanvas()
c3.cd()
ROOT.gStyle.SetOptStat(0)
histo_map["h_nPhotonTriggered_eT"].Draw("")
c3.SaveAs("/eos/user/g/gumoret/www/latest_production/trigger_efficiency_latest_production/h_nPhotonTriggered_eT_"+CONST_NAME+".pdf")
c3.SaveAs("/eos/user/g/gumoret/www/latest_production/trigger_efficiency_latest_production/h_nPhotonTriggered_eT_"+CONST_NAME+".png") 

c4 = ROOT.TCanvas()
c4.cd()
ROOT.gStyle.SetOptStat(0)
histo_map["h_nPhotonOffline_eT"].Draw("")
c4.SaveAs("/eos/user/g/gumoret/www/latest_production/trigger_efficiency_latest_production/h_nPhotonOffline_eT_"+CONST_NAME+".pdf")
c4.SaveAs("/eos/user/g/gumoret/www/latest_production/trigger_efficiency_latest_production/h_nPhotonOffline_eT_"+CONST_NAME+".png") 

c3 = ROOT.TCanvas()
c3.cd()
ROOT.gStyle.SetOptStat(0)
#ROOT.gStyle.SetPaintTextFormat("4.2f %")
histo_map["h_triggerEff_eT"].GetYaxis().SetRangeUser(0.,1.)
histo_map["h_triggerEff_eT"].Draw("")
c3.SaveAs("/eos/user/g/gumoret/www/latest_production/trigger_efficiency_latest_production/h_triggerEff_eT_"+CONST_NAME+".pdf")
c3.SaveAs("/eos/user/g/gumoret/www/latest_production/trigger_efficiency_latest_production/h_triggerEff_eT_"+CONST_NAME+".png") 

fOut.Close()
