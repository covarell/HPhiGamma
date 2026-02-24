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
	meson_dacay   = "#rho #rightarrow #pi^{+}#pi^{-}"
	xMinLine      = 0.62
	xMaxLine      = 0.92
	channel_color = 99
	# Construct signal pdf
	mass_min = 0.5
	mass_max = 1.
	mean_central ,  mean_min,  mean_max = 0.77,mass_min,mass_max
	sigma_central, sigma_min, sigma_max = 0.022,0.0001,0.1
	YLabel = "Event / (0.017)"
	fileRecoVsGen = ROOT.TFile("histos/231102_Rho/histos_SR_preselection_SignalggH.root")
	fitMin,fitMax = -0.02,0.02


elif CHANNEL == "Phi":
	xLabel        = "m_{KK} [GeV]"
	channel_text  = "#phi#gamma"
	meson_dacay   = "#phi #rightarrow K^{+}K^{-}"
	xMinLine      = 1.008
	xMaxLine      = 1.032
	channel_color = 70
	# Construct signal pdf
	mass_min = 1.
	mass_max = 1.042
	mean_central ,  mean_min,  mean_max = 1.02,mass_min,mass_max
	sigma_central, sigma_min, sigma_max = 0.0022,0.00001,0.01
	YLabel = "Event / (0.001)"
	fileRecoVsGen = ROOT.TFile("histos/231102_Phi/histos_SR_preselection_SignalggH.root")
	fitMin,fitMax = -0.01,0.01

elif CHANNEL == "K0s":
	xLabel        = "m_{K#pi} [GeV]"
	channel_text  = "K^{*0}#gamma"
	meson_dacay   = "K^{*0} #rightarrow K^{#pm}#pi^{#mp}"
	xMinLine      = 0.842
	xMaxLine      = 0.942
	channel_color = 51
	# Construct signal pdf
	mass_min = 0.8
	mass_max = 1.
	mean_central ,  mean_min,  mean_max = 0.892,mass_min,mass_max
	sigma_central, sigma_min, sigma_max = 0.0052,0.00005,0.05
	YLabel = "Event / (0.007)"
	fileRecoVsGen = ROOT.TFile("histos/231109_K0s/histos_SR_preselection_SignalggH.root")
	fitMin,fitMax = -0.02,0.02


# P l o t s
# ---------------------------------------------------

#Import the Doube Crystal Ball PDF -----------------------------------------------------
ROOT.gROOT.ProcessLineSync(".L MassAnalysis/dCB/RooDoubleCBFast.cc+")

#CMS-style plotting 
tdrstyle.cmsPrel(39500, energy= 13,simOnly=False, textScale=1.2)
tdrstyle.setTDRStyle(False)
lumi = "39.5"

#m_ditrk reco vs gen
m_recoVsGen = ROOT.RooRealVar("m_recoVsGen","m^{reco}_{ditrk} - m^{gen}_{ditrk} (GeV)",-0.04,0.04)
m_recoVsGen.setRange("SubRange",fitMin,fitMax)

mean2  = ROOT.RooRealVar("mean2","The mean of the gaussian pdf", 0., -0.02,0.02)
sigma = ROOT.RooRealVar("sigma","The width of the gaussian pdf", 0.01, 0.00,0.02)
#signalPDF2 = ROOT.RooGaussian("signalPDF2","Gauss pdf",m_recoVsGen,mean2,sigma)


dCB_pole_ggH  = ROOT.RooRealVar("dCB_pole_GFcat_bdt0_ggH", "Double CB pole", -0.04,0.04)
sigma         = ROOT.RooRealVar("sigma", "sigma",0.01, 0.00,0.02)
dCB_aL_ggH    = ROOT.RooRealVar("dCB_aL_GFcat_bdt0_ggH", "Double CB alpha left", 1.2, 1., 5.)
dCB_aR_ggH    = ROOT.RooRealVar("dCB_aR_GFcat_bdt0_ggH", "Double CB alpha right", 1.5, 1., 2.)
dCB_nL_ggH    = ROOT.RooRealVar("dCB_nL_GFcat_bdt0_ggH", "Double CB n left", 3.1, 0.1, 10.)
dCB_nR_ggH    = ROOT.RooRealVar("dCB_nR_GFcat_bdt0_ggH", "Double CB n right", 3.4, 0., 20.)
signalPDF2 = ROOT.RooDoubleCBFast("signalPDF2", "Double Crystal Ball", m_recoVsGen, dCB_pole_ggH, sigma, dCB_aL_ggH, dCB_nL_ggH, dCB_aR_ggH, dCB_nR_ggH)


# INPUT ###########################################################################################################
h_RecoVsGen = fileRecoVsGen.Get("h_MrecoMinusMgen")

# D o   t h e   f i t
# ---------------------------------------------------------------
data2 = ROOT.RooDataHist("h_RecoVsGen","h_RecoVsGen",ROOT.RooArgList(m_recoVsGen),h_RecoVsGen)
fitResult2 = signalPDF2.fitTo(data2, ROOT.RooFit.Range("SubRange"), ROOT.RooFit.Save())
fitResult2.Print()

#Canvas
canvas2 = ROOT.TCanvas()
canvas2.cd()

#Plot the fit
#FRAME
massFrame2 = m_recoVsGen.frame(50)

data2.plotOn(massFrame2, ROOT.RooFit.Name("data2"),ROOT.RooFit.XErrorSize(0),ROOT.RooFit.MarkerColor(channel_color)) #
signalPDF2.plotOn(massFrame2, ROOT.RooFit.Name("signalPDF2"), ROOT.RooFit.LineColor(1), ROOT.RooFit.LineWidth(3),ROOT.RooFit.Range("SubRange"))

massFrame2.GetXaxis().SetLabelSize(0.04)
massFrame2.GetYaxis().SetLabelSize(0.04)
massFrame2.GetXaxis().SetTitleSize(0.042)
massFrame2.GetYaxis().SetTitleSize(0.042)
massFrame2.GetXaxis().SetTitleOffset(1.5)
massFrame2.GetYaxis().SetTitleOffset(1.5)

magnifier = 1.3
massFrame2.SetMaximum(magnifier * massFrame2.GetMaximum())

#Legend
leg2 = ROOT.TLegend(0.65,0.72,0.92,0.92) #right positioning
leg2.SetEntrySeparation(0.01)
leg2.SetHeader(" ")
leg2.SetFillColorAlpha(0,0.)
leg2.SetBorderSize(0)
leg2.SetLineColor(1)
leg2.SetLineStyle(1)
leg2.SetLineWidth(1)
leg2.SetFillStyle(1001)
leg2.SetNColumns(1)
leg2.AddEntry(massFrame2.findObject("data2"),"MC signal","ep")
leg2.AddEntry(massFrame2.findObject("signalPDF2"),"Fit Result","l")

massFrame2.Draw("E1")
leg2.Draw("SAME")
canvas2.Update()

latex = ROOT.TLatex();
latex.SetNDC();

latex.SetTextSize(0.98*canvas2.GetTopMargin());
latex.SetTextFont(42);
latex.SetTextAlign(11);
latex.DrawLatex(0.2,0.86,meson_dacay);
latex.DrawLatex(0.2,0.8,"sigma = "+str(round(sigma.getValV()*1000,2))+" MeV")


canvas2.SaveAs("/eos/user/g/gumoret/www/paper_plots/m_ditrk_"+CHANNEL+"_signal.pdf")
canvas2.SaveAs("/eos/user/g/gumoret/www/paper_plots/m_ditrk_"+CHANNEL+"_signal.png")
