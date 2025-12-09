from DataFormats.FWLite import Events, Handle
import os
import math
import sys
import numpy as np
#from ROOT import TH1F, TCanvas, TFile, TLegend, gStyle, TPaveText, TArrow
from ROOT import *
import argparse
import tdrstyle, CMS_lumi
import ROOT

#Supress the opening of many Canvas's
ROOT.gROOT.SetBatch(True)   


def BDT_output():

    tdrstyle.setTDRStyle()
    iPeriod = 4
    iPos = 11
    CMS_lumi.lumiTextSize = 0.9
    CMS_lumi.cmsTextSize = 1.
    CMS_lumi.lumi_13TeV = "39.54 fb^{-1}"
    
    f = TFile("outputs/Nominal_training.root")
    
    h_BDT_sig = f.Get("default/Method_BDT/BDT/MVA_BDT_S")
    h_BDT_bkg = f.Get("default/Method_BDT/BDT/MVA_BDT_B")

    h_BDT_Train_sig = f.Get("default/Method_BDT/BDT/MVA_BDT_Train_S")
    h_BDT_Train_bkg = f.Get("default/Method_BDT/BDT/MVA_BDT_Train_B")

    
    leg1 = TLegend(0.40,0.62,0.65,0.87)
    leg1.SetHeader("")
    leg1.SetFillColor(0)
    leg1.SetBorderSize(0)
    leg1.SetLineColor(1)
    leg1.SetLineStyle(1)
    leg1.SetLineWidth(1)
    leg1.SetFillStyle(0)
    leg1.AddEntry(h_BDT_sig,"Signal","f")
    leg1.AddEntry(h_BDT_bkg,"Background","f")
    #leg1.AddEntry(h_BDT_data,"Data","ep")

    channel_text = TPaveText(0.30,0.84,0.65,0.86,"NB,NDC")


    #channel_text.AddText("#phi#gamma channel")
    arrow_SR = TArrow(0.292,2.6,0.59,2.6,0.02,"<|>")#The starting point in x should be 0.285, but then the two arrows overlap
    arrow_CR = TArrow(0.216,2.6,0.285,2.6,0.02,"<|>")
    SR_text  = TPaveText(0.412,2.75,0.454,2.77,"NB")
    CR_text  = TPaveText(0.230,2.75,0.272,2.77,"NB")


    channel_text.SetTextSize(0.04)
    channel_text.SetFillColor(0)
    channel_text.SetFillStyle(0)
    channel_text.SetLineColor(0)
    SR_text.AddText("SR")
    CR_text.AddText("CR")
    arrow_SR.SetLineColor(8)
    arrow_SR.SetLineWidth(2)
    arrow_SR.SetFillColor(8)
    arrow_CR.SetLineColor(kOrange+7)
    arrow_CR.SetLineWidth(2)
    arrow_CR.SetFillColor(kOrange+7)
    SR_text.SetTextSize(0.04)
    SR_text.SetFillColor(0)
    SR_text.SetFillStyle(0)
    SR_text.SetLineColor(0)
    SR_text.SetTextColor(8)
    CR_text.SetTextSize(0.04)
    CR_text.SetFillColor(0)
    CR_text.SetFillStyle(0)
    CR_text.SetLineColor(0)
    CR_text.SetTextColor(kOrange+7)

    gStyle.SetErrorX(0.)
    gStyle.SetOptStat(0)
    canvas1 = TCanvas()
    h_BDT_sig.SetTitle("")
    h_BDT_sig.GetXaxis().SetTitle("BDT discriminant")
    h_BDT_sig.GetXaxis().SetTitleSize(0.055)
    h_BDT_sig.GetYaxis().SetTitle("Arbitrary units")
    h_BDT_sig.GetYaxis().SetTitleSize(0.055)
    h_BDT_bkg.SetTitle("")
    h_BDT_sig.SetFillColor(38)
    h_BDT_sig.SetFillStyle(3002)
    #h_BDT_sig.SetLineColor(1)
    h_BDT_bkg.SetFillColor(2)
    h_BDT_bkg.SetLineColor(2)
    h_BDT_bkg.SetFillStyle(3002)
    h_BDT_sig.Draw("E1, hist")
    h_BDT_bkg.Draw("SAME, E1, hist")
    #h_BDT_data.Draw("SAME, lep")
    h_BDT_Train_sig.SetLineColor(8)
    h_BDT_Train_sig.SetMarkerColor(8)
    h_BDT_Train_sig.SetMarkerStyle(21)
    h_BDT_Train_bkg.SetLineColor(9)
    h_BDT_Train_bkg.SetMarkerColor(9)
    h_BDT_Train_bkg.SetMarkerStyle(21)
    h_BDT_Train_sig.Draw("SAME, lep")
    h_BDT_Train_bkg.Draw("SAME, lep")

    canvas1.SetLogy()
    h_BDT_sig.SetMaximum(50*h_BDT_sig.GetMaximum())

    leg1.Draw("SAME")
    channel_text.Draw("SAME")
    #SR_text.Draw("SAME")
    #CR_text.Draw("SAME")
    #arrow_SR.Draw()
    #arrow_CR.Draw()
    CMS_lumi.CMS_lumi(canvas1, iPeriod, iPos)

    canvas1.SaveAs("/afs/cern.ch/user/g/gumoret/cernbox/www/latest_production/MVA_latest_production/h_BDT_output.pdf")
    canvas1.SaveAs("/afs/cern.ch/user/g/gumoret/cernbox/www/latest_production/MVA_latest_production/h_BDT_output.png")
    

    #raw_input()

def rejB_vs_S():

    f1 = TFile("outputs/Nominal_training.root")

    h_rejB_vs_S_1 = f1.Get("default/Method_BDT/BDT/MVA_BDT_rejBvsS")

    leg2 = TLegend(0.2,0.6,0.6,0.7)
    #leg1.SetHeader(" ")
    leg2.SetFillColor(0)
    leg2.SetBorderSize(0)
    leg2.SetLineColor(1)
    leg2.SetLineStyle(1)
    leg2.SetLineWidth(1)
    leg2.SetFillStyle(0)
    #leg2.AddEntry(h_rejB_vs_S_1,"with data sidebands","l")
    #leg2.AddEntry(h_rejB_vs_S_1,"shifted","l")
    #leg2.AddEntry(h_rejB_vs_S_1,"with m_{#pi#gamma}","l")
    #leg2.AddEntry(h_rejB_vs_S_1,"with m_{T}(#lep,#MET)","l")
    #leg2.AddEntry(h_rejB_vs_S_1,"sin^{2}#theta","l")
    #leg2.AddEntry(h_rejB_vs_S_1,"train: 2018, test: 2017","l")
    #leg2.AddEntry(h_rejB_vs_S_1,"cos#theta","l")
    #leg2.AddEntry(h_rejB_vs_S_1,"testing","l")
    #leg2.AddEntry(h_rejB_vs_S_1,"with signal scaled down","l")
    #leg2.AddEntry(h_rejB_vs_S_2,"with MC","l")
    #leg2.AddEntry(h_rejB_vs_S_2,"without #Delta#varphi_{l,#gamma}","l")
    #leg2.AddEntry(h_rejB_vs_S_2,"without m_{#pi#gamma}","l")
    #leg2.AddEntry(h_rejB_vs_S_2,"train: 2018, test: 2018","l")
    #leg2.AddEntry(h_rejB_vs_S_2,"with signal non scaled","l")

    gStyle.SetOptStat(0)
    canvas2 = TCanvas()
    h_rejB_vs_S_1.SetTitle(" ")
    h_rejB_vs_S_1.SetLineColor(1)
    h_rejB_vs_S_1.SetLineWidth(3)
    h_rejB_vs_S_1.Draw("hist")
    leg2.Draw("SAME")

    canvas2.SaveAs("/afs/cern.ch/user/g/gumoret/cernbox/www/latest_production/MVA_latest_production/h_rejBvsS.pdf")
    canvas2.SaveAs("/afs/cern.ch/user/g/gumoret/cernbox/www/latest_production/MVA_latest_production/h_rejBvsS.png")

    #raw_input()

if __name__ == "__main__":

    rejB_vs_S()
    BDT_output()
