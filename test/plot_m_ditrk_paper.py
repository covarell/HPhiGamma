import ROOT
import argparse
import math
import numpy as np
import sys
import copy
import tdrstyle
from array import array
from ROOT import gROOT, RooFit, gPad, gStyle
import os, sys

#Supress the opening of many Canvas's
ROOT.gROOT.SetBatch(True) 

#input
CHANNEL = str(sys.argv[1])

if CHANNEL == "Rho":
	xLabel        = "m_{#pi#pi} [GeV]"
	channel_text  = "#rho#gamma"
	meson_decay   = "#rho #rightarrow #pi^{+}#pi^{-}"
	xMinLine      = 0.62
	xMaxLine      = 0.92
	channel_color = ROOT.TColor.GetColor(228, 37, 54)
	# Construct signal pdf
	mass_min = 0.55
	mass_max = 1.
	mean_central ,  mean_min,  mean_max = 0.77,mass_min,mass_max
	sigma_central, sigma_min, sigma_max = 0.022,0.0001,0.1
	width_central, width_min, width_max = 0.047,0.0,0.2
	YLabel = "Events / 15 MeV"

elif CHANNEL == "Phi":
	xLabel        = "m_{KK} [GeV]"
	channel_text  = "#phi#gamma"
	meson_decay   = "#phi #rightarrow K^{+}K^{-}"
	xMinLine      = 1.008
	xMaxLine      = 1.032
	channel_color = ROOT.TColor.GetColor(87, 144, 252)
	# Construct signal pdf
	mass_min = 1.
	mass_max = 1.042
	mean_central ,  mean_min,  mean_max = 1.02,mass_min,mass_max
	sigma_central, sigma_min, sigma_max = 0.0022,0.00001,0.01
	width_central, width_min, width_max = 0.0042,0.00001,0.0044
	YLabel = "Events / 1.4 MeV"

elif CHANNEL == "K0s":
	xLabel        = "m_{K#pi} [GeV]"
	channel_text  = "K^{*0}#gamma"
	meson_decay   = "K^{*0} #rightarrow K^{#pm}#pi^{#mp}"
	xMinLine      = 0.842
	xMaxLine      = 0.942
	channel_color = ROOT.TColor.GetColor(150, 74, 139)
	# Construct signal pdf
	mass_min = 0.8
	mass_max = 1.
	mean_central ,  mean_min,  mean_max = 0.892,mass_min,mass_max
	sigma_central, sigma_min, sigma_max = 0.0052,0.00005,0.05
	width_central, width_min, width_max = 0.0042,0.00001,0.0044
	YLabel = "Events / 6.7 MeV"

# P l o t s
# ---------------------------------------------------

#CMS-style plotting 
tdrstyle.cmsPrel(39500, energy= 13,simOnly=False, textScale=1.2)
tdrstyle.setTDRStyle(False)
lumi = "39.5"

# Plot results
# INPUT ###########################################################################################################
fileData   = ROOT.TFile("histos/latest_production/histos_All_preselection_Data_"+CHANNEL+".root")
fileSignal = ROOT.TFile("histos/latest_production/histos_All_preselection_SignalggH_"+CHANNEL+".root")

treeData   = fileData.Get("tree_output")
treeSignal = fileSignal.Get("tree_output")

nEntriesData = treeData.GetEntriesFast()

print "nEntriesData = ",nEntriesData

h_Signal = fileSignal.Get("h_meson_InvMass_TwoTrk")

# C r e a t e   m o d e l  
# -------------------------------------------------------------

# Create observables
mass = ROOT.RooRealVar("mesonMass","ditrack invariant mass",mass_min,mass_max)

mean  = ROOT.RooRealVar("mean","The mean of the gaussian pdf", mean_central, mean_min, mean_max)
sigma = ROOT.RooRealVar("sigma","The sigma of the gaussian pdf", sigma_central, sigma_min, sigma_max)
width = ROOT.RooRealVar("width","The width of the gaussian pdf", width_central, width_min, width_max)

#mean2  = ROOT.RooRealVar("mean2","The mean2 of the gaussian pdf", mean_central, mean_min, mean_max)
#sigma2 = ROOT.RooRealVar("sigma2","The width2 of the gaussian pdf", sigma_central, sigma_min, sigma_max)

signalPDF = ROOT.RooGaussian("signalPDF","Gauss pdf",mass,mean,sigma)
#signalPDF2 = ROOT.RooGaussian("signalPDF2","Gauss pdf2",mass,mean2,sigma2)
signalPDF = ROOT.RooVoigtian("signalPDF","Voigtian pdf",mass,mean,width,sigma)


# Construct background pdf
a1_central, a1_min, a1_max = 0.1,-0.5,0.5
a2_central, a2_min, a2_max = 0.3,-2.,2.
a3_central, a3_min, a3_max = 0.3,-2.,2.

a1_off = ROOT.RooRealVar("a1_off","The a1 of background", a1_central, a1_min, a1_max)
a2_off = ROOT.RooRealVar("a2_off","The a2 of background", a2_central, a2_min, a2_max)
a3_off = ROOT.RooRealVar("a3_off","The a3 of background", a3_central, a3_min, a3_max)

a1_trg = ROOT.RooRealVar("a1_trg","The a1 of background", a1_central, a1_min, a1_max)
a2_trg = ROOT.RooRealVar("a2_trg","The a2 of background", a2_central, a2_min, a2_max)
a3_trg = ROOT.RooRealVar("a3_trg","The a3 of background", a3_central, a3_min, a3_max)

backgroundPDF = ROOT.RooChebychev("backgroundPDF","The background PDF",mass,ROOT.RooArgList(a1_off,a2_off,a3_off))
#backgroundPDFFail = ROOT.RooChebychev("backgroundPDFFail","The background PDF for Fail dataset",mass,ROOT.RooArgList(a1_off,a2_off))
#backgroundPDFPass = ROOT.RooChebychev("backgroundPDFPass","The background PDF for Pass dataset",mass,ROOT.RooArgList(a1_off,a2_off))

# N   e v e n t s
# ---------------------------------------------------------------
nsig = ROOT.RooRealVar("nsig", "signal yield", nEntriesData/10,0.,nEntriesData/2)
nbkg = ROOT.RooRealVar("nbkgFail", "background yield", 0.8*nEntriesData,nEntriesData/2,1.5*nEntriesData)

# R e t r i e v e   d a t a s e t s
# ---------------------------------------------------------------
data   = ROOT.RooDataSet("dataset","dataset",ROOT.RooArgSet(mass),ROOT.RooFit.Import(treeData))
#signal = ROOT.RooDataHist("signal","signal",ROOT.RooArgList(mass), h_Signal)

# C r e a t e   t h e   m o d e l
# ---------------------------------------------------------------
model = ROOT.RooAddPdf("model", "Signal and Background PDF", ROOT.RooArgList(signalPDF, backgroundPDF), ROOT.RooArgList(nsig, nbkg))

# D o   t h e   f i t
# ---------------------------------------------------------------
fitResult = model.fitTo(data,ROOT.RooFit.Extended(True), ROOT.RooFit.Save())
fitResult.Print()

#fitSignal = signalPDF2.fitTo(signal,ROOT.RooFit.Extended(True), ROOT.RooFit.Save())
#fitSignal.Print()

#Canvas
canvas = ROOT.TCanvas()
canvas.cd()

#Plot the fit
#FRAME
massFrame = mass.frame(30)

data.plotOn(massFrame, ROOT.RooFit.Name("data"),ROOT.RooFit.XErrorSize(0))

#Areas
model.plotOn(massFrame, ROOT.RooFit.Components("signalPDF,backgroundPDF"),ROOT.RooFit.FillColor(channel_color),ROOT.RooFit.Name("sigArea"),ROOT.RooFit.FillStyle(4100),ROOT.RooFit.DrawOption("F"), ROOT.RooFit.LineColor(ROOT.kGreen+2), ROOT.RooFit.LineStyle(ROOT.kDashed))#frame1.GetXaxis().SetLabelSize(0.033)
model.plotOn(massFrame, ROOT.RooFit.Components("backgroundPDF"),ROOT.RooFit.FillColor(16),ROOT.RooFit.Name("bkgArea"),ROOT.RooFit.FillStyle(4100),ROOT.RooFit.DrawOption("F"), ROOT.RooFit.LineColor(ROOT.kGreen+2), ROOT.RooFit.LineStyle(ROOT.kDashed))#frame1.GetXaxis().SetLabelSize(0.033)

#Fit lines
model.plotOn(massFrame, ROOT.RooFit.Components("backgroundPDF"),ROOT.RooFit.Name("bkgOnly"), ROOT.RooFit.LineColor(12), ROOT.RooFit.LineWidth(3), ROOT.RooFit.LineStyle(ROOT.kDashed)) #frame1.GetXaxis().SetLabelSize(0.033)
model.plotOn(massFrame, ROOT.RooFit.Name("fit"), ROOT.RooFit.Components("signalPDF,backgroundPDF"), ROOT.RooFit.LineColor(1), ROOT.RooFit.LineWidth(3))
#signalPDF2.plotOn(massFrame, ROOT.RooFit.Components("signalPDF2"),ROOT.RooFit.Name("signalPDF2"),ROOT.RooFit.LineStyle(1),ROOT.RooFit.LineColor(channel_color),RooFit.Normalization(0.2))

data.plotOn(massFrame, ROOT.RooFit.Name("data"),ROOT.RooFit.XErrorSize(0))
#signal.plotOn(massFrame, ROOT.RooFit.Name("signal"),ROOT.RooFit.LineStyle(1),ROOT.RooFit.LineColor(channel_color))

magnifier = 1.6
massFrame.SetMaximum(magnifier * massFrame.GetMaximum())

gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)

#signal MC
h_Signal.Scale(h_Signal.Integral()/500000.)
h_Signal.SetLineStyle(1)	
h_Signal.SetLineColor(channel_color)
h_Signal.SetLineWidth(4)

#Vertical lines
leftLine  = ROOT.TLine(xMinLine,0.,xMinLine,0.9*massFrame.GetMaximum()/magnifier)
rightLine = ROOT.TLine(xMaxLine,0.,xMaxLine,0.9*massFrame.GetMaximum()/magnifier)
leftLine.SetLineColor(1)
leftLine.SetLineStyle(7)
leftLine.SetLineWidth(3)
rightLine.SetLineColor(1)
rightLine.SetLineStyle(7)
rightLine.SetLineWidth(3)

#Axes
massFrame.GetXaxis().SetTitle(xLabel)
massFrame.GetXaxis().SetLabelSize(0.04)
massFrame.GetYaxis().SetLabelSize(0.04)
massFrame.SetMinimum(1) #to remove the first bin label "0"
massFrame.GetXaxis().SetTitleSize(0.05)
massFrame.GetYaxis().SetTitleSize(0.05)
massFrame.GetXaxis().SetTitleOffset(1.2)
massFrame.GetYaxis().SetTitleOffset(1.4)
massFrame.GetYaxis().SetTitle(YLabel)

#Legend
leg1 = ROOT.TLegend(0.59,0.71,0.92,0.95) #right positioning
leg1.SetEntrySeparation(0.01)
leg1.SetHeader(" ")
leg1.SetFillColorAlpha(0,0.)
leg1.SetBorderSize(0)
leg1.SetLineColor(1)
leg1.SetLineStyle(1)
leg1.SetLineWidth(1)
leg1.SetFillStyle(1001)
leg1.SetNColumns(1)
leg1.AddEntry(massFrame.findObject("data"),"Data","ep")
leg1.AddEntry(massFrame.findObject("fit"),"Fit Result","l")
leg1.AddEntry(massFrame.findObject("bkgOnly"),"Total background","l")

#gPad.RedrawAxis()
#gPad.Update()
gStyle.SetErrorX(0)

massFrame.Draw("E1")
leftLine.Draw("SAME")
rightLine.Draw("SAME")

#latex.Draw("SAME")
leg1.Draw("SAME")

canvas.Update()

latex = ROOT.TLatex();
latex.SetNDC();

cmsx = 0.165
cmsy = 0.96

latex.SetTextSize(0.85*canvas.GetTopMargin());
latex.SetTextFont(62);
latex.SetTextAlign(11);
latex.DrawLatex(cmsx,cmsy,"CMS");

latex.SetTextSize(0.85*canvas.GetTopMargin());
latex.SetTextFont(52);
latex.SetTextAlign(11);
#latex.DrawLatex(cmsx+0.065,cmsy,"Preliminary");

latex.SetTextSize(0.82*canvas.GetTopMargin());
latex.SetTextFont(42);
latex.SetTextAlign(11);
latex.DrawLatex(cmsx+0.61,cmsy,"39.5 fb^{-1} (13 TeV)");

latex.SetTextSize(0.98*canvas.GetTopMargin());
latex.SetTextFont(42);
latex.SetTextAlign(11);
latex.DrawLatex(cmsx+0.05,0.86,"ggH");

latex.SetTextSize(0.98*canvas.GetTopMargin());
latex.SetTextFont(42);
latex.SetTextAlign(11);
latex.DrawLatex(cmsx+0.05,0.79,meson_decay);

canvas.SaveAs("/eos/user/g/gumoret/www/paper_plots/m_ditrk_"+CHANNEL+".pdf")
canvas.SaveAs("/eos/user/g/gumoret/www/paper_plots/m_ditrk_"+CHANNEL+".png")