import ROOT
import cmsstyle
import argparse

#bool initialization
includeResiduals   = True  # Flag to include the residuals subplot

#INPUT and OUTPUT #############################################################################################
#Input
p = argparse.ArgumentParser(description='Select rootfile to plot')
p.add_argument('Decay_channel_option', help='Type <<Ds>> for Dstar') #flag for bkg estimation
args = p.parse_args()

CHANNEL = "Dstar"
print ('H -> DstarGamma analysis')

#Signal input rootfiles ---------------------------------------------------------------
fileInput_ggH = ROOT.TFile("./SR_HDst_ORTrigger_BDTCat0_Signal.root")
tree_ggH = fileInput_ggH.Get("tree_output")

#Import the Doube Crystal Ball PDF -----------------------------------------------------
ROOT.gROOT.ProcessLineSync(".L ./dCB/RooDoubleCBFast.cc+")

#Supress the opening of many Canvas's ---------------------------------------------------
ROOT.gROOT.SetBatch(True)   

#CMS-style plotting ---------------------------------------------------------------
cmsstyle.setCMSStyle()
iPeriod = 4
iPos = 11
#CMS_lumi.lumiTextSize = 0.7
#CMS_lumi.lumiTextOffset = 0.25
#CMS_lumi.cmsTextSize = 0.8
#CMS_lumi.cmsTextOffset = 0.4
#CMS_lumi.lumi_13TeV = "39.54 fb^{-1}" 

#prepare a rebinned TH1 for Higgs mass ---------------------------------------------------------------
xLowRange  = 110.
xHighRange = 140.

h_mH_ggH = ROOT.TH1F("h_mH_ggH","h_mH_ggH", int(xHighRange - xLowRange)*10, xLowRange, xHighRange)

nentries_ggH = tree_ggH.GetEntriesFast()

for jentry in range(nentries_ggH):
    ientry = tree_ggH.LoadTree( jentry )
    if ientry < 0:
        break
    nb = tree_ggH.GetEntry(jentry)
    if nb <= 0:
        print ('nb < 0')
        continue

    h_mH_ggH.Fill(tree_ggH.bosonMass, tree_ggH._eventWeight)

#Define the observable ---------------------------------------------------------------
bosonMass = ROOT.RooRealVar("bosonMass", "bosonMass", 125., xLowRange, xHighRange, "GeV/c^2")

#Double Crystal Ball definition ---------------------------------------------------------------
#dCB_pole_ggH  = ROOT.RooRealVar("dCB_pole_"+CHANNEL+"_GFcat_bdt0_ggH", "Double CB pole", 120.,118.,122.)
#dCB_width_ggH = ROOT.RooRealVar("dCB_width_"+CHANNEL+"_GFcat_bdt0_ggH", "Double CB width",2.,0.5,4.5)
#dCB_aL_ggH    = ROOT.RooRealVar("dCB_aL_"+CHANNEL+"_GFcat_bdt0_ggH", "Double CB alpha left", 1.2, 1., 5.)
#dCB_aR_ggH    = ROOT.RooRealVar("dCB_aR_"+CHANNEL+"_GFcat_bdt0_ggH", "Double CB alpha right", 1.5, 1., 5.)
#dCB_nL_ggH    = ROOT.RooRealVar("dCB_nL_"+CHANNEL+"_GFcat_bdt0_ggH", "Double CB n left", 3.1, 0.1, 4.)
#dCB_nR_ggH    = ROOT.RooRealVar("dCB_nR_"+CHANNEL+"_GFcat_bdt0_ggH", "Double CB n right", 3.1, 0.1, 4.)
gauss_mean_ggH     = ROOT.RooRealVar("gauss_mean_"+CHANNEL+"_GFcat_bdt0_ggH", "Gaussian width", 121., 118., 122.)
gauss_width_ggH    = ROOT.RooRealVar("gauss_width_"+CHANNEL+"_GFcat_bdt0_ggH", "Gaussian width", 2., 1.5, 5.)
f_gauss_ggH        = ROOT.RooRealVar("f_gauss_"+CHANNEL+"_GFcat_bdt0_ggH", "Gaussian fraction", 0.3, 0.2, 0.4)
gauss_mean_ggH     = ROOT.RooRealVar("gauss_mean_"+CHANNEL+"_GFcat_bdt0_ggH", "Gaussian width", 121., 118., 122.)
gauss2_width_ggH    = ROOT.RooRealVar("gauss2_width_"+CHANNEL+"_GFcat_bdt0_ggH", "Gaussian width 2", 5., 2.5, 7.5)
f_gauss2_ggH        = ROOT.RooRealVar("f_gauss2_"+CHANNEL+"_GFcat_bdt0_ggH", "Gaussian fraction 2", 0.1, 0.02, 0.2)
#ellpis_axis_ggH     = ROOT.RooRealVar("ellpis_axis_ggH", "Axis ellipse", 5.5, 3., 8.)
#ellpis_cent_ggH     = ROOT.RooRealVar("ellpis_cent_ggH", "Center ellipse", 120.5, 118., 123.)
#f_ellpis_ggH        = ROOT.RooRealVar("f_ellpis"+CHANNEL+"_GFcat_bdt0_ggH", "Ellipse fraction", 0.3, 0.1, 0.6)

dcb_ggH = ROOT.RooDoubleCBFast("crystal_ball_"+CHANNEL+"_GFcat_bdt0_ggH", "Double Crystal Ball", bosonMass, dCB_pole_ggH, dCB_width_ggH, dCB_aL_ggH, dCB_nL_ggH, dCB_aR_ggH, dCB_nR_ggH)
gauss_ggH = ROOT.RooGaussian("gauss_"+CHANNEL+"_GFcat_bdt0_ggH", "Gaussian", bosonMass, gauss_mean_ggH, gauss_width_ggH)
gauss2_ggH = ROOT.RooGaussian("gauss2_"+CHANNEL+"_GFcat_bdt0_ggH", "Gaussian", bosonMass, gauss_mean_ggH, gauss2_width_ggH)
#halfEllipse_ggH = ROOT.RooGenericPdf(
#    "halfEllipse_ggH",
#    "((abs(bosonMass-ellpis_cent_ggH) < ellpis_axis_ggH) ? sqrt(1 - ((bosonMass-ellpis_cent_ggH)/ellpis_axis_ggH)^2) : 0)",
#    ROOT.RooArgList(bosonMass, ellpis_cent_ggH, ellpis_axis_ggH)
#)
signalPDF_ggH = ROOT.RooAddPdf("signalPDF_"+CHANNEL+"_GFcat_bdt0_ggH", "total",ROOT.RooArgList(gauss_ggH,gauss2_ggH,dcb_ggH),ROOT.RooArgList(f_gauss_ggH,f_gauss2_ggH))


#Input tree ------------------------------------------------------------------------------------------------------------------------------
fileInput_ggH.cd()
tree_ggH = fileInput_ggH.Get("tree_output")

#Retrieve dataset from the tree, insert the variable also ---------------------------------------------------------------
#dataset_ggH = ROOT.RooDataSet("dataset_ggH","dataset_ggH", ROOT.RooArgSet(bosonMass), ROOT.RooFit.Import(tree_ggH))
dataset_ggH = ROOT.RooDataHist("dataset_ggH", "dataset_ggH", ROOT.RooArgList(bosonMass), h_mH_ggH)

#Do the fit ------------------------------------------------------------------------------------------------------------------------------
fitResult_ggH = signalPDF_ggH.fitTo(dataset_ggH,ROOT.RooFit.Save())

#Plot ------------------------------------------------------------------------------------------------------------------------------
# Custom canvas dimensions
canvas_width      = 800
canvas_height     = 800
canvas_margin_top = 100  # Empty space added at the top of the main canvas

xframe_ggH = bosonMass.frame(int(xHighRange - xLowRange)*4)
dataset_ggH.plotOn(xframe_ggH)
signalPDF_ggH.plotOn(xframe_ggH)
xframe_ggH.SetTitle("")
ROOT.gStyle.SetOptFit(1111)
xframe_ggH.SetMaximum(1.2 * xframe_ggH.GetMaximum())
signalPDF_ggH.paramOn(xframe_ggH, ROOT.RooFit.Layout(0.53, 0.94, 0.91), ROOT.RooFit.Format("NEU", ROOT.RooFit.AutoPrecision(1)))  # ,ROOT.RooFit.Layout(0.65,0.90,0.90)
xframe_ggH.getAttText().SetLineWidth(0)
xframe_ggH.getAttText().SetTextSize(0.019)
xframe_ggH.GetXaxis().SetTitle("m_{M,#gamma} [GeV]")
xframe_ggH.GetXaxis().SetRangeUser(xLowRange, xHighRange)
#xframe_ggH.GetYaxis().SetMaxDigits(2)

# ChiSquare test ---------------------------------------------------------------------------------------------------------------------------
nParam_ggH = fitResult_ggH.floatParsFinal().getSize()
chi2_ggH = xframe_ggH.chiSquare()  # Returns chi2/ndof. Remember to remove the option XErrorSize(0) from data.PlotOn
my_ndof = int(xHighRange-xLowRange)*4 - nParam_ggH
cut_chi2_ggH = "{:.2f}".format(chi2_ggH*my_ndof) #Crop the chi2 to 2 decimal digits

print('nParam_ggH =', nParam_ggH)
print('cut_chi2_ggH =', cut_chi2_ggH)

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
leg1 = ROOT.TLegend(0.6, 0.29, 0.87, 0.70)  # right positioning
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
leg1.AddEntry(cut_chi2_ggH,"#chi^{2} / ndof = " + cut_chi2_ggH + " / " + str(my_ndof),"brNDC")
leg1.Draw()                                                                                                                                         

if includeResiduals:
	c1.SaveAs("/eos/user/c/covarell/www/AN-26-106/fitsignal_" + CHANNEL + "_BDTcat0_ggH_resid.pdf")
	c1.SaveAs("/eos/user/c/covarell/www/AN-26-106/fitsignal_" + CHANNEL + "_BDTcat0_ggH_resid.png")
else:
	c1.SaveAs("/eos/user/c/covarell/www/AN-26-106/fitsignal_" + CHANNEL + "_BDTcat0_ggH.pdf")
	c1.SaveAs("/eos/user/c/covarell/www/AN-26-106/fitsignal_" + CHANNEL + "_BDTcat0_ggH.png")  
#######################################################################################################

#the same for VBF
#fileInput_VBF.cd()
#tree_VBF = fileInput_VBF.Get("tree_output")

#Retrieve dataset from the tree, insert the variable also
#dataset_VBF = ROOT.RooDataSet("dataset_VBF","dataset_VBF",ROOT.RooArgSet(mass),ROOT.RooFit.Import(tree_VBF))
#dataset_VBF = ROOT.RooDataHist("dataset_VBF", "dataset_VBF", ROOT.RooArgList(mass), h_mH_VBF)

#Do the fit
#fitResult_VBF = signalPDF_VBF.fitTo(dataset_VBF,ROOT.RooFit.Save())

#Plot
#xframe_VBF = mass.frame(int(xHighRange - xLowRange)*10)
#dataset_VBF.plotOn(xframe_VBF)
#signalPDF_VBF.plotOn(xframe_VBF)
#xframe_VBF.SetTitle("")
#ROOT.gStyle.SetOptFit(1111)
#xframe_VBF.SetMaximum(1.2*xframe_VBF.GetMaximum())
#signalPDF_VBF.paramOn(xframe_VBF,ROOT.RooFit.Layout(0.53,0.94,0.91),ROOT.RooFit.Format("NEU",ROOT.RooFit.AutoPrecision(1))) #,ROOT.RooFit.Layout(0.65,0.90,0.90)
#xframe_VBF.getAttText().SetLineWidth(0)
#xframe_VBF.getAttText().SetTextSize(0.019)
#xframe_VBF.GetXaxis().SetTitle("m_{ditrk,#gamma} [GeV]")
#xframe_VBF.GetXaxis().SetRangeUser(xLowRange,xHighRange)
#xframe_VBF.GetYaxis().SetMaxDigits(2)

# ChiSquare test ---------------------------------------------------------------------------------------------------------------------------
#nParam_VBF = fitResult_VBF.floatParsFinal().getSize()
#chi2_VBF = xframe_VBF.chiSquare()  # Returns chi2/ndof. Remember to remove the option XErrorSize(0) from data.PlotOn
#cut_chi2_VBF = "{:.2f}".format(chi2_VBF)  # Crop the chi2 to 2 decimal digits
#
#print('nParam_VBF =", nParam_VBF
#print('cut_chi2_VBF =", cut_chi2_VBF
#
#c2 = ROOT.TCanvas("c2", "c2", canvas_width, canvas_height + canvas_margin_top)
#c2.cd()
#c2.SetTitle("")
#c2.SetBottomMargin(0.15)  # Increase the empty space at the bottom of the main canvas
#
#if includeResiduals:
#    c2.Divide(1, 2, 0, 0.25)  # Divide canvas into two pads: 1x2 grid, with the first pad being 4 times larger
#    c2.cd(1)  # Activate the first pad for the main plot
#else:
#    c2.Divide(1, 1)
#
#xframe_VBF.Draw()

#if includeResiduals:
#    c2.cd(2)  # Activate the second pad for the residuals plot
#    c2.GetPad(2).SetBottomMargin(0.35)  # Increase the empty space at the bottom of the residuals plot
#    residuals = xframe_VBF.residHist()
#    residuals.SetFillColor(ROOT.kBlue)
#    residuals.SetMarkerColor(ROOT.kBlack)
#    residuals.GetYaxis().SetTitle("Resid")
#    residuals.GetYaxis().SetTitleOffset(1.)
#    residuals.GetYaxis().SetTitleSize(0.06)
#    residuals.GetYaxis().SetLabelSize(0.05)
#    residuals.GetXaxis().SetTitleSize(0.06)
#    residuals.GetXaxis().SetLabelSize(0.05)
#    residuals.GetYaxis().SetTitleOffset(1.)
#    residuals.GetXaxis().SetTitle("m_{ditrk,#gamma} [GeV]")
#    residuals.GetXaxis().SetRangeUser(xLowRange, xHighRange)
#    residuals.Draw("AP")
#
#c2.Update()

#if includeResiduals:
#	c2.SaveAs("/eos/user/c/covarell/www/AN-26-106/fitsignal_" + CHANNEL + "_BDTcat0_VBF_resid.pdf")
#	c2.SaveAs("/eos/user/c/covarell/www/AN-26-106/fitsignal_" + CHANNEL + "_BDTcat0_VBF_resid.png")
#else:
#	c2.SaveAs("/eos/user/c/covarell/www/AN-26-106/fitsignal_" + CHANNEL + "_BDTcat0_VBF.pdf")
#	c2.SaveAs("/eos/user/c/covarell/www/AN-26-106/fitsignal_" + CHANNEL + "_BDTcat0_VBF.png")
                                      
#create Workspace
if CHANNEL == "Dstar": #norm factor x2 to include the Dbar channel
    norm_ggH     = fileInput_ggH.Get("h_bosonMass").Integral() #get the normalization of ggH signal (area under ggH signal)
    sig_norm_ggH = ROOT.RooRealVar(signalPDF_ggH.GetName()+ "_norm", signalPDF_ggH.GetName()+ "_norm", 0.0394*2*norm_ggH) 
    #norm_VBF     = fileInput_VBF.Get("h_bosonMass").Integral() #get the normalization of VBF signal (area under VBF signal)
    #sig_norm_VBF = ROOT.RooRealVar(signalPDF_VBF.GetName()+ "_norm", signalPDF_VBF.GetName()+ "_norm", 0.0394*2*norm_VBF)
else:
    norm_ggH     = fileInput_ggH.Get("h_bosonMass").Integral() #get the normalization of ggH signal (area under ggH signal)
    sig_norm_ggH = ROOT.RooRealVar(signalPDF_ggH.GetName()+ "_norm", signalPDF_ggH.GetName()+ "_norm", norm_ggH)
    #norm_VBF     = fileInput_VBF.Get("h_bosonMass").Integral() #get the normalization of VBF signal (area under VBF signal)
    #sig_norm_VBF = ROOT.RooRealVar(signalPDF_VBF.GetName()+ "_norm", signalPDF_VBF.GetName()+ "_norm", norm_VBF)    

dCB_pole_ggH.setConstant(1)  
dCB_width_ggH.setConstant(1)  
dCB_aL_ggH.setConstant(1)     
dCB_aR_ggH.setConstant(1)    
dCB_nL_ggH.setConstant(1)    
dCB_nR_ggH.setConstant(1)     
sig_norm_ggH.setConstant(1)

#dCB_pole_VBF.setConstant(1)  
#dCB_width_VBF.setConstant(1)  
#dCB_aL_VBF.setConstant(1)     
#dCB_aR_VBF.setConstant(1)    
#dCB_nL_VBF.setConstant(1)    
#dCB_nR_VBF.setConstant(1)     
#sig_norm_VBF.setConstant(1)

'''
#Systematics --------------------------------------------------------------------
fileInput_ggH_TwoProngsSFUP  = ROOT.TFile("histos/latest_production/histos_SR_SignalggHTwoProngsSFUp.root")
fileInput_ggH_TwoProngsSFDW  = ROOT.TFile("histos/latest_production/histos_SR_SignalggHTwoProngsSFDown.root")

signalggH_nominal = fileInput_ggH.Get("h_bosonMass")
signalggH_nominal.SetName("signal")
signalggH_trigUP  = fileInput_ggH_TwoProngsSFUP.Get("h_bosonMass")
signalggH_trigUP.SetName("signal_trigEffTwoProngsUp")
signalggH_trigDW  = fileInput_ggH_TwoProngsSFDW.Get("h_bosonMass")
signalggH_trigDW.SetName("signal_trigEffTwoProngsDown")
#---------------------------------------------------------------------------------
'''
fOut = ROOT.TFile("workspaces/workspace_STAT_"+CHANNEL+"_GFcat_bdt0_2024.root","UPDATE")
fOut.cd()

workspace = fOut.Get("workspace_STAT_"+CHANNEL+"_GFcat_bdt0_2024")
getattr(workspace,'import')(signalPDF_ggH)
#getattr(workspace,'import')(signalPDF_VBF)
getattr(workspace,'import')(sig_norm_ggH)
#getattr(workspace,'import')(sig_norm_VBF)
#getattr(workspace,'import')(dataset_ggH)
#getattr(workspace,'import')(dataset_VBF)
print('ggH Signal integral = ',sig_norm_ggH.getVal())
#print('VBF Signal integral = ",sig_norm_VBF.Print()

workspace.Print()

print('----------------------')
print('nParam_ggH   = ', nParam_ggH)
print('chi2_ggH     = ', chi2_ggH)
#print('chi2 / ndof  = ', chi2_ggH/float(nParam_ggH))
#print('"
#print('nParam_VBF   = ", nParam_VBF
#print('chi2_VBF     = ", chi2_VBF
#print('chi2 / ndof  = ", chi2_VBF/float(nParam_VBF)
print('----------------------')
print('')

workspace.Write()
xframe_ggH.Write("xframe_ggH")
#xframe_VBF.Write("xframe_VBF")
h_mH_ggH.Write("h_mH_ggH")
#h_mH_VBF.Write("h_mH_VBF")
#signalggH_nominal.Write()
#signalggH_trigUP.Write()
#signalggH_trigDW.Write()

fOut.Close()	
