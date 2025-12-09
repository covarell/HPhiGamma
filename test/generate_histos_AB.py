import ROOT
import argparse
import math
import numpy as np
import sys
from array import array
from functions_smuggler import Simplified_Workflow_Handler

#bools
debug          = False #Bool for verbose
#isSys          = True

#Following bools are given as input
isDataBlind    = False #Bool for blind analysis
isBDT          = False #BDT bool
isPhiAnalysis  = False # for H -> Phi Gammatefun
isRhoAnalysis  = False # for H -> Rho Gamma
isK0sAnalysis  = False # for H -> K0star Gamma
isPhotonEtaCat = False # for barrel and endcap categories
isGenStudies   = False
isVBFSynch     = False
#Supress the opening of many Canvas's
ROOT.gROOT.SetBatch(True)   

# PARSER and INPUT #############################################################################################
p = argparse.ArgumentParser(description='Select rootfile to plot')
p.add_argument('Decay_channel_option', help='Type <<Phi>> for Phi, <<Rho>> for Rho') #flag for bkg estimation
p.add_argument('CR_option', help='Type <<0>> for SR, <<1>> for CR') #flag for bkg estimation
p.add_argument('isBDT_option', help='Type <<preselection>> or <<BDT>>') #flag for loose selection or tight selection (from BDT output)
p.add_argument('isBlindAnalysis', help='Type <<blind>> or <<unblind>>') #flag for loose selection or tight selection (from BDT output)
p.add_argument("isEtaCat",help='Type the photon eta category',default='noPhotonEtaCat')
p.add_argument('rootfile_name', help='Type rootfile name')
p.add_argument('outputfile_option', help='Provide output file name')

args = p.parse_args()
fInput = ROOT.TFile(args.rootfile_name)
output_filename = args.outputfile_option
mytree = fInput.Get("HPhiGammaAnalysis/mytree")
h_Events = fInput.Get("HPhiGammaAnalysis/h_Events")

#Trigger eff scale factors
fInput_TwoProngsTriggerSF = ROOT.TFile("scale_factors/TwoProngsTriggerSF.root") 
fInput_PhotonTriggerSF    = ROOT.TFile("scale_factors/Photon35TriggerSF_FSR.root") #Photon35 is the new histo containing SFs calculated changing the Photon eT threshold to 35 GeV at HLT level
fInput_IsoChSF_barrel     = ROOT.TFile("scale_factors/IsoChEfficiencySF_barrel.root") 
fInput_IsoChSF_endcap     = ROOT.TFile("scale_factors/IsoChEfficiencySF_endcap.root") 
fInput_IsoNeuSF_barrel    = ROOT.TFile("scale_factors/IsoNeuEfficiencySF_barrel.root") 
fInput_IsoNeuSF_endcap    = ROOT.TFile("scale_factors/IsoNeuEfficiencySF_endcap.root") 
h_TwoProngsTriggerSF = fInput_TwoProngsTriggerSF.Get("h_efficiency_Data")
h_PhotonTriggerSF    = fInput_PhotonTriggerSF.Get("h_triggerEff_eT")
h_IsoChSF_barrel     = fInput_IsoChSF_barrel.Get("h_efficiency_Data")
h_IsoChSF_endcap     = fInput_IsoChSF_endcap.Get("h_efficiency_Data")
h_IsoNeuSF_barrel    = fInput_IsoNeuSF_barrel.Get("h_efficiency_Data")
h_IsoNeuSF_endcap    = fInput_IsoNeuSF_endcap.Get("h_efficiency_Data")

#Bools ######################################################################################################
print "################################################################################"

#SPLIT: I can split a string of chars before and after a split code (that could be a string or a symbol)
#then I can take the string standing before or after with [0] or [1], respectively. 
#[:-n] is not an emoji, it deletes last n symbols from the string
samplename =(args.rootfile_name.split("HPhiGammaAnalysis_")[1])[:-5] 
print "samplename =", samplename

if args.Decay_channel_option == "Phi":
    isPhiAnalysis = True
    print "H -> PhiGamma analysis"
if args.Decay_channel_option == "Rho": 
    isRhoAnalysis = True
    print "H -> RhoGamma analysis"
if args.Decay_channel_option == "K0s": 
    isK0sAnalysis = True
    print "H -> K0sGamma analysis"

if args.isBlindAnalysis == "blind":
    isDataBlind = True
    print "isDataBlind = ",isDataBlind

CRflag = int(args.CR_option)
if CRflag > 0 :
    print "Processing the control region ", CRflag
else :
    print "Processing the signal region" 

if (args.isBDT_option == "BDT0" or args.isBDT_option == "BDT1" or args.isBDT_option == "custom"):
    isBDT = True
    fInputBDT = ROOT.TFile("MVA/BDToutput.root","READ")
    BDTtree = fInputBDT.Get("BDTtree")
    BDTtree.GetEntry(0)
    BDT_OUT = BDTtree._BDT_output
    #BDT_OUT = 0.
    print "BDT_OUT = ",BDT_OUT
    fInputBDT.Close()

if (args.isEtaCat == "EB" or args.isEtaCat == "EE"):
    isPhotonEtaCat = True
    PHOTONCAT = args.isEtaCat
else:
    PHOTONCAT = "No photon cat"


print "Category = ",args.isBDT_option, ", ",PHOTONCAT
print "-----------------------------------------------"

if not samplename == "Data":
    #choose production mode
    PROD = samplename.split("_")[2]

    #Pol weight files
    if(isPhiAnalysis): 
        if PROD == "ggH": fInput_pol = ROOT.TFile("/eos/user/g/gumoret/useful_files/HPhiGammaAOD_Signal_Phi_ggH.root")
        if PROD == "VBF": fInput_pol = ROOT.TFile("/eos/user/g/gumoret/useful_files/HPhiGammaAOD_Signal_Phi_VBF_2018_M125.root")
        tree_pol = fInput_pol.Get("HPhiGammaAOD/mytree")
    if(isRhoAnalysis): 
        if PROD == "ggH": fInput_pol = ROOT.TFile("/eos/user/g/gumoret/useful_files/HRhoGammaAnalysis_Signal_Rho_ggH_AOD.root")
        if PROD == "VBF": fInput_pol = ROOT.TFile("/eos/user/g/gumoret/useful_files/HRhoGammaAnalysis_Signal_Rho_VBF_2018_M125_AOD.root")
        tree_pol = fInput_pol.Get("HRhoGammaAOD/mytree")
    if(isK0sAnalysis): 
        if PROD == "ggH": fInput_pol = ROOT.TFile("/eos/user/g/gumoret/useful_files/HK0sgammaAnalysis_Signal_K0s_ggH.root")
        if PROD == "VBF": fInput_pol = ROOT.TFile("/eos/user/g/gumoret/useful_files/HK0sgammaAnalysis_Signal_K0s_VBF_2018_M125.root")
        tree_pol = fInput_pol.Get("HK0sGammaAOD/mytree")

    # Create the theta polarization dictionary
    theta_pol_dict = {}
    n_entries = tree_pol.GetEntriesFast()
    for jentry in range(n_entries):
        ientry = tree_pol.LoadTree(jentry)
        if ientry < 0:
            break
        nb = tree_pol.GetEntry(jentry)
        if nb <= 0:
            continue
        theta_pol_dict[tree_pol.event_number] = tree_pol.theta_pol

################################################################################################################
myWF = Simplified_Workflow_Handler("Signal","Data",isBDT)

#Normalization for MC dataset ################################################################################
if not samplename == "Data":
    normalization_InputFile = open("rootfiles/latest_production/MC/normalizations/Normalizations_table.txt","r")
    norm_map = dict()
    for line in normalization_InputFile:
        data_norm = line.split()
        norm_map[data_norm[0]] = float(data_norm[1])

    normalization_weight = norm_map[samplename]

    #Combine luminosity
    #luminosity2018A = 14.00 #fb^-1
    #luminosity2018B = 3.41 #fb^-1   
    #luminosity2018C = 6.94 #fb^-1
    #luminosity2018D = 31.93 #fb^-1
    luminosity = 39.54 #total lumi delivered during the trigger activity: 39.54 #fb^-1

if not samplename == "Data":
    weightSum = 0.
else: weightSum = 1.


#HISTOS ###########################################################################################################
histo_map = dict()
list_histos = ["h_InvMass_TwoTrk_Photon","h_meson_InvMass_TwoTrk","h_firstTrk_pT","h_secondTrk_pT","h_firstTrk_Eta","h_secondTrk_Eta","h_firstTrk_Phi","h_secondTrk_Phi","h_bestCouplePt","h_bestCoupleEta","h_bestCoupleDeltaR","h_bestJetPt","h_bestJetEta","h_firstTrk_Iso","h_firstTrk_Iso_ch","h_secondTrk_Iso","h_secondTrk_Iso_ch","h_couple_Iso","h_couple_Iso_ch","h_photon_energy","h_photon_eta","h_nJets_25","h_nMuons","h_nElectrons","h_nPhotons38WP80","h_efficiency","h_decayChannel","h_couple_Iso_neutral","h_cutOverflow","h_met_pT","h_dPhiGammaTrk","h_nPhotons15WP90barrel","h_pTOverHmass","h_eTOverHmass","h_JetChargedEmEnergy","h_JetNeutralEmEnergy","h_JetChargedHadEnergy","h_JetNeutralHadEnergy","h_massResolution","h_genPhotonEt","h_genMesonPt","h_MrecoMinusMgen","h_isoSumPtNeu","h_nPhotons25WP90endcap","h_nPhotons20WP90eta2p5","h_theta_pol","h_deltaRGammaTrk","h_deltaEtaGammaTrk","h_K_pT","h_Pi_pT","h_H_pT","h_IsoSumPt","h_IsoSumPtVsJetPt","h_IsoSumPtVsMesonPt","h_photon_HoverE","h_photon_hadTowOverEm"]
if not isK0sAnalysis: 
    list_histos.remove("h_K_pT")
    list_histos.remove("h_Pi_pT")

histo_map[list_histos[0]]  = ROOT.TH1F(list_histos[0],"M_{H}",140,100.,170.) 
if   isPhiAnalysis: histo_map[list_histos[1]]  = ROOT.TH1F(list_histos[1],"M_{meson}", 100, 1., 1.05) 
elif isRhoAnalysis: histo_map[list_histos[1]]  = ROOT.TH1F(list_histos[1],"M_{meson}", 100, 0.5, 1.) 
elif isK0sAnalysis: histo_map[list_histos[1]]  = ROOT.TH1F(list_histos[1],"M_{meson}", 100, 0.8, 1.) 
histo_map[list_histos[2]]  = ROOT.TH1F(list_histos[2],"p_{T} of the 1st track", 100, 20.,60.)
if   isPhiAnalysis: histo_map[list_histos[3]]  = ROOT.TH1F(list_histos[3],"p_{T} of the 2nd track", 100, 11.,55.)
elif isRhoAnalysis: histo_map[list_histos[3]]  = ROOT.TH1F(list_histos[3],"p_{T} of the 2nd track", 100, 5.,50.)
elif isK0sAnalysis: histo_map[list_histos[3]]  = ROOT.TH1F(list_histos[3],"p_{T} of the 2nd track", 100, 5.,50.)
histo_map[list_histos[4]]  = ROOT.TH1F(list_histos[4],"#eta of the 1st track", 100, -2.5,2.5)
histo_map[list_histos[5]]  = ROOT.TH1F(list_histos[5],"#eta of the 2nd track", 100, -2.5,2.5)
histo_map[list_histos[6]]  = ROOT.TH1F(list_histos[6],"#phi of the 1st track", 100, -3.14,3.14)
histo_map[list_histos[7]]  = ROOT.TH1F(list_histos[7],"#phi of the 2nd track", 100, -3.14,3.14)
histo_map[list_histos[8]]  = ROOT.TH1F(list_histos[8],"p_{T} of the meson", 100, 38.,110.)
histo_map[list_histos[9]]  = ROOT.TH1F(list_histos[9],"#eta_{meson}", 100, -2.5,2.5)
if   isPhiAnalysis: histo_map[list_histos[10]] = ROOT.TH1F(list_histos[10],"#Delta R_{meson}", 100, 0.,0.026)
elif isRhoAnalysis: histo_map[list_histos[10]] = ROOT.TH1F(list_histos[10],"#Delta R_{meson}", 100, 0.,0.07)
elif isK0sAnalysis: histo_map[list_histos[10]] = ROOT.TH1F(list_histos[10],"#Delta R_{meson}", 100, 0.,0.07)
histo_map[list_histos[11]] = ROOT.TH1F(list_histos[11],"p_{T} of the jet", 100, 30.,170.)
histo_map[list_histos[12]] = ROOT.TH1F(list_histos[12],"#eta of the jet", 100, -2.5,2.5)
histo_map[list_histos[13]] = ROOT.TH1F(list_histos[13],"Iso of the 1st track", 100, 0.45,1.)
histo_map[list_histos[14]] = ROOT.TH1F(list_histos[14],"Iso_ch of the 1st track", 100, 0.8,1.)
histo_map[list_histos[15]] = ROOT.TH1F(list_histos[15],"Iso of the 2nd track", 100, 0.3,1.)
histo_map[list_histos[16]] = ROOT.TH1F(list_histos[16],"Iso_ch of the 2nd track", 100, 0.75,1.)
histo_map[list_histos[17]] = ROOT.TH1F(list_histos[17],"Iso of the meson", 100, 0.6,1.)
histo_map[list_histos[18]] = ROOT.TH1F(list_histos[18],"Iso_ch of the meson", 100, 0.9,1.)
histo_map[list_histos[19]] = ROOT.TH1F(list_histos[19],"E_{T} of the #gamma", 100, 38.,160.)
histo_map[list_histos[20]] = ROOT.TH1F(list_histos[20],"#eta_{#gamma}", 100, -2.5,2.5)
histo_map[list_histos[21]] = ROOT.TH1F(list_histos[21],"n. of jets over pre-filters",  7, -0.5,6.5)
histo_map[list_histos[22]] = ROOT.TH1F(list_histos[22],"n. of muons", 6, -0.5,5.5)
histo_map[list_histos[23]] = ROOT.TH1F(list_histos[23],"n. of electrons", 5, -0.5,4.5)
histo_map[list_histos[24]] = ROOT.TH1F(list_histos[24],"n. of #gamma 38wp80", 6, -0.5,5.5)
histo_map[list_histos[25]] = ROOT.TH1F(list_histos[25],"Efficiency steps", 7, 0.,7.)
histo_map[list_histos[26]] = ROOT.TH1F(list_histos[26],"Phi or Rho channel", 2, -0.5,1.5)
if isBDT: histo_map[list_histos[27]] = ROOT.TH1F(list_histos[27],"Iso_neutral of the meson", 100, 0.8,1.)
else: histo_map[list_histos[27]] = ROOT.TH1F(list_histos[27],"Iso_neutral of the meson", 100, 0.6,1.)
histo_map[list_histos[28]] = ROOT.TH1F(list_histos[28],"Data cut overflow", 5, 0.,5.)
histo_map[list_histos[29]] = ROOT.TH1F(list_histos[29],"p_{T} of the met", 200, 0.,120.)
histo_map[list_histos[30]] = ROOT.TH1F(list_histos[30],"#Delta#phi between leading track and photon", 100, 0.,3.14)
histo_map[list_histos[31]] = ROOT.TH1F(list_histos[31],"n. of #gamma 15wp90 barrel", 6, -0.5,5.5)
histo_map[list_histos[32]] = ROOT.TH1F(list_histos[32],"p_{T} of the meson divided by m_{ditrk#gamma}", 100, 0.2,0.75)
histo_map[list_histos[33]] = ROOT.TH1F(list_histos[33],"E_{T} of the #gamma divided by m_{ditrk#gamma}", 100, 0.2,1.1)
histo_map[list_histos[34]] = ROOT.TH1F(list_histos[34],"Charged em energy of the jet", 100, 0.,0.001)
histo_map[list_histos[35]] = ROOT.TH1F(list_histos[35],"Neutral em energy of the jet", 10, 0.,0.7)
histo_map[list_histos[36]] = ROOT.TH1F(list_histos[36],"Charged had energy of the jet", 100, 0.,1.)
histo_map[list_histos[37]] = ROOT.TH1F(list_histos[37],"Neutral had energy of the jet", 100, 0.,0.4)
histo_map[list_histos[38]] = ROOT.TH1F(list_histos[38],"Mass resolution", 100, 0.,0.1)
histo_map[list_histos[39]] = ROOT.TH1F(list_histos[39],"genPhoton eT", 100, 38.,160.)
histo_map[list_histos[40]] = ROOT.TH1F(list_histos[40],"genMeson pT", 100, 38.,110.)
histo_map[list_histos[41]] = ROOT.TH1F(list_histos[41],"mMesonReco - mMesonGen", 100, -0.04,0.04)
histo_map[list_histos[42]] = ROOT.TH1F(list_histos[42],"Neutral energy of the isolation cone", 100, 0.,20.)
histo_map[list_histos[43]] = ROOT.TH1F(list_histos[43],"n. of #gamma 25wp90 endcap", 6, -0.5,5.5)
histo_map[list_histos[44]] = ROOT.TH1F(list_histos[44],"n. of #gamma 20 high eta", 6, -0.5,5.5)
histo_map[list_histos[45]] = ROOT.TH1F(list_histos[45],"theta pol", 100, -1.,1.)
histo_map[list_histos[46]] = ROOT.TH1F(list_histos[46],"deltaR gamma leading trk", 100, 0.,4.)
histo_map[list_histos[47]] = ROOT.TH1F(list_histos[47],"#Delta#eta #gamma leading trk", 100, -5.,5.)
histo_map[list_histos[48]] = ROOT.TH1F(list_histos[48],"Higgs transverse momentum", 100, 70.,300.)
histo_map[list_histos[49]] = ROOT.TH1F(list_histos[49],"sum pT inside the isolation cone", 100, 0.,100.)
histo_map[list_histos[50]] = ROOT.TH2F(list_histos[50],"sum pT inside the iso cone vs jet pT;IsoSumPt;JetPt", 100, 0.,100.,100,35.,170.)
histo_map[list_histos[51]] = ROOT.TH2F(list_histos[51],"sum pT inside the iso cone vs meson pT;IsoSumPt;MesonPt", 100, 0.,100.,100,38.,170.)
histo_map[list_histos[52]] = ROOT.TH1F(list_histos[52],"Photon H over E", 100, 0.,0.12)
histo_map[list_histos[53]] = ROOT.TH1F(list_histos[53],"Photon H over E tower", 100, 0.,0.04)
if isK0sAnalysis:
    histo_map[list_histos[54]] = ROOT.TH1F(list_histos[54],"p_{T} of the Kaon", 100, 5.,70.)
    histo_map[list_histos[55]] = ROOT.TH1F(list_histos[55],"p_{T} of the Pion", 100, 5.,70.)

#histo_map[list_histos[29]] = ROOT.TH1F(list_histos[29],"BDT output", 40, -1.,1.)

#CREATE OUTPUT ROOTFILE ##################################################################################################
fOut = ROOT.TFile(output_filename,"RECREATE")
fOut.cd()

#Variables to go in the output tree #############################################################################################
mesonGammaMass       = np.zeros(1, dtype=float)   
massResolution       = np.zeros(1, dtype=float)
mesonMass            = np.zeros(1, dtype=float)
_coupleIsoCh         = np.zeros(1, dtype=float)
_coupleIso           = np.zeros(1, dtype=float)
_coupleIso0          = np.zeros(1, dtype=float)
_bestJetPt           = np.zeros(1, dtype=float)
_bestCouplePt        = np.zeros(1, dtype=float)
_firstTrkPt          = np.zeros(1, dtype=float)
_secondTrkPt         = np.zeros(1, dtype=float)
_photonEt            = np.zeros(1, dtype=float)
_HpT                 = np.zeros(1, dtype=float)
_firstTrkIso         = np.zeros(1, dtype=float)  
_secondTrkIso        = np.zeros(1, dtype=float)  
_firstTrkIsoCh       = np.zeros(1, dtype=float)  
_secondTrkIsoCh      = np.zeros(1, dtype=float) 
_firstTrkEta         = np.zeros(1, dtype=float)  
_secondTrkEta        = np.zeros(1, dtype=float)  
_bestCoupleEta       = np.zeros(1, dtype=float)  
_bestCoupleDeltaR    = np.zeros(1, dtype=float) 
_photonEta           = np.zeros(1, dtype=float)  
_eventWeight         = np.zeros(1, dtype=float)
_BDTweight           = np.zeros(1, dtype=float)
_BDTdisc             = np.zeros(1, dtype=float)
_metPt               = np.zeros(1, dtype=float)
_nJets               = np.zeros(1, dtype=float)
_nPV                 = np.zeros(1, dtype=int)
_dPhiGammaTrk        = np.zeros(1, dtype=float)
_runNumber           = np.zeros(1, dtype=float)
_eventNumber         = np.zeros(1, dtype=float)
_JetChargedEmEnergy  = np.zeros(1, dtype=float)
_JetNeutralEmEnergy  = np.zeros(1, dtype=float)
_JetChargedHadEnergy = np.zeros(1, dtype=float)
_JetNeutralHadEnergy = np.zeros(1, dtype=float)

tree_output = ROOT.TTree('tree_output','tree_output')
tree_output.Branch('mesonGammaMass',mesonGammaMass,'mesonGammaMass/D')
tree_output.Branch('massResolution',massResolution,'massResolution/D')
tree_output.Branch('mesonMass',mesonMass,'mesonMass/D')
tree_output.Branch('_coupleIsoCh',_coupleIsoCh,'_coupleIsoCh/D')
tree_output.Branch('_coupleIso',_coupleIso,'_coupleIso/D')
tree_output.Branch('_coupleIso0',_coupleIso0,'_coupleIso0/D')
tree_output.Branch('_bestJetPt',_bestJetPt,'_bestJetPt/D')
tree_output.Branch('_bestCouplePt',_bestCouplePt,'_bestCouplePt/D')
tree_output.Branch('_firstTrkPt',_firstTrkPt,'_firstTrkPt/D')
tree_output.Branch('_secondTrkPt',_secondTrkPt,'_secondTrkPt/D')
tree_output.Branch('_photonEt',_photonEt,'_photonEt/D')
tree_output.Branch('_firstTrkIso',_firstTrkIso,'_firstTrkIso/D')
tree_output.Branch('_firstTrkIsoCh',_firstTrkIsoCh,'_firstTrkIsoCh/D')
tree_output.Branch('_secondTrkIso',_secondTrkIso,'_secondTrkIso/D')
tree_output.Branch('_secondTrkIsoCh',_secondTrkIsoCh,'_secondTrkIsoCh/D')
tree_output.Branch('_firstTrkEta',_firstTrkEta,'_firstTrkEta/D')
tree_output.Branch('_secondTrkEta',_secondTrkEta,'_secondTrkEta/D')
tree_output.Branch('_bestCoupleEta',_bestCoupleEta,'_bestCoupleEta/D')
tree_output.Branch('_bestCoupleDeltaR',_bestCoupleDeltaR,'_bestCoupleDeltaR/D')
tree_output.Branch('_photonEta',_photonEta,'_photonEta/D')
tree_output.Branch('_eventWeight',_eventWeight,'_eventWeight/D')
tree_output.Branch('_BDTweight',_BDTweight,'_BDTweight/D')
tree_output.Branch('_BDTdisc',_BDTdisc,'_BDTdisc/D')
tree_output.Branch('_metPt',_metPt,'_metPt/D')
tree_output.Branch('_nJets',_nJets,'_nJets/D')
tree_output.Branch('_dPhiGammaTrk',_dPhiGammaTrk,'_dPhiGammaTrk/D')
tree_output.Branch('_runNumber',_runNumber,'_runNumber/D')
tree_output.Branch('_eventNumber',_eventNumber,'_eventNumber/D')
tree_output.Branch('_JetChargedEmEnergy',_JetChargedEmEnergy,'_JetChargedEmEnergy/D')
tree_output.Branch('_JetNeutralEmEnergy',_JetNeutralEmEnergy,'_JetNeutralEmEnergy/D')
tree_output.Branch('_JetChargedHadEnergy',_JetChargedHadEnergy,'_JetChargedHadEnergy/D')
tree_output.Branch('_JetNeutralHadEnergy',_JetNeutralHadEnergy,'_JetNeutralHadEnergy/D')
tree_output.Branch('_HpT',_HpT,'_HpT/D')
tree_output.Branch('_nPV',_nPV,'_nPV/I')

if not isBDT:
    tree_output_forMVA = ROOT.TTree('tree_output_forMVA','tree_output_forMVA')
    tree_output_forMVA.Branch('mesonGammaMass',mesonGammaMass,'mesonGammaMass/D')
    tree_output_forMVA.Branch('massResolution',massResolution,'massResolution/D')
    tree_output_forMVA.Branch('mesonMass',mesonMass,'mesonMass/D')
    tree_output_forMVA.Branch('_coupleIsoCh',_coupleIsoCh,'_coupleIsoCh/D')
    tree_output_forMVA.Branch('_coupleIso',_coupleIso,'_coupleIso/D')
    tree_output_forMVA.Branch('_coupleIso0',_coupleIso0,'_coupleIso0/D')
    tree_output_forMVA.Branch('_bestJetPt',_bestJetPt,'_bestJetPt/D')
    tree_output_forMVA.Branch('_bestCouplePt',_bestCouplePt,'_bestCouplePt/D')
    tree_output_forMVA.Branch('_firstTrkPt',_firstTrkPt,'_firstTrkPt/D')
    tree_output_forMVA.Branch('_secondTrkPt',_secondTrkPt,'_secondTrkPt/D')
    tree_output_forMVA.Branch('_photonEt',_photonEt,'_photonEt/D')
    tree_output_forMVA.Branch('_firstTrkIso',_firstTrkIso,'_firstTrkIso/D')
    tree_output_forMVA.Branch('_firstTrkIsoCh',_firstTrkIsoCh,'_firstTrkIsoCh/D')
    tree_output_forMVA.Branch('_secondTrkIso',_secondTrkIso,'_secondTrkIso/D')
    tree_output_forMVA.Branch('_secondTrkIsoCh',_secondTrkIsoCh,'_secondTrkIsoCh/D')
    tree_output_forMVA.Branch('_firstTrkEta',_firstTrkEta,'_firstTrkEta/D')
    tree_output_forMVA.Branch('_secondTrkEta',_secondTrkEta,'_secondTrkEta/D')
    tree_output_forMVA.Branch('_bestCoupleEta',_bestCoupleEta,'_bestCoupleEta/D')
    tree_output_forMVA.Branch('_bestCoupleDeltaR',_bestCoupleDeltaR,'_bestCoupleDeltaR/D')
    tree_output_forMVA.Branch('_photonEta',_photonEta,'_photonEta/D')
    tree_output_forMVA.Branch('_eventWeight',_eventWeight,'_eventWeight/D')
    tree_output_forMVA.Branch('_BDTweight',_BDTweight,'_BDTweight/D')
    tree_output_forMVA.Branch('_BDTdisc',_BDTdisc,'_BDTdisc/D')
    tree_output_forMVA.Branch('_metPt',_metPt,'_metPt/D')
    tree_output_forMVA.Branch('_nJets',_nJets,'_nJets/D')
    tree_output_forMVA.Branch('_dPhiGammaTrk',_dPhiGammaTrk,'_dPhiGammaTrk/D')
    tree_output_forMVA.Branch('_runNumber',_runNumber,'_runNumber/D')
    tree_output_forMVA.Branch('_eventNumber',_eventNumber,'_eventNumber/D')
    tree_output_forMVA.Branch('_JetChargedEmEnergy',_JetChargedEmEnergy,'_JetChargedEmEnergy/D')
    tree_output_forMVA.Branch('_JetNeutralEmEnergy',_JetNeutralEmEnergy,'_JetNeutralEmEnergy/D')
    tree_output_forMVA.Branch('_JetChargedHadEnergy',_JetChargedHadEnergy,'_JetChargedHadEnergy/D')
    tree_output_forMVA.Branch('_JetNeutralHadEnergy',_JetNeutralHadEnergy,'_JetNeutralHadEnergy/D')
    tree_output_forMVA.Branch('_HpT',_HpT,'_HpT/D')
    tree_output_forMVA.Branch('_nPV',_nPV,'_nPV/I')


print "This sample has ", mytree.GetEntriesFast(), " events"
nentries = mytree.GetEntriesFast()

#------------- counters -----------------
nEventsMesonAnalysis      = 0
nEventsOverLeptonVeto     = 0
nEventsOverDiPhotonVeto   = 0
nEventsOverVBFOrt         = 0
nEventsAfterRegionDefiner = 0
nEventsInHmassRange       = 0
nEventsOverCuts           = 0
nEventsLeftSB             = 0
nEventsRightSB            = 0
nTrkPlusMatched           = 0
nTrkMinusMatched          = 0
nPhotonMatched            = 0
nHmatched                 = 0
nMesonMatched             = 0
nHiggsFound               = 0
nMesonPtMatched           = 0
nMesonPtNotMatched        = 0
nPhotonEtMatched          = 0
nPhotonEtNotMatched       = 0
nLeadingTrkMatched        = 0
nLeadingTrkNotMatched     = 0
nSubleadingTrkMatched     = 0
nSubleadingTrkNotMatched  = 0
nOneTrkMatched            = 0
nEventsPhotonLowEff       = 0
nEventsKpt20              = 0
TwoProngsTriggerSystDW    = 0
TwoProngsTriggerSystUP    = 0
PhotonTriggerSystDW       = 0
PhotonTriggerSystUP       = 0
PhotonIDSystDW            = 0
PhotonIDSystUP            = 0

#EVENTS LOOP ##################################################################################################################### 
for jentry in xrange(nentries):
    ientry = mytree.LoadTree( jentry )
    if ientry < 0:
        break
    nb = mytree.GetEntry(jentry)
    if nb <= 0:
        print "nb < 0"
        continue

    
    if debug: 
        print "Processing EVENT n.",jentry+1," ..."

    #Retrieve variables from the tree 
    if isPhiAnalysis: Hmass = mytree._PhiGammaMass
    if isRhoAnalysis: Hmass = mytree._RhoGammaMass
    if isK0sAnalysis: Hmass = mytree._K0starGammaMass
    if isPhiAnalysis: MesonMass = mytree._PhiMass
    if isRhoAnalysis: MesonMass = mytree._RhoMass
    if isK0sAnalysis: MesonMass = mytree._K0starMass
    MesonIsoCh     = mytree.iso_couple_ch
    jetPt          = mytree.bestJet_pT      
    MesonPt        = mytree.bestCouplePt      
    firstTrkPt     = mytree.firstCandPt         
    secondTrkPt    = mytree.secondCandPt        
    photonEt       = mytree.photon_eT
    HiggsPt        = photonEt + MesonPt        
    massResolution = mytree.photonRegressionError/photonEt #calculated as photonErr / photonEt 
    phEt_sigmaDW   = mytree.photon_eT_sigmaDW
    phEt_sigmaUP   = mytree.photon_eT_sigmaUP
    phET_scaleDW   = mytree.photon_eT_scaleDW
    phET_scaleUP   = mytree.photon_eT_scaleUP
    #ph_HoverE      = mytree.photon_HoverE
    #ph_hadTowOverEm= mytree.photon_hadTowOverEm
    ph_HoverE      = 1.
    ph_hadTowOverEm= 1.
    firstTrketa    = mytree.firstCandEta
    secondTrketa   = mytree.secondCandEta
    firstTrkphi    = mytree.firstCandPhi
    secondTrkphi   = mytree.secondCandPhi
    jetEta         = mytree.bestJet_eta
    MesonIso       = mytree.iso_couple
    firstTrkiso    = mytree.iso_K1
    firstTrkisoCh  = mytree.iso_K1_ch
    secondTrkiso   = mytree.iso_K2
    secondTrkisoCh = mytree.iso_K2_ch
    photonEta      = mytree.photon_eta
    nJets          = mytree.nJets25
    MesonEta       = mytree.bestCoupleEta
    isPhiEvent     = mytree.isPhi
    isRhoEvent     = mytree.isRho
    isK0sEvent     = mytree.isK0star
    isTrigger      = mytree.isTwoProngTrigger
    nElectrons     = mytree.nElectrons10
    nMuons         = mytree.nMuons10
    MesonIso0      = MesonPt/(MesonPt + (mytree.Couple_sum_pT_05 - mytree.Couple_sum_pT_05_ch))
    IsoSumPt       = mytree.Couple_sum_pT_05
    metPt          = mytree.met_pT
    isoSumPtNeu    = mytree.Couple_sum_pT_05 - mytree.Couple_sum_pT_05_ch 
    nPV            = mytree.nPV
    nPhotons38WP80              = mytree.nPhotons38WP80
    nPhotonsWP90_pT15_barrel    = mytree.nPhotonsWP90_pT15_barrel
    nPhotonsWP90_pT25_endcap    = mytree.nPhotonsWP90_pT25_endcap
    nPhotonsWP90_pT20_2p5eta3p0 = mytree.nPhotonsWP90_pT20_2p5eta3p0

    # Trigger studies ------------------- 
    if not isTrigger: continue
    #if MesonPt < 100.: continue
    
    if isBDT: 
        if MesonIso0 < 0.8:  continue
    
    # -----------------------------------

    dPhiGammaTrk   = math.fabs(firstTrkphi - mytree.photon_phi)
    if dPhiGammaTrk > 3.14:
        dPhiGammaTrk = 6.28 - dPhiGammaTrk
    dEtaGammaTrk   = firstTrketa - mytree.photon_eta

    deltaRGammaTrk = math.sqrt(dPhiGammaTrk * dPhiGammaTrk + dEtaGammaTrk * dEtaGammaTrk)

    JetChargedEmEn = mytree.bestJet_chargedEmEnergyFraction
    JetNeutralEmEn = mytree.bestJet_neutralEmEnergyFraction
    JetChargedHadEn= (mytree.bestJet_chargedHadEnergy - MesonPt)/jetPt
    JetNeutralHadEn= mytree.bestJet_neutralHadEnergyFraction

    if samplename == "Data":
        eventNumber    = mytree.event_number
        runNumber      = mytree.run_number
    else:
        isHiggsMatched  = mytree.isHiggsMatched
        isPhotonMatched = mytree.isPhotonMatched
        genPhotonEt     = mytree.genPhoton_eT
        genMesonPt      = mytree.genMeson_pT
        genMesonMass    = mytree.genMeson_m

    #If I'm performing a PhiGamma analysis I don't want to choose those events tagged as a RhoGamma events, and viceversa
    if isPhiAnalysis and not isPhiEvent: continue
    if isRhoAnalysis and not isRhoEvent: continue
    if isK0sAnalysis and not isK0sEvent: continue

    nEventsMesonAnalysis+=1

    #MC Truth Study -------------------------------------------
    #if not samplename == "Data":
     #   if not isPhotonMatched: continue #FIXMEEEE

    #VBF ORTHOGONALITY ------------------------------------------
    #if nJets > 1 : continue
    nEventsOverVBFOrt += 1


    #Define Control and Signal regions: ------------------------------------------
    if isPhiAnalysis: #for Phi meson
        if CRflag == 0 and not (MesonMass > 1.008 and MesonMass < 1.032) :
            continue

        if CRflag == 1 and (MesonMass > 1.008 and MesonMass < 1.032) :
            continue

        if CRflag == 3 and (MesonMass > 1.008): #left sideband tests
            continue

        if CRflag == 4 and (MesonMass < 1.032): #right sideband tests
            continue

    if isRhoAnalysis: #for Rho meson
        if CRflag == 0 and not (MesonMass > 0.62 and MesonMass < 0.92) :
            continue

        if CRflag == 1 and (MesonMass > 0.62 and MesonMass < 0.92) :
            continue

        if CRflag == 3 and (MesonMass > 0.62): #left sideband tests
            continue

        if CRflag == 4 and (MesonMass < 0.92): #right sideband tests
            continue

    if isK0sAnalysis: #for K0s meson
        if CRflag == 0 and not (MesonMass > 0.842 and MesonMass < 0.942) :
            continue

        if CRflag == 1 and (MesonMass > 0.842 and MesonMass < 0.942) :
            continue

        if CRflag == 3 and (MesonMass > 0.842): #left sideband tests
            continue

        if CRflag == 4 and (MesonMass < 0.942): #right sideband tests
            continue

################### line used to take simmetrical sidebands ################
    if (isPhiAnalysis and MesonMass > 1.05): continue
    if (isRhoAnalysis and MesonMass < 0.58): continue
    if (isK0sAnalysis and MesonMass < 0.80): continue
    nEventsAfterRegionDefiner+=1
############################################################################
    
    if debug:
        print ""
        print"EVENT FEATURES"
        print"--------------------------------------"
        print "isRhoAnalysis = ",isRhoAnalysis
        print "isRhoEvent    = ",isRhoEvent
        print "CRflag        = ",CRflag
        print "isDataBlind   = ",isDataBlind
        print "MesonMass     = ",MesonMass
        print ""

    #--------------------------------------------------------------------------------------

    #phi angle folding
    coupleDeltaPhi = math.fabs(mytree.firstCandPhi - mytree.secondCandPhi)
    if coupleDeltaPhi > 3.14:
        coupleDeltaPhi = 6.28 - coupleDeltaPhi
    deltaR = math.sqrt((mytree.firstCandEta - mytree.secondCandEta)**2 + (coupleDeltaPhi)**2)

    #if firstTrkphi > 0.65 and firstTrkphi < 0.8: continue
    if abs(photonEta) > 2.1: continue
    if abs(MesonEta) > 2.1: continue
    #if (Hmass > 114. and Hmass < 118.): continue #NoTail
    #if (Hmass < 114. or  Hmass > 118.): continue #Tail

    #--------------------------------------------------------------------------
    central_photonEt = photonEt
    #photonEt = phET_scaleUP

    #NORMALIZATION -------------------------------------------------------------------
    #normalization for MC
    if not samplename == "Data":
        
        PUWeight               = mytree.PU_Weight
        weight_sign            = mytree.MC_Weight/abs(mytree.MC_Weight) #just take the sign of the MC gen weight
        photonSF, photonSF_err = myWF.get_photon_scale(photonEt,mytree.photon_eta)
        #photonSF              += photonSF_err
        
        #Photon leg SF
        if photonEt < 80.:
            PhotonTriggerSF        = h_PhotonTriggerSF.GetBinContent(h_PhotonTriggerSF.GetXaxis().FindBin(photonEt))
            PhotonTriggerSF_err    = h_PhotonTriggerSF.GetBinError(h_PhotonTriggerSF.GetXaxis().FindBin(photonEt))
        else: PhotonTriggerSF,PhotonTriggerSF_err = h_PhotonTriggerSF.GetBinContent(9),h_PhotonTriggerSF.GetBinError(9)
        
        # TwoProngs SF
        if MesonPt < 80.:
            TwoProngsTriggerSF     = h_TwoProngsTriggerSF.GetBinContent(h_TwoProngsTriggerSF.GetXaxis().FindBin(MesonPt))
            TwoProngsTriggerSF_err = h_TwoProngsTriggerSF.GetBinError(h_TwoProngsTriggerSF.GetXaxis().FindBin(MesonPt))
        else:
            TwoProngsTriggerSF, TwoProngsTriggerSF_err = h_TwoProngsTriggerSF.GetBinContent(2),h_TwoProngsTriggerSF.GetBinError(2)

        #IsoCh SF
        if MesonPt < 80.:
            if abs(MesonEta) < 1.444:  
                IsoChSF = h_IsoChSF_barrel.GetBinContent(h_IsoChSF_barrel.GetXaxis().FindBin(MesonPt))
            else:
                IsoChSF = h_IsoChSF_endcap.GetBinContent(h_IsoChSF_endcap.GetXaxis().FindBin(MesonPt))                
        else:
            if abs(MesonEta) < 1.444:  
                IsoChSF = h_IsoChSF_barrel.GetBinContent(6)
            else:
                IsoChSF = h_IsoChSF_endcap.GetBinContent(6)

        #IsoNeu SF
        if MesonPt < 80.:
            if abs(MesonEta) < 1.444:  
                IsoNeuSF = h_IsoNeuSF_barrel.GetBinContent(h_IsoNeuSF_barrel.GetXaxis().FindBin(MesonPt))
            else:
                IsoNeuSF = h_IsoNeuSF_endcap.GetBinContent(h_IsoNeuSF_endcap.GetXaxis().FindBin(MesonPt))
        else:
            if abs(MesonEta) < 1.444:  
                IsoNeuSF = h_IsoNeuSF_barrel.GetBinContent(6)
            else:
                IsoNeuSF = h_IsoNeuSF_endcap.GetBinContent(6)

        #Polarization effect
        try: 
            theta_pol  = theta_pol_dict[mytree.event_number]
            weight_pol = 1.5 * math.sin(theta_pol) * math.sin(theta_pol)
        except KeyError:
            "No event number found in the pol dictionary. Weight set to 1"
            weight_pol = 1.

        #weight_pol = 1.
        
        #FIXMEEEEEEE
        if isBDT:
            eventWeight =  luminosity * normalization_weight * weight_sign * PUWeight * weight_pol * photonSF * PhotonTriggerSF * TwoProngsTriggerSF * IsoNeuSF * IsoChSF 
        else:
            eventWeight =  luminosity * normalization_weight * weight_sign * PUWeight * weight_pol * photonSF * PhotonTriggerSF * TwoProngsTriggerSF * IsoChSF 

        if debug:
            print "EVENT WEIGHT"
            print "--------------------------------------"
            print "phi angle trk 1        = ",firstTrkphi
            print "luminosity             = ",luminosity
            print "normalization_weight   = ",normalization_weight
            print "mytree.MC_Weight       = ",mytree.MC_Weight, " (this is not considered)"
            print "weight sign            = ",weight_sign
            print "PUWeight               = ",PUWeight
            print "weight_pol             = ",weight_pol
            print "photonSF               = ",photonSF
            print "photonSF_err           = ",photonSF_err
            print "TwoProngsTriggerSF     = ",TwoProngsTriggerSF
            print "TwoProngsTriggerSF_err = ",TwoProngsTriggerSF_err
            print "Photon Et              = ",central_photonEt
            print "Photon Et smeared down = ",phEt_sigmaDW
            print "Photon Et smeared up   = ",phEt_sigmaUP
            print "Photon Et scaled down  = ",phET_scaleDW
            print "Photon Et scaled up    = ",phET_scaleUP
            print "PhotonTriggerSF        = ",PhotonTriggerSF
            print "MesonPt                = ",MesonPt
            print "Meson iso0             = ",MesonIso0
            print "Meson eta              = ",MesonEta
            print "IsoChSF                = ",IsoChSF
            print "IsoNeuSF               = ",IsoNeuSF
    #        print "PhotonTriggerSF_err    = ",PhotonTriggerSF_err
            print "Final eventWeight **** = ",_eventWeight
            print "isHiggsMatched         = ",isHiggsMatched
            print "isPhotonMatched        = ",isPhotonMatched
            print ""

    #normalization for DATA 
    if samplename == "Data":
        eventWeight = 1.  

    #Electron and muon veto ------------------------------------------
    histo_map["h_nMuons"].Fill(nMuons, eventWeight) # fill this histo to check the number of electrons and muons before the veto
    histo_map["h_nElectrons"].Fill(nElectrons, eventWeight)

    #Lepton veto
    if nElectrons > 0: continue
    if nMuons     > 0: continue
    nEventsOverLeptonVeto += 1

    #DiPhoton veto ------------------------------------------ #FIXMEEEEE
    if (nPhotonsWP90_pT15_barrel > 1 or nPhotonsWP90_pT25_endcap > 1): continue 
    nEventsOverDiPhotonVeto += 1

    #Photon eta cut ------------------------------------------
    if (abs(photonEta) > 1.444 and abs(photonEta) < 1.566): continue
    nEventsPhotonLowEff += 1

    #-------------- n events in the sidebands -----------------------------
    if (Hmass < 100. or Hmass > 170.): continue

    #TIGHT SELECTION from BDT output -------------------------------------------------  
    BDT_out = 1. #to be initialized
    if isBDT: 
        BDT_out = myWF.get_BDT_output(firstTrkisoCh,MesonPt,photonEt,MesonEta,Hmass)#,JetNeutralEmEn,JetChargedHadEn,JetNeutralHadEn)  MesonIso0 
        #histo_map["h_BDT_out"].Fill(BDT_out)

        if debug: print "BDT value before selection = ", BDT_out
        if args.isBDT_option == "BDT0":
            if BDT_out < BDT_OUT: #Cut on BDT output
                if debug: print "BDT cut NOT passed"
                continue
        
        if args.isBDT_option == "BDT1":
            if (BDT_out < -0.4 or BDT_out > BDT_OUT):
                if debug: print "BDT cut NOT passed"
                continue

        if args.isBDT_option == "custom":
            if (BDT_out < -0.4 or BDT_out > 1.):
                if debug: print "BDT cut NOT passed"
                continue

    nEventsInHmassRange+=1

    if samplename == 'Data':
         if (CRflag == 0 and Hmass > 100. and Hmass < 115.) : nEventsLeftSB  += 1
         if (CRflag == 0 and Hmass > 135. and Hmass < 170.) : nEventsRightSB += 1

    # Just for K0s analysis: pT > 20 if the second track is a K
    if isK0sAnalysis and not mytree.isFirstCandK and secondTrkPt < 20.: 
        continue
    else:    
        nEventsKpt20 += 1

    #FILL HISTOS --------------------------------------------------------------------------
    #if DATA -> Blind Analysis on H inv mass plot
    if samplename == "Data":
        if isDataBlind:
            if Hmass < 115. or Hmass > 135.:
                histo_map["h_InvMass_TwoTrk_Photon"].Fill(Hmass, eventWeight)
        else:
            histo_map["h_InvMass_TwoTrk_Photon"].Fill(Hmass, eventWeight)
    else:
        histo_map["h_InvMass_TwoTrk_Photon"].Fill(Hmass, eventWeight)
            
    histo_map["h_meson_InvMass_TwoTrk"].Fill(MesonMass, eventWeight)       
    histo_map["h_couple_Iso_ch"].Fill(MesonIsoCh, eventWeight)
    histo_map["h_bestJetPt"].Fill(jetPt, eventWeight)
    histo_map["h_bestCouplePt"].Fill(MesonPt, eventWeight)
    histo_map["h_firstTrk_pT"].Fill(firstTrkPt, eventWeight)
    histo_map["h_secondTrk_pT"].Fill(secondTrkPt, eventWeight)
    histo_map["h_photon_energy"].Fill(photonEt, eventWeight)
    histo_map["h_H_pT"].Fill(HiggsPt, eventWeight)
    histo_map["h_firstTrk_Eta"].Fill(firstTrketa, eventWeight)    
    histo_map["h_secondTrk_Eta"].Fill(secondTrketa, eventWeight)   
    histo_map["h_firstTrk_Phi"].Fill(firstTrkphi, eventWeight)    
    histo_map["h_secondTrk_Phi"].Fill(secondTrkphi, eventWeight)   
    histo_map["h_bestCoupleDeltaR"].Fill(deltaR/MesonMass, eventWeight)
    histo_map["h_bestJetEta"].Fill(jetEta, eventWeight)
    histo_map["h_couple_Iso"].Fill(MesonIso, eventWeight)
    histo_map["h_firstTrk_Iso"].Fill(firstTrkiso, eventWeight)
    histo_map["h_firstTrk_Iso_ch"].Fill(firstTrkisoCh, eventWeight)
    histo_map["h_secondTrk_Iso"].Fill(secondTrkiso, eventWeight)
    histo_map["h_secondTrk_Iso_ch"].Fill(secondTrkisoCh, eventWeight)
    histo_map["h_photon_eta"].Fill(photonEta, eventWeight)
    histo_map["h_nJets_25"].Fill(nJets, eventWeight)
    histo_map["h_nPhotons38WP80"].Fill(nPhotons38WP80, eventWeight)
    histo_map["h_bestCoupleEta"].Fill(MesonEta, eventWeight)
    histo_map["h_decayChannel"].Fill(isPhiEvent, eventWeight)
    histo_map["h_couple_Iso_neutral"].Fill(MesonIso0, eventWeight)
    histo_map["h_met_pT"].Fill(metPt, eventWeight)
    histo_map["h_dPhiGammaTrk"].Fill(dPhiGammaTrk,eventWeight)
    histo_map["h_pTOverHmass"].Fill(MesonPt/Hmass, eventWeight)
    histo_map["h_eTOverHmass"].Fill(photonEt/Hmass, eventWeight)
    histo_map["h_JetChargedEmEnergy"].Fill(JetChargedEmEn, eventWeight)
    histo_map["h_JetNeutralEmEnergy"].Fill(JetNeutralEmEn, eventWeight)
    histo_map["h_JetChargedHadEnergy"].Fill(JetChargedHadEn, eventWeight)
    histo_map["h_JetNeutralHadEnergy"].Fill(JetNeutralHadEn, eventWeight)
    histo_map["h_JetNeutralHadEnergy"].Fill(JetNeutralHadEn, eventWeight)
    histo_map["h_massResolution"].Fill(massResolution, eventWeight)
    histo_map["h_isoSumPtNeu"].Fill(isoSumPtNeu, eventWeight)
    histo_map["h_nPhotons15WP90barrel"].Fill(nPhotonsWP90_pT15_barrel, eventWeight)
    histo_map["h_nPhotons25WP90endcap"].Fill(nPhotonsWP90_pT25_endcap, eventWeight)
    histo_map["h_nPhotons20WP90eta2p5"].Fill(nPhotonsWP90_pT20_2p5eta3p0, eventWeight)
    histo_map["h_deltaRGammaTrk"].Fill(deltaRGammaTrk, eventWeight)
    histo_map["h_deltaEtaGammaTrk"].Fill(dEtaGammaTrk, eventWeight)
    histo_map["h_IsoSumPt"].Fill(IsoSumPt, eventWeight)
    histo_map["h_IsoSumPtVsJetPt"].Fill(IsoSumPt * eventWeight, jetPt * eventWeight)
    histo_map["h_IsoSumPtVsMesonPt"].Fill(IsoSumPt * eventWeight, MesonPt * eventWeight)
    histo_map["h_photon_HoverE"].Fill(ph_HoverE, eventWeight)
    histo_map["h_photon_hadTowOverEm"].Fill(ph_hadTowOverEm, eventWeight)

    if isK0sAnalysis:
        if mytree.isFirstCandK: 
            histo_map["h_K_pT"].Fill(firstTrkPt,eventWeight)
            histo_map["h_Pi_pT"].Fill(secondTrkPt,eventWeight)
        else:
            histo_map["h_K_pT"].Fill(secondTrkPt,eventWeight)
            histo_map["h_Pi_pT"].Fill(firstTrkPt,eventWeight)
    
    if not samplename == "Data":
        histo_map["h_genPhotonEt"].Fill(genPhotonEt, eventWeight)
        histo_map["h_genMesonPt"].Fill(genMesonPt, eventWeight)
        histo_map["h_MrecoMinusMgen"].Fill(MesonMass - genMesonMass, eventWeight)
        histo_map["h_theta_pol"].Fill(math.cos(theta_pol),weight_pol)

    #Syst evaluation
    if not samplename == "Data":
        PhotonTriggerSystDW    += (eventWeight/PhotonTriggerSF)*(PhotonTriggerSF - PhotonTriggerSF_err)
        PhotonTriggerSystUP    += (eventWeight/PhotonTriggerSF)*(PhotonTriggerSF + PhotonTriggerSF_err)
        TwoProngsTriggerSystDW += (eventWeight/TwoProngsTriggerSF)*(TwoProngsTriggerSF - TwoProngsTriggerSF_err)
        TwoProngsTriggerSystUP += (eventWeight/TwoProngsTriggerSF)*(TwoProngsTriggerSF + TwoProngsTriggerSF_err)
        PhotonIDSystDW         += (eventWeight/photonSF)*(photonSF - photonSF_err)
        PhotonIDSystUP         += (eventWeight/photonSF)*(photonSF + photonSF_err)

    #------------------------------------------------------------------------------------
    #If preselection, reweight events as function of the mass resolution. Just for the BDT.
    if not (samplename == "Data"): 
        BDTweight = eventWeight/massResolution
    else:
        BDTweight = 1.

    #FILL TREE
    mesonGammaMass[0]     = Hmass
    mesonMass[0]          = MesonMass
    _coupleIsoCh[0]       = MesonIsoCh
    _coupleIso[0]         = MesonIso
    _coupleIso0[0]        = MesonIso0
    _bestJetPt[0]         = jetPt        
    _bestCouplePt[0]      = MesonPt    
    _HpT[0]               = HiggsPt    
    _firstTrkPt[0]        = firstTrkPt        
    _secondTrkPt[0]       = secondTrkPt           
    _photonEt[0]          = photonEt
    _firstTrkIso[0]       = firstTrkiso        
    _secondTrkIso[0]      = secondTrkiso        
    _firstTrkIsoCh[0]     = firstTrkisoCh       
    _secondTrkIsoCh[0]    = secondTrkisoCh
    _firstTrkEta[0]       = firstTrketa        
    _secondTrkEta[0]      = secondTrketa        
    _bestCoupleEta[0]     = MesonEta
    _bestCoupleDeltaR[0]  = deltaR
    _photonEta[0]         = photonEta  
    _eventWeight[0]       = eventWeight
    _BDTweight[0]         = BDTweight
    _BDTdisc[0]           = BDT_out
    _metPt[0]             = metPt
    _nJets[0]             = nJets
    _dPhiGammaTrk[0]      = dPhiGammaTrk
    _nPV[0]               = nPV
    _JetChargedEmEnergy[0]  = JetChargedEmEn
    _JetNeutralEmEnergy[0]  = JetNeutralEmEn
    _JetChargedHadEnergy[0] = JetChargedHadEn
    _JetNeutralHadEnergy[0] = JetNeutralHadEn
    if samplename == "Data":
        _eventNumber[0]       = eventNumber
        _runNumber[0]         = runNumber
    
    if not isBDT: #this is done to train the BDT with events under the peak
        if (Hmass > 115. and Hmass < 135.): tree_output_forMVA.Fill()

    tree_output.Fill()


    if debug:
        print "***********************************"
        print "*** EVENT RECORDED: tree filled ***"
        print "***********************************"
        print ""

    #counters
    nEventsOverCuts += 1

    if not samplename == 'Data' :
        weightSum += eventWeight


#HISTO LABELS
histo_map["h_InvMass_TwoTrk_Photon"].GetXaxis().SetTitle("m_{trk^{+}trk^{-}#gamma} [GeV/c^2]")
histo_map["h_InvMass_TwoTrk_Photon"].SetTitle("Tracks+Photon invariant mass (Cut on phi inv. mass)")
histo_map["h_meson_InvMass_TwoTrk"].GetXaxis().SetTitle("m_{trk^{+}trk^{-}} [GeV/c^2]")
histo_map["h_meson_InvMass_TwoTrk"].SetTitle("Tracks invariant mass")
histo_map["h_firstTrk_pT"].GetXaxis().SetTitle("pT_{trk} [GeV/c]")
histo_map["h_firstTrk_pT"].SetTitle("Transverse momentum of the first charged particle (pT_{max} of the couple)")
histo_map["h_secondTrk_pT"].GetXaxis().SetTitle("pT_{trk} [GeV/c]")
histo_map["h_secondTrk_pT"].SetTitle("Transverse momentum of the second charged particle (pT_{min} of the couple)")
histo_map["h_firstTrk_Eta"].GetXaxis().SetTitle("#eta")
histo_map["h_firstTrk_Eta"].SetTitle("Pseudorapidity of the first charged particle (pT_{max} of the couple)")
histo_map["h_secondTrk_Eta"].GetXaxis().SetTitle("#eta")
histo_map["h_secondTrk_Eta"].SetTitle("Pseudorapidity of the second charged particle (pT_{max} of the couple)")
histo_map["h_firstTrk_Phi"].GetXaxis().SetTitle("#phi [rad]")
histo_map["h_firstTrk_Phi"].SetTitle("Azimuthal angle of the first charged particle (pT_{max} of the couple)")
histo_map["h_secondTrk_Phi"].GetXaxis().SetTitle("#phi [rad]")
histo_map["h_secondTrk_Phi"].SetTitle("Azimuthal angle of the second charged particle (pT_{max} of the couple)")
histo_map["h_bestCouplePt"].GetXaxis().SetTitle("pT_{trk^{+}trk^{-}} [GeV]")
histo_map["h_bestCouplePt"].SetTitle("Transverse momentum of the couple")
histo_map["h_H_pT"].GetXaxis().SetTitle("p_{T}^{H} [GeV]")
histo_map["h_H_pT"].SetTitle("Transverse momentum of the Higgs candidate")
histo_map["h_bestCoupleEta"].GetXaxis().SetTitle("#eta")
histo_map["h_bestCoupleEta"].SetTitle("Pseudorapidity of the couple")
histo_map["h_bestJetPt"].GetXaxis().SetTitle("pT_{jet} [GeV]")
histo_map["h_bestJetPt"].SetTitle("Transverse momentum of the jet")
histo_map["h_bestJetEta"].GetXaxis().SetTitle("#eta_{jet}")
histo_map["h_bestJetEta"].SetTitle("Pseudorapidity of the jet")
histo_map["h_firstTrk_Iso"].GetXaxis().SetTitle("sum pT_{trk_{1}}/pT_{trk_{1}}")
histo_map["h_firstTrk_Iso"].SetTitle("Isolation of the trk_{1} candidate")
histo_map["h_firstTrk_Iso_ch"].GetXaxis().SetTitle("sum pT_{trk_{1}}/pT_{trk_{1}}")
histo_map["h_firstTrk_Iso_ch"].SetTitle("Isolation of the trk_{1} candidate")
histo_map["h_secondTrk_Iso"].GetXaxis().SetTitle("sum pT_{trk_{2}}/pT_{trk_{2}}")
histo_map["h_secondTrk_Iso"].SetTitle("Isolation of the trk_{2} candidate")
histo_map["h_secondTrk_Iso_ch"].GetXaxis().SetTitle("sum pT_{trk_{2}}/pT_{trk_{2}}")
histo_map["h_secondTrk_Iso_ch"].SetTitle("Isolation of the trk_{1} candidate")
histo_map["h_couple_Iso"].GetXaxis().SetTitle("sum pT_{2trk}/pT_{2trk}")
histo_map["h_couple_Iso"].SetTitle("Isolation of the couple candidate")
histo_map["h_couple_Iso_ch"].GetXaxis().SetTitle("sum pT_{2trk}/pT_{2trk}")
histo_map["h_couple_Iso_ch"].SetTitle("Isolation of the couple candidate")
histo_map["h_bestCoupleDeltaR"].GetXaxis().SetTitle("#DeltaR_{trk^{+}trk^{-}}")
histo_map["h_bestCoupleDeltaR"].SetTitle("Delta R of the couple")
histo_map["h_photon_energy"].GetXaxis().SetTitle("E_{T}^{#gamma}[GeV]")
histo_map["h_photon_energy"].SetTitle("Energy of the photon")
histo_map["h_photon_eta"].GetXaxis().SetTitle("#eta_{#gamma}")
histo_map["h_photon_eta"].SetTitle("Eta of the photon")
histo_map["h_nJets_25"].GetXaxis().SetTitle("nJets over 25 GeV")
histo_map["h_nJets_25"].SetTitle("# of jets with pT > 25 GeV")
histo_map["h_nPhotons38WP80"].GetXaxis().SetTitle("n.#gamma_{38wp80}")
histo_map["h_nPhotons38WP80"].SetTitle("n.#gamma over selections")
histo_map["h_nPhotons15WP90barrel"].GetXaxis().SetTitle("n.#gamma_{15wp90_barrel}")
histo_map["h_nPhotons15WP90barrel"].SetTitle("n.#gamma over selections")
histo_map["h_nPhotons25WP90endcap"].GetXaxis().SetTitle("n.#gamma_{25wp90_endcap}")
histo_map["h_nPhotons25WP90endcap"].SetTitle("n.#gamma over selections")
histo_map["h_nPhotons20WP90eta2p5"].GetXaxis().SetTitle("n.#gamma_{20wp90_eta2p5}")
histo_map["h_nPhotons20WP90eta2p5"].SetTitle("n.#gamma over selections")
histo_map["h_efficiency"].GetXaxis().SetTitle("")
histo_map["h_efficiency"].GetYaxis().SetTitle("#epsilon (%)")
histo_map["h_decayChannel"].SetTitle("Decay channel")
histo_map["h_decayChannel"].GetXaxis().SetBinLabel(1,"Rho events")
histo_map["h_decayChannel"].GetXaxis().SetBinLabel(2,"Phi events")
histo_map["h_couple_Iso_neutral"].GetXaxis().SetTitle("sum pT_{2trk}/pT_{2trk}")
histo_map["h_couple_Iso_neutral"].SetTitle("Isolation of the couple candidate from neutral particles")
histo_map["h_met_pT"].GetXaxis().SetTitle("pT_{met} [GeV/c]")
histo_map["h_met_pT"].SetTitle("Transverse momentum of the missing energy")
histo_map["h_dPhiGammaTrk"].GetXaxis().SetTitle("#Delta#Phi_{#gamma,Trk_1} [rad]")
histo_map["h_dPhiGammaTrk"].SetTitle("#Delta#Phi_{#gamma,Trk_1} [rad]")
histo_map["h_pTOverHmass"].GetXaxis().SetTitle("p_T^{trk^{+}trk^{-}}/m_{ditrk#gamma}")
histo_map["h_pTOverHmass"].SetTitle("pT of the meson divided by Hmass")
histo_map["h_eTOverHmass"].GetXaxis().SetTitle("eT_{#gamma}/m_{ditrk#gamma}")
histo_map["h_eTOverHmass"].SetTitle("eT of the photon divided by Hmass")
histo_map["h_JetChargedEmEnergy"].GetXaxis().SetTitle("E_{jet}^{ch,em}")
histo_map["h_JetNeutralEmEnergy"].GetXaxis().SetTitle("E_{jet}^{0,em}")
histo_map["h_JetChargedHadEnergy"].GetXaxis().SetTitle("E_{jet}^{ch,had}")
histo_map["h_JetNeutralHadEnergy"].GetXaxis().SetTitle("E_{jet}^{0,had}")
histo_map["h_massResolution"].GetXaxis().SetTitle("#sigmaM/M")
histo_map["h_isoSumPtNeu"].GetXaxis().SetTitle("#Sigma pT")
histo_map["h_deltaRGammaTrk"].GetXaxis().SetTitle("#DeltaR_{#gamma,trk_{1}}")
histo_map["h_deltaEtaGammaTrk"].GetXaxis().SetTitle("#Delta#eta_{#gamma,trk_{1}}")
histo_map["h_IsoSumPt"].GetXaxis().SetTitle("#Sigmap_{T} [GeV]")
histo_map["h_IsoSumPtVsJetPt"].GetXaxis().SetTitle("#Sigmap_{T} [GeV]")
histo_map["h_IsoSumPtVsJetPt"].GetYaxis().SetTitle("p_{T}^{jet} [GeV]")
histo_map["h_IsoSumPtVsMesonPt"].GetXaxis().SetTitle("#Sigmap_{T} [GeV]")
histo_map["h_IsoSumPtVsMesonPt"].GetYaxis().SetTitle("p_{T}^{meson} [GeV]")
histo_map["h_photon_HoverE"].GetXaxis().SetTitle("H/E")
histo_map["h_photon_hadTowOverEm"].GetXaxis().SetTitle("H_{tow}/E")
    
#Draw just the heatmaps
canvas = ROOT.TCanvas("c1", "Canvas Title", 800, 600)  # Un canvas di dimensioni maggiori
pad = canvas.cd()
pad.SetRightMargin(0.15)  # Aumenta il margine destro

histo_map["h_IsoSumPtVsMesonPt"].SetStats(0)
histo_map["h_IsoSumPtVsMesonPt"].Draw("COLZ")
canvas.Update()

canvas.SaveAs("~/cernbox/www/h_IsoSumPtVsMesonPt.png")
canvas.SaveAs("~/cernbox/www/h_IsoSumPtVsMesonPt.pdf")

#Draw just the heatmaps
canvas2 = ROOT.TCanvas("c2", "Canvas Title", 800, 600)  # Un canvas di dimensioni maggiori
pad2 = canvas2.cd()
pad2.SetRightMargin(0.15)  # Aumenta il margine destro

histo_map["h_IsoSumPtVsJetPt"].SetStats(0)
histo_map["h_IsoSumPtVsJetPt"].Draw("COLZ")
canvas2.Update()

canvas2.SaveAs("~/cernbox/www/h_IsoSumPtVsJetPt.png")
canvas2.SaveAs("~/cernbox/www/h_IsoSumPtVsJetPt.pdf")

if isK0sAnalysis:
    histo_map["h_K_pT"].GetXaxis().SetTitle("pT_{K} [GeV/c]")
    histo_map["h_Pi_pT"].GetXaxis().SetTitle("pT_{#Pi} [GeV/c]")

if not samplename == "Data":
    histo_map["h_genPhotonEt"].GetXaxis().SetTitle("E_{T}^{gen#gamma}[GeV]")
    histo_map["h_genPhotonEt"].SetTitle("eT of the genPhoton")
    histo_map["h_genMesonPt"].GetXaxis().SetTitle("pT_{genMeson} [GeV]")
    histo_map["h_genMesonPt"].SetTitle("Transverse momentum of the genMeson")
    histo_map["h_MrecoMinusMgen"].GetXaxis().SetTitle("m_{recoMeson}-m_{genMeson} [GeV]")
    histo_map["h_theta_pol"].GetXaxis().SetTitle("cos(K,#phi)")

#########################################################################
#Tree writing
tree_output.Write()
if not isBDT: tree_output_forMVA.Write()
#tree_output.Scan()

#Variables for cut overflow
nEventsProcessed   = h_Events.GetBinContent(1)
nEventsTriggered   = h_Events.GetBinContent(2)
nEventsPhoton      = h_Events.GetBinContent(3)
nEventsBestPair    = h_Events.GetBinContent(6)
nEventsMesonMassSR = nEventsRightSB + nEventsLeftSB

#EFFICIENCY STEP PLOT MANAGEMENT
if not samplename == "Data":

    bin1content  = h_Events.GetBinContent(1)
    bin2content  = h_Events.GetBinContent(2)
    bin3content  = h_Events.GetBinContent(3)
    bin4content  = h_Events.GetBinContent(4)
    bin5content  = h_Events.GetBinContent(5)
    bin6content  = h_Events.GetBinContent(6)
    bin7content  = h_Events.GetBinContent(7)
    bin8content  = nEventsOverCuts
    nSignal      = bin1content
    scale_factor = 100/nSignal

    histo_map["h_efficiency"].Fill(0.5,bin1content*scale_factor)
    histo_map["h_efficiency"].Fill(1.5,bin2content*scale_factor)
    histo_map["h_efficiency"].Fill(2.5,bin3content*scale_factor)
    histo_map["h_efficiency"].Fill(3.5,bin4content*scale_factor)
    histo_map["h_efficiency"].Fill(4.5,bin5content*scale_factor)
    histo_map["h_efficiency"].Fill(5.5,bin6content*scale_factor)
    histo_map["h_efficiency"].Fill(6.5,bin7content*scale_factor)
    histo_map["h_efficiency"].Fill(7.5,bin8content*scale_factor)
    histo_map["h_efficiency"].GetXaxis().SetBinLabel(1,"Events processed")
    histo_map["h_efficiency"].GetXaxis().SetBinLabel(2,"Events triggered")
    histo_map["h_efficiency"].GetXaxis().SetBinLabel(3,"Photon requested")
    histo_map["h_efficiency"].GetXaxis().SetBinLabel(4,"Best couple found")
    histo_map["h_efficiency"].GetXaxis().SetBinLabel(5,"trk-cand pT selection")
    histo_map["h_efficiency"].GetXaxis().SetBinLabel(6,"trktrk iso selection")
    histo_map["h_efficiency"].GetXaxis().SetBinLabel(7,"VBF veto")
    histo_map["h_efficiency"].GetXaxis().SetBinLabel(8,"Tight selections")

    c11 = ROOT.TCanvas()
    c11.cd()
    histo_map["h_efficiency"].SetFillColor(1) 
    histo_map["h_efficiency"].SetFillStyle(3003)
    ROOT.gStyle.SetPaintTextFormat("4.2f %")
    ROOT.gStyle.SetOptStat(0)
    histo_map["h_efficiency"].SetMarkerSize(1.4)
    histo_map["h_efficiency"].GetXaxis().SetRangeUser(0.,7.1)
    histo_map["h_efficiency"].GetYaxis().SetRangeUser(0.,30.)
    #histo_map["h_efficiency"].SetMaximum(max(histo_map["h_efficiency"].GetHistogram().GetMaximum(),30.))
    histo_map["h_efficiency"].Draw("HIST TEXT0")
    c11.SaveAs("plots/h_efficiency.pdf")
    c11.SaveAs("plots/h_efficiency.png")    

else: #Only if data
    histo_map["h_cutOverflow"].Fill(0.5,nEventsProcessed)
    histo_map["h_cutOverflow"].Fill(1.5,nEventsTriggered)
    histo_map["h_cutOverflow"].Fill(2.5,nEventsPhoton)
    histo_map["h_cutOverflow"].Fill(3.5,nEventsBestPair)
    histo_map["h_cutOverflow"].Fill(4.5,nEventsMesonMassSR)
    histo_map["h_cutOverflow"].GetXaxis().SetBinLabel(1,"Events processed")
    histo_map["h_cutOverflow"].GetXaxis().SetBinLabel(2,"Events triggered")
    histo_map["h_cutOverflow"].GetXaxis().SetBinLabel(3,"Photon requested")
    histo_map["h_cutOverflow"].GetXaxis().SetBinLabel(4,"Best pair found")
    histo_map["h_cutOverflow"].GetXaxis().SetBinLabel(5,"Mmass SR and MGammaMass SB")

    c11 = ROOT.TCanvas()
    c11.cd()
    histo_map["h_cutOverflow"].SetFillColor(1) 
    histo_map["h_cutOverflow"].SetFillStyle(3003)
    ROOT.gStyle.SetPaintTextFormat("4.2f")
    ROOT.gStyle.SetOptStat(0)
    histo_map["h_cutOverflow"].SetMarkerSize(1.4)
    histo_map["h_cutOverflow"].GetXaxis().SetRangeUser(1.,4.1)
#    histo_map["h_cutOverflow"].GetYaxis().SetRangeUser(0.,30.)
    #histo_map["h_cutOverflow"].SetMaximum(max(histo_map["h_cutOverflow"].GetHistogram().GetMaximum(),30.))
    histo_map["h_cutOverflow"].Draw("HIST TEXT0")
    c11.SaveAs("plots/h_cutOverflow.pdf")
    c11.SaveAs("plots/h_cutOverflow.png")

#FINAL PRINTS ###########################################################
print ""
print ""
print "CUT OVERFLOW"
print "---------------------------------------"
print "CRflag                    = ",CRflag," (SR if 0, CR if 1)"
print "nEventsProcessed          = ",nEventsProcessed," (n. events in dataset)"
print "nEventsTriggered          = ",nEventsTriggered," (n. events over HLT)"
print "nEventsPhoton             = ",nEventsPhoton," (n. events with a best photon found)"
print "nEventsMesonAnalysis      = ",nEventsMesonAnalysis," (split in PhiGamma or RhoGamma analysis)"
print "nEventsOverVBFOrt         = ",nEventsOverVBFOrt," (n. events over the VBF orthogonality: events with more than one jet are discarded)"
print "nEventsAfterRegionDefiner = ",nEventsAfterRegionDefiner," (split in SR or CR of the ditrack inv mass)"
print "nEventsOverLeptonVeto     = ",nEventsOverLeptonVeto," (n. events without any electron or muon)"
print "nEventsOverDiPhotonVeto   = ",nEventsOverDiPhotonVeto," (n. events with just one photon)"
print "nEventsPhotonLowEf        = ",nEventsPhotonLowEff," (n. events with no photons with low eff)"
if isK0sAnalysis: print "nEventsKpt20              = ",nEventsKpt20," (n. events with with kaon pT > 20)"
print "nEventsInHmassRange       = ",nEventsInHmassRange," (n. events in 100 < Hmass < 170 GeV)"
print "nEventsMesonMassSR        = ",nEventsMesonMassSR," (Events in SR of MesonMass and in SBs of Hmass)"
print ""
print "----------- SUMMARY -----------------------"
if isBDT:
    print "BDT output used = ",BDT_OUT
if not samplename == "Data":
    print "Signal MC sample (~ 2M events)"
if isBDT:
    print "n. events after preselection = ",jentry
print "nEventsInHmassRange         = ",nEventsInHmassRange," (n. events in 100 < Hmass < 170 GeV)"
print "n. events after cuts        = " , nEventsOverCuts

if samplename == 'Data' and CRflag == 0:
    print "n. events in the left sideband counted = ",nEventsLeftSB
    print "n. events in the right sideband counted = ",nEventsRightSB 
    print "Total events in the sidebands = ", nEventsRightSB + nEventsLeftSB

if not samplename == "Data":
    print "Signal weight sum   = ",float(weightSum)
    print "Signal integral     = ",histo_map["h_InvMass_TwoTrk_Photon"].Integral()
    print "Total signal events = ",bin1content
    print "Signal efficiency   = ",nEventsOverCuts/bin1content
    print "Syst ------------------------"
    print "PhotonTrig SF DW = ", (1 - PhotonTriggerSystDW/float(weightSum))*100
    print "PhotonTrig SF UP = ", (1 - float(weightSum)/PhotonTriggerSystUP)*100
    print "TwoProngs  SF DW = ", (1 - TwoProngsTriggerSystDW/float(weightSum))*100
    print "TwoProngs  SF UP = ", (1 - float(weightSum)/TwoProngsTriggerSystUP)*100
    print "PhotonID   SF DW = ", (1 - PhotonIDSystDW/float(weightSum))*100
    print "PhotonID   SF UP = ", (1 - float(weightSum)/PhotonIDSystUP)*100

print "-------------------------------------------"
print ""
print ""

#HISTOS WRITING
fOut.cd()
for hist_name in list_histos:
    histo_map[hist_name].Write()
fOut.Close()
