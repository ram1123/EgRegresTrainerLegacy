import sys

if sys.version_info[0] < 3:
    print("This script requires Python 3. Please use Python 3 to run this script.")
    sys.exit()

import ROOT
from ROOT import TFile, TTree, TH1F, TCanvas, TLegend, TLatex
ROOT.gROOT.SetBatch(True)

#set the tdr style
import CMS_lumi, tdrstyle
tdrstyle.setTDRStyle()
ROOT.gStyle.SetOptStat(0)

CMS_lumi.lumi_7TeV = "4.8 fb^{-1}"
CMS_lumi.lumi_8TeV = "18.3 fb^{-1}"
CMS_lumi.writeExtraText = 1
CMS_lumi.extraText = "      Simulation Preliminary"
CMS_lumi.lumi_sqrtS = "" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
iPeriod = 0
iPos = 0

# Input uncorrected file
InputFile_UnCorr = "/eos/cms/store/group/phys_egamma/ec/Run3Studies/SCRegression/ReducedNtuples/FixedClusterSize_REAL.root"
Tree_Uncorr = "egHLTRun3Tree"
var3 = "eg_energy/eg_gen_energy"

# Input corrected file
InputFile_CorrectedFile = "/eos/user/r/rasharma/post_doc_ihep/EGamma/HLT/regression/MainNtuples_v2/results/resultSC_UpdatedEtaDef_23March/Run3HLT_RealIC_RealTraining_stdVar_stdCuts_ntrees1500_applied.root"
Tree1_Corrected = "egHLTRun3Tree"

# Variables to be plotted using the new corrected root file
var1 = "eg_rawEnergy/eg_gen_energy"
var2 = "regInvTar*regMean"

# Open input files and get trees
f_uncorr = TFile.Open(InputFile_UnCorr)
tree_uncorr = f_uncorr.Get(Tree_Uncorr)

f_corr = TFile.Open(InputFile_CorrectedFile)
tree_corr = f_corr.Get(Tree1_Corrected)

# Define the cuts
cut_configs = [
    # pattern of below array: (suffix, suffix_symbol, nBins, minX, maxX, pt_low, pt_high, etaCutVal)
    ("Barrel", "<", 108, 0.50, 1.20, 10, 20, 1.479),
    ("Barrel", "<", 108, 0.65, 1.15, 20, 60, 1.479),
    ("Barrel", "<", 108, 0.80, 1.07, 60, 200, 1.479),
    ("Endcap", ">", 108, 0.30, 1.40, 10, 20, 1.479),
    ("Endcap", ">", 108, 0.55, 1.20, 20, 60, 1.479),
    ("Endcap", ">", 108, 0.70, 1.15, 60, 200, 1.479),
]


for suffix, suffix_symbol, nBins, minX, maxX, pt_low, pt_high, etaCutVal in cut_configs:
    etaCut = f"abs(eg_gen_eta) {suffix_symbol} {etaCutVal}"
    cut = f"eg_gen_pt>{pt_low} && eg_gen_pt<{pt_high} && {etaCut}"

    # Create histograms
    h3_uncorr = TH1F(f"h3_uncorr_{suffix}", ";E^{reco}/E^{gen};Entries", nBins, minX, maxX)
    h1_corr = TH1F(f"h1_corr_{suffix}", ";E^{reco}/E^{gen};Entries", nBins, minX, maxX)
    h2_corr = TH1F(f"h2_corr_{suffix}", ";E^{reco}/E^{gen};Entries", nBins, minX, maxX)

    # Fill histograms
    tree_uncorr.Draw(f"{var3}>>h3_uncorr_{suffix}", cut)
    tree_corr.Draw(f"{var1}>>h1_corr_{suffix}", cut)
    tree_corr.Draw(f"{var2}>>h2_corr_{suffix}", cut)

    # Normalize histograms
    h3_uncorr.Scale(1.0 / h3_uncorr.Integral())
    h1_corr.Scale(1.0 / h1_corr.Integral())
    h2_corr.Scale(1.0 / h2_corr.Integral())

    # Draw histograms
    c = TCanvas(f"c_{suffix}", "", 800, 600)
    h3_uncorr.SetLineColor(ROOT.kBlack)
    h1_corr.SetLineColor(ROOT.kRed)
    h2_corr.SetLineColor(ROOT.kBlue)

    h3_uncorr.SetMarkerColor(ROOT.kBlack)
    h1_corr.SetMarkerColor(ROOT.kRed)
    h2_corr.SetMarkerColor(ROOT.kBlue)

    # Get maximum Y value from three histograms, and set it as the maximum Y value for the canvas
    if suffix == "Barrel":
        multiplicative_factor = 1.1
    else:
        multiplicative_factor = 1.1
    h3_uncorr.SetMaximum(ROOT.TMath.Max(h3_uncorr.GetMaximum()*multiplicative_factor,h1_corr.GetMaximum()*multiplicative_factor))
    h3_uncorr.SetMaximum(ROOT.TMath.Max(h3_uncorr.GetMaximum()*multiplicative_factor,h2_corr.GetMaximum()*multiplicative_factor))

    h3_uncorr.Draw()
    h1_corr.Draw("SAME")
    h2_corr.Draw("SAME")

    # Add legend
    leg = TLegend(0.7, 0.7, 0.9, 0.9)
    leg.AddEntry(h3_uncorr, "Corrected run2", "lp")
    leg.AddEntry(h1_corr, "Raw", "lp")
    leg.AddEntry(h2_corr, "Corrected new", "lp")
    # leg.Draw()

    l = ROOT.TLatex()
    l.SetTextSize(0.040)

    # Add mean and standard deviation for each histogram on the canvas
    l.SetTextColor(ROOT.kBlue)
    l.DrawLatexNDC(0.18, 0.91, "Corrected new:  (#mu, #sigma) = (%.3f,%.3f)" % (h2_corr.GetMean(), h2_corr.GetStdDev()))
    l.SetTextColor(ROOT.kBlack)
    l.DrawLatexNDC(0.18, 0.87, "Corrected run2: (#mu, #sigma) = (%.3f,%.3f)" % (h3_uncorr.GetMean(), h3_uncorr.GetStdDev()))
    l.SetTextColor(ROOT.kRed)
    l.DrawLatexNDC(0.18, 0.82, "Raw:  (#mu, #sigma) = (%.3f,%.3f)" % (h1_corr.GetMean(), h1_corr.GetStdDev()))

    # Add the pT and eta cuts on the canvas
    l.SetTextColor(ROOT.kBlack)
    l.DrawLatexNDC(0.18, 0.77, str(pt_low) +" < p_{T}^{gen} < " + str(pt_high))
    l.DrawLatexNDC(0.18, 0.72,"| #eta^{gen} | " + suffix_symbol + str(etaCutVal))

    # Add CMS Preliminary label
    CMS_lumi.CMS_lumi(c, iPeriod, iPos)

    # Save the output plots
    c.SaveAs(f"new_17March/comparison_plot_{suffix}_pt{pt_low}_{pt_high}_eta{etaCutVal}.png")
    c.SaveAs(f"new_17March/comparison_plot_{suffix}_pt{pt_low}_{pt_high}_eta{etaCutVal}.pdf")
    c.SaveAs(f"new_17March/comparison_plot_{suffix}_pt{pt_low}_{pt_high}_eta{etaCutVal}.C")
    c.SaveAs(f"new_17March/comparison_plot_{suffix}_pt{pt_low}_{pt_high}_eta{etaCutVal}.root")

# Close input files
f_uncorr.Close()
f_corr.Close()
