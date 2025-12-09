import ROOT
import tdrstyle, CMS_lumi
import argparse

#bool initialization
isRhoGammaAnalysis = False
isPhiGammaAnalysis = False
isK0sGammaAnalysis = False
includeResiduals   = False  # Flag to include the residuals subplot

#INPUT and OUTPUT #############################################################################################
#Input
p = argparse.ArgumentParser(description='Select rootfile to plot')
p.add_argument('Decay_channel_option', help='Type <<Phi>> for Phi, <<Rho>> for Rho') #flag for bkg estimation
args = p.parse_args()

if args.Decay_channel_option == "Phi":
    isPhiGammaAnalysis = True
    CHANNEL = "Phi"
    print "H -> PhiGamma analysis"
if args.Decay_channel_option == "Rho":
    isRhoGammaAnalysis = True
    CHANNEL = "Rho"
    print "H -> RhoGamma analysis"
if args.Decay_channel_option == "K0s":
    isK0sGammaAnalysis = True
    CHANNEL = "K0s"
    print "H -> K0sGamma analysis"

#Signal input rootfiles ---------------------------------------------------------------
fileInput_ggH = ROOT.TFile("histos/latest_production/histos_SR_BDTcat1_SignalggH.root")
fileInput_VBF = ROOT.TFile("histos/latest_production/histos_SR_BDTcat1_SignalVBF.root")
tree_ggH = fileInput_ggH.Get("tree_output")
tree_VBF = fileInput_VBF.Get("tree_output")

#Import the Doube Crystal Ball PDF -----------------------------------------------------
ROOT.gROOT.ProcessLineSync(".L MassAnalysis/dCB/RooDoubleCBFast.cc+")

#Supress the opening of many Canvas's ---------------------------------------------------
ROOT.gROOT.SetBatch(True)   

#CMS-style plotting ---------------------------------------------------------------
tdrstyle.setTDRStyle()
iPeriod = 4
iPos = 11
CMS_lumi.lumiTextSize = 0.7
CMS_lumi.lumiTextOffset = 0.25
CMS_lumi.cmsTextSize = 0.6  # Adjust the CMS text size here
CMS_lumi.cmsTextOffset = 0.1  # Adjust the CMS text offset here
CMS_lumi.lumi_13TeV = "39.54 fb^{-1}"

#prepare a rebinned TH1 for Higgs mass ---------------------------------------------------------------
xLowRange  = 110.
xHighRange = 160.

h_mH_ggH = ROOT.TH1F("h_mH_ggH","h_mH_ggH", int(xHighRange - xLowRange)*10, xLowRange, xHighRange)
h_mH_VBF = ROOT.TH1F("h_mH_VBF","h_mH_VBF", int(xHighRange - xLowRange)*10, xLowRange, xHighRange)

nentries_ggH = tree_ggH.GetEntriesFast()
nentries_VBF = tree_VBF.GetEntriesFast()

for jentry in xrange(nentries_ggH):
    ientry = tree_ggH.LoadTree( jentry )
    if ientry < 0:
        break
    nb = tree_ggH.GetEntry(jentry)
    if nb <= 0:
        print "nb < 0"
        continue

    h_mH_ggH.Fill(tree_ggH.mesonGammaMass, tree_ggH._eventWeight)

for jentry in xrange(nentries_VBF):
    ientry = tree_VBF.LoadTree( jentry )
    if ientry < 0:
        break
    nb = tree_VBF.GetEntry(jentry)
    if nb <= 0:
        print "nb < 0"
        continue

    h_mH_VBF.Fill(tree_VBF.mesonGammaMass, tree_VBF._eventWeight)

#Define the observable ---------------------------------------------------------------
mass = ROOT.RooRealVar("mesonGammaMass", "mesonGammaMass", 125., xLowRange, xHighRange, "GeV/c^2")

#Double Crystal Ball definition ---------------------------------------------------------------
dCB_pole_ggH  = ROOT.RooRealVar("dCB_pole_"+CHANNEL+"_GFcat_bdt1_ggH", "Double CB pole", 125.,120.,130.)
dCB_width_ggH = ROOT.RooRealVar("dCB_width_"+CHANNEL+"_GFcat_bdt1_ggH", "Double CB width",1.,0.,2.)
dCB_aL_ggH    = ROOT.RooRealVar("dCB_aL_"+CHANNEL+"_GFcat_bdt1_ggH", "Double CB alpha left", 1.1, 0.8, 1.7)
dCB_aR_ggH    = ROOT.RooRealVar("dCB_aR_"+CHANNEL+"_GFcat_bdt1_ggH", "Double CB alpha right", 1.5, 0.8, 1.7)
dCB_nL_ggH    = ROOT.RooRealVar("dCB_nL_"+CHANNEL+"_GFcat_bdt1_ggH", "Double CB n left", 4., 1., 5.)
dCB_nR_ggH    = ROOT.RooRealVar("dCB_nR_"+CHANNEL+"_GFcat_bdt1_ggH", "Double CB n right", 3.7, 1., 5.)

dCB_pole_VBF  = ROOT.RooRealVar("dCB_pole_"+CHANNEL+"_GFcat_bdt1_VBF", "Double CB pole", 125.,120.,130.)
dCB_width_VBF = ROOT.RooRealVar("dCB_width_"+CHANNEL+"_GFcat_bdt1_VBF", "Double CB width",1.,0.,2.)
dCB_aL_VBF    = ROOT.RooRealVar("dCB_aL_"+CHANNEL+"_GFcat_bdt1_VBF", "Double CB alpha left", 1.2, 0.5, 2.)
dCB_aR_VBF    = ROOT.RooRealVar("dCB_aR_"+CHANNEL+"_GFcat_bdt1_VBF", "Double CB alpha right", 1.6, 0.5, 2.)
dCB_nL_VBF    = ROOT.RooRealVar("dCB_nL_"+CHANNEL+"_GFcat_bdt1_VBF", "Double CB n left", 3., 1., 10.)
dCB_nR_VBF    = ROOT.RooRealVar("dCB_nR_"+CHANNEL+"_GFcat_bdt1_VBF", "Double CB n right", 3.1, 1., 10.)

signalPDF_ggH = ROOT.RooDoubleCBFast("crystal_ball_"+CHANNEL+"_GFcat_bdt1_ggH", "Double Crystal Ball", mass, dCB_pole_ggH, dCB_width_ggH, dCB_aL_ggH, dCB_nL_ggH, dCB_aR_ggH, dCB_nR_ggH)
signalPDF_VBF = ROOT.RooDoubleCBFast("crystal_ball_"+CHANNEL+"_GFcat_bdt1_VBF", "Double Crystal Ball", mass, dCB_pole_VBF, dCB_width_VBF, dCB_aL_VBF, dCB_nL_VBF, dCB_aR_VBF, dCB_nR_VBF)

#Input tree ------------------------------------------------------------------------------------------------------------------------------
fileInput_ggH.cd()
tree_ggH = fileInput_ggH.Get("tree_output")

#Retrieve dataset from the tree, insert the variable also ---------------------------------------------------------------
#dataset_ggH = ROOT.RooDataSet("dataset_ggH","dataset_ggH", ROOT.RooArgSet(mass), ROOT.RooFit.Import(tree_ggH))
dataset_ggH = ROOT.RooDataHist("dataset_ggH", "dataset_ggH", ROOT.RooArgList(mass), h_mH_ggH)

#Do the fit ------------------------------------------------------------------------------------------------------------------------------
fitResult_ggH = signalPDF_ggH.fitTo(dataset_ggH,ROOT.RooFit.Save())

#Plot ------------------------------------------------------------------------------------------------------------------------------
# Custom canvas dimensions
canvas_width      = 800
canvas_height     = 800
canvas_margin_top = 100  # Empty space added at the top of the main canvas

xframe_ggH = mass.frame(int(xHighRange - xLowRange)*10)
dataset_ggH.plotOn(xframe_ggH)
signalPDF_ggH.plotOn(xframe_ggH)
xframe_ggH.SetTitle("")
ROOT.gStyle.SetOptFit(1111)
xframe_ggH.SetMaximum(1.2 * xframe_ggH.GetMaximum())
signalPDF_ggH.paramOn(xframe_ggH, ROOT.RooFit.Layout(0.53, 0.94, 0.91), ROOT.RooFit.Format("NEU", ROOT.RooFit.AutoPrecision(1)))  # ,ROOT.RooFit.Layout(0.65,0.90,0.90)
xframe_ggH.getAttText().SetLineWidth(0)
xframe_ggH.getAttText().SetTextSize(0.019)
xframe_ggH.GetXaxis().SetTitle("m_{ditrk,#gamma} [GeV]")
xframe_ggH.GetXaxis().SetRangeUser(xLowRange, xHighRange)
#xframe_ggH.GetYaxis().SetMaxDigits(2)

# ChiSquare test ---------------------------------------------------------------------------------------------------------------------------
nParam_ggH = fitResult_ggH.floatParsFinal().getSize()
chi2_ggH = xframe_ggH.chiSquare()  # Returns chi2/ndof. Remember to remove the option XErrorSize(0) from data.PlotOn
cut_chi2_ggH = "{:.2f}".format(chi2_ggH)  # Crop the chi2 to 2 decimal digits

print "nParam_ggH =", nParam_ggH
print "cut_chi2_ggH =", cut_chi2_ggH

# Create the first canvas (c1) for the main plot
c1 = ROOT.TCanvas("c1", "c1", canvas_width, canvas_height + canvas_margin_top)
c1.cd()
c1.SetTitle("")
c1.SetBottomMargin(0.15)  # Increase the empty space at the bottom of the main canvas

if includeResiduals:
    c1.Divide(1, 2, 0, 0.25)  # Divide canvas into two pads: 1x2 grid, with the first pad being 4 times larger
    c1.cd(1)  # Activate the first pad for the main plot
else:
    c1.Divide(1, 1)

xframe_ggH.Draw()

if includeResiduals:
    c1.cd(2)  # Activate the second pad for the residuals plot
    c1.GetPad(2).SetBottomMargin(0.15)  # Increase the empty space at the bottom of the residuals plot
    residuals = xframe_ggH.residHist()
    residuals.SetFillColor(ROOT.kBlue)
    residuals.SetMarkerColor(ROOT.kBlack)
    residuals.GetYaxis().SetTitle("Resid")
    residuals.GetYaxis().SetTitleOffset(1.)
    residuals.GetYaxis().SetTitleSize(0.06)
    residuals.GetYaxis().SetLabelSize(0.05)
    residuals.GetXaxis().SetTitleSize(0.06)
    residuals.GetXaxis().SetLabelSize(0.05)
    residuals.GetYaxis().SetTitleOffset(1.)
    residuals.GetXaxis().SetTitle("m_{ditrk,#gamma} [GeV]")
    residuals.GetXaxis().SetRangeUser(xLowRange, xHighRange)
    residuals.Draw("AP")

c1.Update()

# Legend ----------------------------------------
leg1 = ROOT.TLegend(0.5, 0.39, 0.87, 0.90)  # right positioning
leg1.SetHeader(" ")
leg1.SetNColumns(1)
leg1.SetFillColorAlpha(0, 0.)
leg1.SetBorderSize(0)
leg1.SetLineColor(1)
leg1.SetLineStyle(1)
leg1.SetLineWidth(1)
leg1.SetFillStyle(1001)
# leg1.AddEntry(histo_map["h_MesonMass"],"Data","elp")
# leg1.AddEntry("totPDFOffline","Fit","l")
# leg1.AddEntry("backgroundPDF","Bkg only fit","l")
# leg1.AddEntry(cut_chi2_ggH,"#chi^{2} / ndof = " + cut_chi2_ggH + " / " + str(nParam_ggH),"brNDC")
leg1.Draw()                                                                                                                                   

if includeResiduals:
	c1.SaveAs("/eos/user/g/gumoret/www/latest_production/massanalysis_latest_production/fitsignal_" + CHANNEL + "_BDTcat1_ggH_resid.pdf")
	c1.SaveAs("/eos/user/g/gumoret/www/latest_production/massanalysis_latest_production/fitsignal_" + CHANNEL + "_BDTcat1_ggH_resid.png")
else:
	c1.SaveAs("/eos/user/g/gumoret/www/latest_production/massanalysis_latest_production/fitsignal_" + CHANNEL + "_BDTcat1_ggH.pdf")
	c1.SaveAs("/eos/user/g/gumoret/www/latest_production/massanalysis_latest_production/fitsignal_" + CHANNEL + "_BDTcat1_ggH.png")  
#######################################################################################################

#the same for VBF
fileInput_VBF.cd()
tree_VBF = fileInput_VBF.Get("tree_output")

#Retrieve dataset from the tree, insert the variable also
#dataset_VBF = ROOT.RooDataSet("dataset_VBF","dataset_VBF",ROOT.RooArgSet(mass),ROOT.RooFit.Import(tree_VBF))
dataset_VBF = ROOT.RooDataHist("dataset_VBF", "dataset_VBF", ROOT.RooArgList(mass), h_mH_VBF)

#Do the fit
fitResult_VBF = signalPDF_VBF.fitTo(dataset_VBF,ROOT.RooFit.Save())

#Plot
xframe_VBF = mass.frame(int(xHighRange - xLowRange)*10)
dataset_VBF.plotOn(xframe_VBF)
signalPDF_VBF.plotOn(xframe_VBF)
xframe_VBF.SetTitle("")
ROOT.gStyle.SetOptFit(1111)
xframe_VBF.SetMaximum(1.2*xframe_VBF.GetMaximum())
signalPDF_VBF.paramOn(xframe_VBF,ROOT.RooFit.Layout(0.53,0.94,0.91),ROOT.RooFit.Format("NEU",ROOT.RooFit.AutoPrecision(1))) #,ROOT.RooFit.Layout(0.65,0.90,0.90)
xframe_VBF.getAttText().SetLineWidth(0)
xframe_VBF.getAttText().SetTextSize(0.019)
xframe_VBF.GetXaxis().SetTitle("m_{ditrk,#gamma} [GeV]")
xframe_VBF.GetXaxis().SetRangeUser(110.,160.)
xframe_VBF.GetYaxis().SetMaxDigits(2)

# ChiSquare test ---------------------------------------------------------------------------------------------------------------------------
nParam_VBF = fitResult_VBF.floatParsFinal().getSize()
chi2_VBF = xframe_VBF.chiSquare()  # Returns chi2/ndof. Remember to remove the option XErrorSize(0) from data.PlotOn
cut_chi2_VBF = "{:.2f}".format(chi2_VBF)  # Crop the chi2 to 2 decimal digits

print "nParam_VBF =", nParam_VBF
print "cut_chi2_VBF =", cut_chi2_VBF

c2 = ROOT.TCanvas("c2", "c2", canvas_width, canvas_height + canvas_margin_top)
c2.cd()
c2.SetTitle("")
c2.SetBottomMargin(0.15)  # Increase the empty space at the bottom of the main canvas

if includeResiduals:
    c2.Divide(1, 2, 0, 0.25)  # Divide canvas into two pads: 1x2 grid, with the first pad being 4 times larger
    c2.cd(1)  # Activate the first pad for the main plot
else:
    c2.Divide(1, 1)

xframe_VBF.Draw()

if includeResiduals:
    c2.cd(2)  # Activate the second pad for the residuals plot
    c2.GetPad(2).SetBottomMargin(0.35)  # Increase the empty space at the bottom of the residuals plot
    residuals = xframe_VBF.residHist()
    residuals.SetFillColor(ROOT.kBlue)
    residuals.SetMarkerColor(ROOT.kBlack)
    residuals.GetYaxis().SetTitle("Resid")
    residuals.GetYaxis().SetTitleOffset(1.)
    residuals.GetYaxis().SetTitleSize(0.06)
    residuals.GetYaxis().SetLabelSize(0.05)
    residuals.GetXaxis().SetTitleSize(0.06)
    residuals.GetXaxis().SetLabelSize(0.05)
    residuals.GetYaxis().SetTitleOffset(1.)
    residuals.GetXaxis().SetTitle("m_{ditrk,#gamma} [GeV]")
    residuals.GetXaxis().SetRangeUser(xLowRange, xHighRange)
    residuals.Draw("AP")

c2.Update()

if includeResiduals:
	c2.SaveAs("/eos/user/g/gumoret/www/latest_production/massanalysis_latest_production/fitsignal_" + CHANNEL + "_BDTcat1_VBF_resid.pdf")
	c2.SaveAs("/eos/user/g/gumoret/www/latest_production/massanalysis_latest_production/fitsignal_" + CHANNEL + "_BDTcat1_VBF_resid.png")
else:
	c2.SaveAs("/eos/user/g/gumoret/www/latest_production/massanalysis_latest_production/fitsignal_" + CHANNEL + "_BDTcat1_VBF.pdf")
	c2.SaveAs("/eos/user/g/gumoret/www/latest_production/massanalysis_latest_production/fitsignal_" + CHANNEL + "_BDTcat1_VBF.png")                                                                                                                                                          


#create Workspace
if CHANNEL == "K0s":
    norm_ggH     = fileInput_ggH.Get("h_InvMass_TwoTrk_Photon").Integral() #get the normalization of ggH signal (area under ggH signal)
    sig_norm_ggH = ROOT.RooRealVar(signalPDF_ggH.GetName()+ "_norm", signalPDF_ggH.GetName()+ "_norm", 0.6667*2*norm_ggH)
    norm_VBF     = fileInput_VBF.Get("h_InvMass_TwoTrk_Photon").Integral() #get the normalization of VBF signal (area under VBF signal)
    sig_norm_VBF = ROOT.RooRealVar(signalPDF_VBF.GetName()+ "_norm", signalPDF_VBF.GetName()+ "_norm", 0.6667*2*norm_VBF)
else:
    norm_ggH     = fileInput_ggH.Get("h_InvMass_TwoTrk_Photon").Integral() #get the normalization of ggH signal (area under ggH signal)
    sig_norm_ggH = ROOT.RooRealVar(signalPDF_ggH.GetName()+ "_norm", signalPDF_ggH.GetName()+ "_norm", norm_ggH)
    norm_VBF     = fileInput_VBF.Get("h_InvMass_TwoTrk_Photon").Integral() #get the normalization of VBF signal (area under VBF signal)
    sig_norm_VBF = ROOT.RooRealVar(signalPDF_VBF.GetName()+ "_norm", signalPDF_VBF.GetName()+ "_norm", norm_VBF)  

dCB_pole_ggH.setConstant(1)  
dCB_width_ggH.setConstant(1)  
dCB_aL_ggH.setConstant(1)     
dCB_aR_ggH.setConstant(1)    
dCB_nL_ggH.setConstant(1)    
dCB_nR_ggH.setConstant(1)     
sig_norm_ggH.setConstant(1)

dCB_pole_VBF.setConstant(1)  
dCB_width_VBF.setConstant(1)  
dCB_aL_VBF.setConstant(1)     
dCB_aR_VBF.setConstant(1)    
dCB_nL_VBF.setConstant(1)    
dCB_nR_VBF.setConstant(1)     
sig_norm_VBF.setConstant(1)

'''
#Systematics --------------------------------------------------------------------
fileInput_ggH_TwoProngsSFUP  = ROOT.TFile("histos/latest_production/histos_SR_SignalggHTwoProngsSFUp.root")
fileInput_ggH_TwoProngsSFDW  = ROOT.TFile("histos/latest_production/histos_SR_SignalggHTwoProngsSFDown.root")

signalggH_nominal = fileInput_ggH.Get("h_InvMass_TwoTrk_Photon")
signalggH_nominal.SetName("signal")
signalggH_trigUP  = fileInput_ggH_TwoProngsSFUP.Get("h_InvMass_TwoTrk_Photon")
signalggH_trigUP.SetName("signal_trigEffTwoProngsUp")
signalggH_trigDW  = fileInput_ggH_TwoProngsSFDW.Get("h_InvMass_TwoTrk_Photon")
signalggH_trigDW.SetName("signal_trigEffTwoProngsDown")
#---------------------------------------------------------------------------------
'''

workspace = ROOT.RooWorkspace("workspace_STAT_"+CHANNEL+"_GFcat_bdt1_2018")
getattr(workspace,'import')(signalPDF_ggH)
getattr(workspace,'import')(signalPDF_VBF)
getattr(workspace,'import')(sig_norm_ggH)
getattr(workspace,'import')(sig_norm_VBF)
#getattr(workspace,'import')(dataset_ggH)
#getattr(workspace,'import')(dataset_VBF)
print "ggH Signal integral = ",sig_norm_ggH.Print()
print "VBF Signal integral = ",sig_norm_VBF.Print()

workspace.Print()

print "----------------------"
print "nParam_ggH   = ", nParam_ggH
print "chi2_ggH     = ", chi2_ggH
print "chi2 / ndof  = ", chi2_ggH/float(nParam_ggH)
print ""
print "nParam_VBF   = ", nParam_VBF
print "chi2_VBF     = ", chi2_VBF
print "chi2 / ndof  = ", chi2_VBF/float(nParam_VBF)
print "----------------------"
print ""

fOut = ROOT.TFile("workspaces/workspace_STAT_"+CHANNEL+"_GFcat_bdt1_2018.root","RECREATE")
fOut.cd()
workspace.Write()
xframe_ggH.Write("xframe_ggH")
xframe_VBF.Write("xframe_VBF")
h_mH_ggH.Write("h_mH_ggH")
h_mH_VBF.Write("h_mH_VBF")
#signalggH_nominal.Write()
#signalggH_trigUP.Write()
#signalggH_trigDW.Write()

fOut.Close()	