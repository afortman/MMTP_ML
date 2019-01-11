import ROOT
from ROOT import TCanvas, TGraph, TFile
from ROOT import gROOT
from array import array

## https://root.cern.ch/doc/v610/graph_8py.html
##https://root.cern.ch/doc/master/classTGraphPainter.html


def FindPoints(fsig, fbkg):
    
    ####### get trees ##
    tr_sig   = fsig.Get("hazel")
    tr_bkg   = fbkg.Get("hazel")
    
    sig_dtheta = []
    bkg_dtheta = []
    
    ########### get lists of delta thetas from each tree ##
    for ent1 in range(tr_sig.GetEntries()):
        _ = tr_sig.GetEntry(ent1)
        sig_dtheta.append(tr_sig.dtheta)
    
    for ent2 in range(tr_bkg.GetEntries()):
        _ = tr_bkg.GetEntry(ent2)
        bkg_dtheta.append(tr_bkg.dtheta)

    ########## scan over different cutoff angles and prepare arrays for plotting ##
    sig_eff = array( 'd' )
    bkg_rej = array( 'd' )
    for iangle in range(0,1000):
        cutoff = iangle*0.0001
        sig = 0
        bkg = 0
        for theta_sig in sig_dtheta:
            if abs(theta_sig) < cutoff:
                sig += 1
        for theta_bkg in bkg_dtheta:
            if abs(theta_bkg) < cutoff:
                bkg += 1
        sig_eff.append( float(sig)/len(sig_dtheta) )
        bkg_rej.append( 1.0 - float(bkg)/len(bkg_dtheta) )
    return [sig_eff, bkg_rej]


def main():
    c1 = TCanvas( 'roc', 'roc', 200, 10, 700, 500 )
    c1.cd()
    
    ####### No Smearing ##############
    points_0 = FindPoints(TFile("hazel_sig_smear0.root"), TFile("hazel_bkg_smear0.root"))
    signal_eff_0 = points_0[0]
    background_rej_0 = points_0[1]
    n0 = len(signal_eff_0)

    ####### 1 Strip Smearing ##############
    points_1 = FindPoints(TFile("hazel_sig_smear1.root"), TFile("hazel_bkg_smear1.root"))
    signal_eff_1 = points_1[0]
    background_rej_1 = points_1[1]
    n1 = len(signal_eff_1)
    
    ####### 2 Strip Smearing ##############
    points_2 = FindPoints(TFile("hazel_sig_smear2.root"), TFile("hazel_bkg_smear2.root"))
    signal_eff_2 = points_2[0]
    background_rej_2 = points_2[1]
    n2 = len(signal_eff_2)

    c1.SetGrid()

    gr0 = TGraph( n0, signal_eff_0, background_rej_0 )
    gr1 = TGraph( n1, signal_eff_1, background_rej_1 )
    gr2 = TGraph( n2, signal_eff_2, background_rej_2 )
    
    gr0.GetXaxis().SetTitle( 'Signal Efficiency' )
    gr0.GetYaxis().SetTitle( '1 - Background Efficiency' )
    gr0.SetTitle( 'ROC Curve' )
    
    gr0.SetLineColor( 46 )
    gr0.SetLineWidth( 3 )
    gr0.SetMarkerStyle( 4 )
    gr0.SetMarkerColor( 2 )
    
    gr1.SetLineColor( 30 )
    gr1.SetLineWidth( 3 )
    gr1.SetMarkerStyle( 21 )
    gr1.SetMarkerColor( 3 )
    
    gr2.SetLineColor( 38 )
    gr2.SetLineWidth( 3 )
    gr2.SetMarkerStyle( 29 )
    gr2.SetMarkerColor( 4 )

    gr0.Draw( 'APL' )
    gr1.Draw( 'PL' )
    gr2.Draw( 'PL' )
    
    legend = ROOT.TLegend(0.1,0.3,0.48,0.5);
    legend.AddEntry( gr0, '10,000 events, 0 strip smearing', "lp" );
    legend.AddEntry( gr1, '10,000 events, 1 strip smearing', "lp");
    legend.AddEntry( gr2, '10,000 events, 2 strip smearing', "lp");
    legend.Draw()
    

    c1.Update()
    c1.SaveAs("%s.pdf" % (c1.GetName()))

if __name__ == "__main__":
    main()
