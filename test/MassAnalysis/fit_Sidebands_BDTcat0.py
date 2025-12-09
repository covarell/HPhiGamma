import ROOT
import tdrstyle, CMS_lumi
import argparse

#####################################################
# This script takes the fit_Signal.py workspace and
# update it with a RooMultiPDF containing bkg models
# with their normalizations
#####################################################

#Supress the opening of many Canvas's
ROOT.gROOT.SetBatch(True)   

#bool initialization
isRhoGammaAnalysis = False
isPhiGammaAnalysis = False
isK0sGammaAnalysis = False

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

#CMS-style plotting ---------------------------------------------------------------
tdrstyle.setTDRStyle()
iPeriod = 4
iPos = 11
CMS_lumi.lumiTextSize = 0.7
CMS_lumi.lumiTextOffset = 0.25
CMS_lumi.cmsTextSize = 0.8
#CMS_lumi.cmsTextOffset = 0.4
CMS_lumi.lumi_13TeV = "39.54 fb^{-1}" 

#Parameters of the PDF ---------------------------------------------------------------
xLowRange  = 110.
xHighRange = 160.

mass = ROOT.RooRealVar("mesonGammaMass","mesonGammaMass",xLowRange,xHighRange,"GeV")
mass.setRange("LowSideband",xLowRange,120.)
mass.setRange("HighSideband",130.,xHighRange)
mass.setRange("full",xLowRange,xHighRange)

#Initialize a Chebychev pdf
a_bkg = ROOT.RooRealVar("a_bkg_chebychev_"+CHANNEL+"_GFcat_bdt0","a_bkg",-1.,-3.,0.)
b_bkg = ROOT.RooRealVar("b_bkg_chebychev_"+CHANNEL+"_GFcat_bdt0","b_bkg",0.3,-3.,1.)
c_bkg = ROOT.RooRealVar("c_bkg_chebychev_"+CHANNEL+"_GFcat_bdt0","c_bkg",-0.01,-1.,1.)
d_bkg = ROOT.RooRealVar("d_bkg_chebychev_"+CHANNEL+"_GFcat_bdt0","d_bkg",-0.05,-0.2,0.1)
f_bkg = ROOT.RooRealVar("e_bkg_chebychev_"+CHANNEL+"_GFcat_bdt0","e_bkg",-0.05,-0.1,0.)
if isPhiGammaAnalysis:
	bkgPDF_chebychev  = ROOT.RooChebychev("chebychev_GFcat_bdt0_bkg","bkgPDF",mass,ROOT.RooArgList(a_bkg, b_bkg))
	bkgPDF_chebychev_Nplus1 = ROOT.RooChebychev("chebychev_Nplus1_GFcat_bdt0_bkg","bkgPDF",mass,ROOT.RooArgList(a_bkg,b_bkg,c_bkg))
else:
	bkgPDF_chebychev  = ROOT.RooChebychev("chebychev_GFcat_bdt0_bkg","bkgPDF",mass,ROOT.RooArgList(a_bkg, b_bkg))
	bkgPDF_chebychev_Nplus1 = ROOT.RooChebychev("chebychev_Nplus1_GFcat_bdt0_bkg","bkgPDF",mass,ROOT.RooArgList(a_bkg,b_bkg,c_bkg))
#bkgPDF_chebychev  = ROOT.RooChebychev("chebychev_GFcat_bdt0_bkg","bkgPDF",mass,ROOT.RooArgList(a_bkg, b_bkg, c_bkg))
#bkgPDF_chebychev_Nplus1 = ROOT.RooChebychev("chebychev_Nplus1_GFcat_bdt0_bkg","bkgPDF",mass,ROOT.RooArgList(a_bkg,b_bkg,c_bkg, d_bkg))

#Initialize a exponential pdf
e1_bkg = ROOT.RooRealVar("e1_bkg_exponential_"+CHANNEL+"_GFcat_bdt0","e1_bkg",-0.031,-1.,0.)
exp1   = ROOT.RooExponential("exponential1_GFcat_bdt0_bkg","bkgPDF",mass,e1_bkg)
e2_bkg = ROOT.RooRealVar("e2_bkg_exponential_"+CHANNEL+"_GFcat_bdt0","e2_bkg",-0.931,-1.,0.)
exp2   = ROOT.RooExponential("exponential2_GFcat_bdt0_bkg","bkgPDF",mass,e2_bkg)
frac_exp = ROOT.RooRealVar("f0_bkg_exponential_"+CHANNEL+"_GFcat_bdt0","frac_exp",0.,1.)

#bkgPDF_exponential = ROOT.RooAddPdf("exponential_GFcat_bdt0_bkg","bkgPDF",ROOT.RooArgList(exp1,exp2),ROOT.RooArgList(frac_exp))
bkgPDF_exponential = ROOT.RooExponential("exponential_GFcat_bdt0_bkg","bkgPDF",mass,e1_bkg)
#if CHANNEL == "Phi": bkgPDF_exponential = ROOT.RooExponential("exponential_GFcat_bdt0_bkg","bkgPDF",mass,e1_bkg)

#Initialize a Bernstein pdf
bern_c0 = ROOT.RooRealVar("c0_bkg_bernstein_"+CHANNEL+"_GFcat_bdt0", 'bern_c0', 0.05)#0.05, 0.,0.1)
bern_c1 = ROOT.RooRealVar("c1_bkg_bernstein_"+CHANNEL+"_GFcat_bdt0", 'bern_c1', 0.01, 0.,1.)
bern_c2 = ROOT.RooRealVar("c2_bkg_bernstein_"+CHANNEL+"_GFcat_bdt0", 'bern_c2', 0.01, 0.,1.)
bern_c3 = ROOT.RooRealVar("c3_bkg_bernstein_"+CHANNEL+"_GFcat_bdt0", 'bern_c3', 0.05, 0.,1.)
bern_c4 = ROOT.RooRealVar("c4_bkg_bernstein_"+CHANNEL+"_GFcat_bdt0", 'bern_c4', 0.05, 0., 5.)
bern_c5 = ROOT.RooRealVar("c5_bkg_bernstein_"+CHANNEL+"_GFcat_bdt0", 'bern_c5', 1e-2, 0., 0.1)
if isPhiGammaAnalysis:
	bkgPDF_bernstein = ROOT.RooBernstein("bernstein_GFcat_bdt0_bkg", "bkgPDF", mass, ROOT.RooArgList(bern_c0,bern_c1,bern_c2,bern_c3))
else:
	bkgPDF_bernstein = ROOT.RooBernstein("bernstein_GFcat_bdt0_bkg", "bkgPDF", mass, ROOT.RooArgList(bern_c0,bern_c1,bern_c2))
#bkgPDF_bernstein = ROOT.RooBernstein("bernstein_GFcat_bdt0_bkg", "bkgPDF", mass, ROOT.RooArgList(bern_c0,bern_c1,bern_c2,bern_c3,bern_c4))

#bkgPDF_bernstein  = ROOT.RooProdPdf("bkgPDF_bernstein","bkg PDF",ROOT.RooArgSet(e1_bkg,bkgPDF_bernstein1))

#Initialize a Landau pdf
#mean_land = ROOT.RooRealVar("mean_land","mean_land",0., 0.,100.)
#sigma_land = ROOT.RooRealVar("sigma_land","sigma_land",0.,0.,5.)
#bkgPDF_bernstein = ROOT.RooLandau("bkgPDFland","BG function",mass,mean_land,sigma_land)

#Input file and tree ---------------------------------------------------------------
fileInput = ROOT.TFile("histos/latest_production/histos_SR_BDTcat0_Data.root")
fileInput.cd()
tree = fileInput.Get("tree_output")

h_mass = ROOT.TH1F("h_mass","h_mass", int(xHighRange - xLowRange), xLowRange, xHighRange)

nentries_histo = tree.GetEntriesFast()
print "nentries_histo = ",nentries_histo

for jentry in xrange(nentries_histo):
    ientry = tree.LoadTree( jentry )
    if ientry < 0:
        break
    nb = tree.GetEntry(jentry)
    if nb <= 0:
        print "nb < 0"
        continue

    h_mass.Fill(tree.mesonGammaMass, tree._eventWeight)

#Retrieve observed_data from the tree, insert the variable also ---------------------------------------------------------------
observed_data = ROOT.RooDataSet("observed_data","observed_data",ROOT.RooArgSet(mass),ROOT.RooFit.Import(tree))
#observed_data = ROOT.RooDataHist("observed_data","observed_data",ROOT.RooArgList(mass),h_mass)
nEntries = observed_data.numEntries() 
print "nEntries = ",nEntries

#Give the blind range ------------------------------------------------------------------------------------------------------------------------
data_blinded = observed_data.reduce("mesonGammaMass < 120. || mesonGammaMass > 130.")

#Do the fit ------------------------------------------------------------------------------------------------------------------------------
fitResult_chebychev   = bkgPDF_chebychev.fitTo(observed_data,ROOT.RooFit.Save())
fitResult_bernstein   = bkgPDF_bernstein.fitTo(observed_data,ROOT.RooFit.Save())
fitResult_exponential = bkgPDF_exponential.fitTo(observed_data,ROOT.RooFit.Save())
fitResult_chebychev_Nplus1  = bkgPDF_chebychev_Nplus1.fitTo(observed_data,ROOT.RooFit.Save())

#ROOT.RooFit.Range("LowSideband,HighSideband")
#Do the F-test ------------------------------------------------------------------------------------------------------------------------------
print "################## F-TEST"
print "minNll = ", fitResult_chebychev.minNll()
print "2Delta_minNll = ", 2*(19265.2886079-fitResult_chebychev.minNll()) # If 2*(NLL(N)-NLL(N+1)) > 3.85 -> N+1 is significant improvement
print "##################"

#Plot ------------------------------------------------------------------------------------------------------------------------
canvas_chebychev = ROOT.TCanvas()
canvas_chebychev.cd()

#Chebychev frame
if isPhiGammaAnalysis:
	xframe_chebychev = mass.frame(30)
else:
	xframe_chebychev = mass.frame(60)

data_blinded.plotOn(xframe_chebychev)
bkgPDF_chebychev.plotOn(xframe_chebychev,ROOT.RooFit.NormRange("LowSideband,HighSideband"),ROOT.RooFit.Range("LowSideband,HighSideband"),ROOT.RooFit.Name("bkgPDF_chebychev"),ROOT.RooFit.LineColor(ROOT.kBlue))
xframe_chebychev.SetTitle("#sqrt{s} = 13 TeV       lumi = 39.54/fb")
xframe_chebychev.GetXaxis().SetTitle("m_{ditrk,#gamma} [GeV]")
xframe_chebychev.SetMaximum(1.3*xframe_chebychev.GetMaximum())
bkgPDF_chebychev.paramOn(xframe_chebychev,ROOT.RooFit.Layout(0.45,0.94,0.91),ROOT.RooFit.Format("NEU",ROOT.RooFit.AutoPrecision(1))) #,ROOT.RooFit.Layout(0.65,0.90,0.90)
xframe_chebychev.getAttText().SetTextSize(0.02)
xframe_chebychev.Draw() #remember to draw the frame before the legend initialization to fill the latter correctly

#Calculate Chi square and parameters 
nParam_cheby = fitResult_chebychev.floatParsFinal().getSize()
chi2_cheby = xframe_chebychev.chiSquare()#Returns chi2. Remember to remove the option XErrorSize(0) from data.PlotOn
cut_chi2_cheby = "{:.2f}".format(chi2_cheby) #Crop the chi2 to 2 decimal digits
print "Chi square cheby = ",chi2_cheby
print "n param cheby = ",nParam_cheby
print ""

leg1 = ROOT.TLegend(0.5,0.62,0.72,0.90) #right positioning
leg1.SetHeader(" ")
leg1.SetNColumns(1)
leg1.SetFillColorAlpha(0,0.)
leg1.SetBorderSize(0)
leg1.SetLineColor(1)
leg1.SetLineStyle(1)
leg1.SetLineWidth(1)
leg1.SetFillStyle(1001)
leg1.AddEntry(cut_chi2_cheby,"#chi^{2}/ndof = " + cut_chi2_cheby + " / " + str(nParam_cheby),"brNDC")

leg1.Draw()

CMS_lumi.CMS_lumi(canvas_chebychev, iPeriod, iPos) #Print integrated lumi and energy information

canvas_chebychev.SaveAs("/eos/user/g/gumoret/www/latest_production/massanalysis_latest_production/fit_sidebands_GFcat_bdt0_chebychev.pdf")
canvas_chebychev.SaveAs("/eos/user/g/gumoret/www/latest_production/massanalysis_latest_production/fit_sidebands_GFcat_bdt0_chebychev.png")


#Bernstein frame
canvas_bernstein = ROOT.TCanvas()
canvas_bernstein.cd()

if isPhiGammaAnalysis:
	xframe_bernstein = mass.frame(40)
else:
	xframe_bernstein = mass.frame(60)

data_blinded.plotOn(xframe_bernstein)
bkgPDF_bernstein.plotOn(xframe_bernstein,ROOT.RooFit.NormRange("LowSideband,HighSideband"),ROOT.RooFit.Range("LowSideband,HighSideband"),ROOT.RooFit.Name("bkgPDF_bernstein"), ROOT.RooFit.LineColor(ROOT.kGreen))
xframe_bernstein.SetTitle("#sqrt{s} = 13 TeV       lumi = 39.54/fb")
xframe_bernstein.GetXaxis().SetTitle("m_{ditrk,#gamma} [GeV]")
xframe_bernstein.SetMaximum(1.3*xframe_bernstein.GetMaximum())
bkgPDF_bernstein.paramOn(xframe_bernstein,ROOT.RooFit.Layout(0.45,0.94,0.91),ROOT.RooFit.Format("NEU",ROOT.RooFit.AutoPrecision(1))) #,ROOT.RooFit.Layout(0.65,0.90,0.90)
xframe_bernstein.getAttText().SetTextSize(0.02)
xframe_bernstein.Draw() #remember to draw the frame before the legend initialization to fill the latter correctly

nParam_bern = fitResult_bernstein.floatParsFinal().getSize()
chi2_bern = xframe_bernstein.chiSquare()#Returns chi2. Remember to remove the option XErrorSize(0) from data.PlotOn
cut_chi2_bern = "{:.2f}".format(chi2_bern) #Crop the chi2 to 2 decimal digits
print "Chi square bern = ",chi2_bern
print "n param bern = ",nParam_bern

leg2 = ROOT.TLegend(0.5,0.52,0.72,0.80) #right positioning
leg2.SetHeader(" ")
leg2.SetNColumns(1)
leg2.SetFillColorAlpha(0,0.)
leg2.SetBorderSize(0)
leg2.SetLineColor(1)
leg2.SetLineStyle(1)
leg2.SetLineWidth(1)
leg2.SetFillStyle(1001)
leg2.AddEntry(cut_chi2_bern,"#chi^{2}/ndof = " + cut_chi2_bern + " / " + str(nParam_bern),"brNDC")

leg2.Draw()

CMS_lumi.CMS_lumi(canvas_bernstein, iPeriod, iPos) #Print integrated lumi and energy information

canvas_bernstein.SaveAs("/eos/user/g/gumoret/www/latest_production/massanalysis_latest_production/fit_sidebands_GFcat_bdt0_bernstein.pdf")
canvas_bernstein.SaveAs("/eos/user/g/gumoret/www/latest_production/massanalysis_latest_production/fit_sidebands_GFcat_bdt0_bernstein.png")

#Exponential frame
canvas_exponential = ROOT.TCanvas()
canvas_exponential.cd()

if isPhiGammaAnalysis:
	xframe_exponential = mass.frame(40)
else:
	xframe_exponential = mass.frame(60)

data_blinded.plotOn(xframe_exponential)
bkgPDF_exponential.plotOn(xframe_exponential,ROOT.RooFit.Range("LowSideband,HighSideband"),ROOT.RooFit.Name("bkgPDF_exponential"), ROOT.RooFit.LineColor(ROOT.kRed))
xframe_exponential.SetTitle("#sqrt{s} = 13 TeV       lumi = 39.54/fb")
xframe_exponential.GetXaxis().SetTitle("m_{ditrk,#gamma} [GeV]")
xframe_exponential.SetMaximum(1.3*xframe_exponential.GetMaximum())
bkgPDF_exponential.paramOn(xframe_exponential,ROOT.RooFit.Layout(0.45,0.94,0.91),ROOT.RooFit.Format("NEU",ROOT.RooFit.AutoPrecision(1))) #,ROOT.RooFit.Layout(0.65,0.90,0.90)
xframe_exponential.getAttText().SetTextSize(0.02)
xframe_exponential.Draw() #remember to draw the frame before the legend initialization to fill the latter correctly

nParam_exp = fitResult_exponential.floatParsFinal().getSize()
chi2_exp = xframe_exponential.chiSquare()#Returns chi2. Remember to remove the option XErrorSize(0) from data.PlotOn
cut_chi2_exp = "{:.2f}".format(chi2_exp) #Crop the chi2 to 2 decimal digits
print "Chi square exp = ",chi2_exp
print "n param exp = ",nParam_exp

leg2 = ROOT.TLegend(0.5,0.62,0.72,0.90) #right positioning
leg2.SetHeader(" ")
leg2.SetNColumns(1)
leg2.SetFillColorAlpha(0,0.)
leg2.SetBorderSize(0)
leg2.SetLineColor(1)
leg2.SetLineStyle(1)
leg2.SetLineWidth(1)
leg2.SetFillStyle(1001)
leg2.AddEntry(cut_chi2_exp,"#chi^{2}/ndof = " + cut_chi2_exp + " / " + str(nParam_exp),"brNDC")

leg2.Draw()

CMS_lumi.CMS_lumi(canvas_exponential, iPeriod, iPos) #Print integrated lumi and energy information

canvas_exponential.SaveAs("/eos/user/g/gumoret/www/latest_production/massanalysis_latest_production/fit_sidebands_GFcat_bdt0_exponential.pdf")
canvas_exponential.SaveAs("/eos/user/g/gumoret/www/latest_production/massanalysis_latest_production/fit_sidebands_GFcat_bdt0_exponential.png")


#Plot ------------------------------------------------------------------------------------------------------------------------
canvas_chebychev_Nplus1 = ROOT.TCanvas()
canvas_chebychev_Nplus1.cd()

#chebychev_Nplus1 frame
if isPhiGammaAnalysis:
	xframe_chebychev_Nplus1 = mass.frame(40)
else:
	xframe_chebychev_Nplus1 = mass.frame(60)

data_blinded.plotOn(xframe_chebychev_Nplus1)
bkgPDF_chebychev_Nplus1.plotOn(xframe_chebychev_Nplus1,ROOT.RooFit.NormRange("LowSideband,HighSideband"),ROOT.RooFit.Range("LowSideband,HighSideband"),ROOT.RooFit.Name("bkgPDF_chebychev_Nplus1"),ROOT.RooFit.LineColor(ROOT.kBlue))
xframe_chebychev_Nplus1.SetTitle("#sqrt{s} = 13 TeV       lumi = 39.54/fb")
xframe_chebychev_Nplus1.GetXaxis().SetTitle("m_{ditrk,#gamma} [GeV]")
xframe_chebychev_Nplus1.SetMaximum(1.3*xframe_chebychev_Nplus1.GetMaximum())
bkgPDF_chebychev_Nplus1.paramOn(xframe_chebychev_Nplus1,ROOT.RooFit.Layout(0.45,0.94,0.91),ROOT.RooFit.Format("NEU",ROOT.RooFit.AutoPrecision(1))) #,ROOT.RooFit.Layout(0.65,0.90,0.90)
xframe_chebychev_Nplus1.getAttText().SetTextSize(0.02)
xframe_chebychev_Nplus1.Draw() #remember to draw the frame before the legend initialization to fill the latter correctly

#Calculate Chi square and parameters 
nParam_cheby = fitResult_chebychev_Nplus1.floatParsFinal().getSize()
chi2_cheby = xframe_chebychev_Nplus1.chiSquare()#Returns chi2. Remember to remove the option XErrorSize(0) from data.PlotOn
cut_chi2_cheby = "{:.2f}".format(chi2_cheby) #Crop the chi2 to 2 decimal digits
print "Chi square cheby = ",chi2_cheby
print "n param cheby = ",nParam_cheby
print ""

leg1 = ROOT.TLegend(0.5,0.52,0.72,0.80) #right positioning
leg1.SetHeader(" ")
leg1.SetNColumns(1)
leg1.SetFillColorAlpha(0,0.)
leg1.SetBorderSize(0)
leg1.SetLineColor(1)
leg1.SetLineStyle(1)
leg1.SetLineWidth(1)
leg1.SetFillStyle(1001)
leg1.AddEntry(cut_chi2_cheby,"#chi^{2}/ndof = " + cut_chi2_cheby + " / " + str(nParam_cheby),"brNDC")

leg1.Draw()

CMS_lumi.CMS_lumi(canvas_chebychev_Nplus1, iPeriod, iPos) #Print integrated lumi and energy information

canvas_chebychev_Nplus1.SaveAs("/eos/user/g/gumoret/www/latest_production/massanalysis_latest_production/fit_sidebands_GFcat_bdt0_chebychev_Nplus1.pdf")
canvas_chebychev_Nplus1.SaveAs("/eos/user/g/gumoret/www/latest_production/massanalysis_latest_production/fit_sidebands_GFcat_bdt0_chebychev_Nplus1.png")


# Multipdf ------------------------------------------------------------------------------------------------------------------------------
cat = ROOT.RooCategory("pdf_index_GFcat_bdt0","Index of Pdf which is active")
mypdfs = ROOT.RooArgList()
mypdfs.add(bkgPDF_chebychev)
mypdfs.add(bkgPDF_bernstein)
mypdfs.add(bkgPDF_exponential)
#mypdfs.add(bkgPDF_chebychev_Nplus1)

multipdf = ROOT.RooMultiPdf("multipdf_"+CHANNEL+"_GFcat_bdt0_bkg","All Pdfs",cat,mypdfs)

#create Workspace ------------------------------------------------------------------------------------------------------------------------------
norm     = nEntries #fileInput.Get("h_InvMass_TwoTrk_Photon").Integral() #get the normalization of ggH signal (area under ggH signal)
bkg_norm = ROOT.RooRealVar(multipdf.GetName()+ "_norm", multipdf.GetName()+ "_norm", norm,0.5*norm, 2*norm)

print "************************************** n. events = ",nEntries
#workspace = ROOT.RooWorkspace("myworkspace")
#getattr(workspace,'import')(bkgPDF_chebychev)
#getattr(workspace,'import')(bkgPDF_bernstein)

inputWS = ROOT.TFile("workspaces/workspace_STAT_"+CHANNEL+"_GFcat_bdt0_2018.root") #there's only one ws for both ggH and VBF 
inputWS.cd()
workspace = inputWS.Get("workspace_STAT_"+CHANNEL+"_GFcat_bdt0_2018")
#getattr(workspace,'import')(bkgPDF_chebychev)
#getattr(workspace,'import')(bkgPDF_bernstein)
#getattr(workspace,'import')(bkgPDF_exponential)
getattr(workspace,'import')(cat)
getattr(workspace,'import')(multipdf)
getattr(workspace,'import')(observed_data)
getattr(workspace,'import')(bkg_norm)
print("integral BKG",bkg_norm.Print())
#workspace.Print()

#fOut = ROOT.TFile("workspaces/ws_sidebands.root","RECREATE")
fOut = ROOT.TFile("workspaces/workspace_STAT_"+CHANNEL+"_GFcat_bdt0_2018.root","UPDATE")
fOut.cd()
workspace.Write()
#print "-------------------------------------------"
#print "Final print to check the workspace update:"
#workspace.Print()
fOut.Close()


