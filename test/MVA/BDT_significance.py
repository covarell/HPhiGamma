import ROOT
import math
import numpy as np
import argparse

#Supress the opening of many Canvas's
ROOT.gROOT.SetBatch(True)

#Choose an injected BR (since you moved to BR = 1 here you can set it at 10^-5 to make comparison with previous productions)
BR_inj = 0.00001

#Input files
fInputSignal = ROOT.TFile("../histos/latest_production/histos_SR_preselection_SignalggH.root")
sig_tree     = fInputSignal.Get("tree_output_forMVA")

fInputData  = ROOT.TFile("../histos/latest_production/histos_SR_preselection_Data.root")
data_tree   = fInputData.Get("tree_output_forMVA")
h_mesonMass = fInputData.Get("h_meson_InvMass_TwoTrk")

Nbkg_passed = 0
nEntriesData = int(h_mesonMass.GetEntries())

for dataEntry in xrange(nEntriesData):
    ientry = data_tree.LoadTree( dataEntry )  
    if ientry < 0:
        break
    nb = data_tree.GetEntry(dataEntry )
    if nb <= 0:
        print "nb < 0"
        continue
    
    Hmass = data_tree.mesonGammaMass
    if (Hmass < 120. or Hmass > 130.): continue
    Nbkg_passed += 1

Nsig_passed = 0 #Initialize the number of signal events from the sum of the weights (before applying BDT cuts), take this number running the generate_histos for signal

#EVENTS LOOP 
nEntriesSig = sig_tree.GetEntriesFast()
for sigEntry in xrange(nEntriesSig):
    ientry = sig_tree.LoadTree( sigEntry )  
    if ientry < 0:
        break
    nb = sig_tree.GetEntry(sigEntry )
    if nb <= 0:
        print "nb < 0"
        continue
    Hmass = sig_tree.mesonGammaMass
    if (Hmass < 120. or Hmass > 130.): continue
    #print Hmass
    Nsig_passed += sig_tree._eventWeight * BR_inj

print "nEntriesSig  = ",nEntriesSig
print "Nsig_passed  = ",Nsig_passed
print "nEntriesData = ",nEntriesData
print "Nbkg_passed  = ",Nbkg_passed


BDT_file = ROOT.TFile("outputs/Nominal_training.root")

h_BDT_effB_effS = BDT_file.Get("default/Method_BDT/BDT/MVA_BDT_effBvsS")

canvas1 = ROOT.TCanvas()
sig_eff = []
bkg_eff = []
signif  = []
_effS   = 0

for jbin in range(1,h_BDT_effB_effS.GetNbinsX()+1):
    if h_BDT_effB_effS.GetBinCenter(jbin) > 0.2: # (0.57 for Phi channel) insert the number before whom the function fluctuates too much to estimate the maximum
        sig_eff.append(h_BDT_effB_effS.GetBinCenter(jbin))
        if h_BDT_effB_effS.GetBinContent(jbin) <= 0.:
            bkg_eff.append(0.)
            signif.append(0)
        else:
            bkg_eff.append(h_BDT_effB_effS.GetBinContent(jbin))
            signif.append(Nsig_passed*h_BDT_effB_effS.GetBinCenter(jbin)/math.sqrt(Nbkg_passed*h_BDT_effB_effS.GetBinContent(jbin)))


sig_eff_array = np.array(sig_eff)
bkg_eff_array = np.array(bkg_eff)
signif_array = np.array(signif)
#print "signif_len: ", len(signif_array)
sign = ROOT.TGraph(70,sig_eff_array,signif_array)
sign.SetTitle("")
sign.GetXaxis().SetTitle("#varepsilon_{S}^{BDT}")
sign.GetYaxis().SetTitle("Significance")
sign.SetMinimum(0.)
#sign.SetMinimum(0.8*ROOT.TMath.MinElement(sign.GetN(),sign.GetY()))
#sign.SetMaximum(1.2*ROOT.TMath.MaxElement(sign.GetN(),sign.GetY()))
sign.SetMarkerStyle(8)
sign.SetMarkerColor(4)
sign.GetXaxis().SetRangeUser(0.1,1.)
sign.GetYaxis().SetRangeUser(0.8*ROOT.TMath.MinElement(sign.GetN(),sign.GetY()),1.2*ROOT.TMath.MaxElement(sign.GetN(),sign.GetY()))

sign.Draw("AP")

canvas2 = ROOT.TCanvas()
sign_vs_bkg = ROOT.TGraph(70,bkg_eff_array,signif_array)
sign_vs_bkg.SetTitle("")
sign_vs_bkg.GetXaxis().SetTitle("#varepsilon_{B}^{BDT}")
sign_vs_bkg.GetYaxis().SetTitle("Significance")
sign_vs_bkg.GetXaxis().SetRangeUser(0.,0.8)
sign_vs_bkg.SetMinimum(0.8*ROOT.TMath.MinElement(sign_vs_bkg.GetN(),sign_vs_bkg.GetY()))
sign_vs_bkg.SetMaximum(1.2*ROOT.TMath.MaxElement(sign_vs_bkg.GetN(),sign_vs_bkg.GetY()))
sign_vs_bkg.SetMarkerStyle(8)
sign_vs_bkg.SetMarkerColor(4)
sign_vs_bkg.Draw("AP")


canvas1.SaveAs("/afs/cern.ch/user/g/gumoret/cernbox/www/latest_production/MVA_latest_production/signif_vs_effS.pdf")
canvas1.SaveAs("/afs/cern.ch/user/g/gumoret/cernbox/www/latest_production/MVA_latest_production/signif_vs_effS.png")
canvas2.SaveAs("/afs/cern.ch/user/g/gumoret/cernbox/www/latest_production/MVA_latest_production/signif_vs_effB.pdf")
canvas2.SaveAs("/afs/cern.ch/user/g/gumoret/cernbox/www/latest_production/MVA_latest_production/signif_vs_effB.png")

#---- Now find the BDT output corresponding to the highest significance

h_BDT_effS = BDT_file.Get("default/Method_BDT/BDT/MVA_BDT_effS")
signif_maximizing_eff = sig_eff_array[np.argmax(signif_array)]
#print "signif_maximizing_eff = ",signif_maximizing_eff
BDT_output = 0. 

for entry in xrange(h_BDT_effS.GetNbinsX()):

    effS = h_BDT_effS.GetBinContent(entry)
    effS = float(format(effS, '.3f'))
    signif_maximizing_eff = float(format(signif_maximizing_eff, '.3f'))
    #print "effS: ", effS, "signif_max_eff: ", signif_maximizing_eff
    if effS == signif_maximizing_eff:
        BDT_output =  h_BDT_effS.GetBinCenter(entry)
        _effS = effS

print ""
print "RESULT"
print "-------------------------------------------------------------"
print "Nsig_passed       = " ,Nsig_passed
print "Nbkg_passed       = " ,Nbkg_passed
print "Signal efficiency = ", _effS
print "Significance:   Z = ",signif_array[np.argmax(signif_array)]
print "BDT output        = ", BDT_output
print "-------------------------------------------------------------"

# Create a ROOT file to store the tree
output_file = ROOT.TFile("BDToutput.root", "RECREATE")

# Create the tree and add a branch for the BDT output variable
tree = ROOT.TTree("BDTtree", "Tree with BDT output")

output_file.cd()

_BDT_output = np.zeros(1, dtype=float)
tree.Branch("_BDT_output",_BDT_output, "_BDT_output/D")
_BDT_output[0] = BDT_output
tree.Fill()
# Save the tree to the output file and close the file
output_file.Write()
output_file.Close()

#raw_input()
