import ROOT
from ROOT import TCanvas, TGraph, TFile, TH1F
from ROOT import gROOT
from array import array

## https://root.cern.ch/doc/v610/graph_8py.html
##https://root.cern.ch/doc/master/classTGraphPainter.html


chisquare = False
hist = True


def FindCurveDTheta(fsig, fbkg):
    
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

    return [sig_eff, bkg_rej, sig_dtheta, bkg_dtheta]


def FindCurveChi2(fsig, fbkg):
    
    ####### get trees ##
    tr_sig   = fsig.Get("hazel")
    tr_bkg   = fbkg.Get("hazel")
    
    sig_chi2 = []
    bkg_chi2 = []
    
    ########### get lists of chi2/NDF from each tree ##
    for ent1 in range(tr_sig.GetEntries()):
        _ = tr_sig.GetEntry(ent1)
        sig_chi2.append(tr_sig.chi2)
    
    for ent2 in range(tr_bkg.GetEntries()):
        _ = tr_bkg.GetEntry(ent2)
        bkg_chi2.append(tr_bkg.chi2)
    
    ########## scan over different chi2/NDF and prepare arrays for plotting ##
    sig_eff = array( 'd' )
    bkg_rej = array( 'd' )
    chiscan = [k*0.0001 for k in range(0,11)]+[i*0.001 for i in range(1,1001)]+[j*0.01 for j in range(101,1200)]
    for cutoff in chiscan:
        #cutoff = ichi2*0.001
        sig = 0
        bkg = 0
        for chi2_sig in sig_chi2:
            if abs(chi2_sig) < cutoff:
                sig += 1
        for chi2_bkg in bkg_chi2:
            if abs(chi2_bkg) < cutoff:
                bkg += 1
        sig_eff.append( float(sig)/len(sig_chi2) )
        bkg_rej.append( 1.0 - float(bkg)/len(bkg_chi2) )

    return [sig_eff, bkg_rej, sig_chi2, bkg_chi2]


def main():
    
    c1 = TCanvas( 'roc', 'roc', 200, 10, 700, 500 )
    c1.cd()
    
    if chisquare:
        
        points_0 = FindCurveChi2(TFile("hazel_sig_smear0.root"), TFile("hazel_bkg_smear0.root"))
        points_1 = FindCurveChi2(TFile("hazel_sig_smear1.root"), TFile("hazel_bkg_smear1.root"))
        points_2 = FindCurveChi2(TFile("hazel_sig_smear2.root"), TFile("hazel_bkg_smear2.root"))
        points_f = FindCurveChi2(TFile("hazel_sig_smearf.root"), TFile("hazel_bkg_smearf.root"))
    
    else:
    
        ####### No Smearing ##############
        points_0 = FindCurveDTheta(TFile("hazel_sig_smear0.root"), TFile("hazel_bkg_smear0.root"))
        ####### 1 Strip Smearing ##############
        points_1 = FindCurveDTheta(TFile("hazel_sig_smear1.root"), TFile("hazel_bkg_smear1.root"))
        ####### 2 Strip Smearing ##############
        points_2 = FindCurveDTheta(TFile("hazel_sig_smear2.root"), TFile("hazel_bkg_smear2.root"))
        points_f = FindCurveDTheta(TFile("hazel_sig_smearf.root"), TFile("hazel_bkg_smearf.root"))
        
    signal_eff_0 = points_0[0]
    background_rej_0 = points_0[1]
    n0 = len(signal_eff_0)
        
    signal_eff_1 = points_1[0]
    background_rej_1 = points_1[1]
    n1 = len(signal_eff_1)
    
    signal_eff_2 = points_2[0]
    background_rej_2 = points_2[1]
    n2 = len(signal_eff_2)

    signal_eff_f = points_f[0]
    background_rej_f = points_f[1]
    nf = len(signal_eff_f)

    if hist:

        h_sig_0 = TH1F("signal_dtheta","signal dtheta",1000,-0.05,0.05)
        h_bkg_0 = TH1F("background_0","background dtheta",1000,-0.05,0.05)
        for i in points_0[2]:
            h_sig_0.Fill(i)
        for i in points_0[3]:
            h_bkg_0.Fill(i)

        h_sig_1 = TH1F("signal_1","signal_1",1000,-0.05,0.05)
        h_bkg_1 = TH1F("background_1","background_1",1000,-0.05,0.05)
        for i in points_1[2]:
            h_sig_1.Fill(i)
        for i in points_1[3]:
            h_bkg_1.Fill(i)

        h_sig_2 = TH1F("signal_2","signal_2",1000,-0.05,0.05)
        h_bkg_2 = TH1F("background_2","background_2",10000,-0.05,0.05)
        for i in points_2[2]:
            h_sig_2.Fill(i)
        for i in points_2[3]:
            h_bkg_2.Fill(i)

        h_sig_f = TH1F("signal_f","signal_f",1000,-0.05,0.05)
        h_bkg_f = TH1F("background_f","background_f",1000,-0.05,0.05)
        for i in points_f[2]:
            h_sig_f.Fill(i)
        for i in points_f[3]:
            h_bkg_f.Fill(i)

                
        



    c1.SetGrid()

    gr0 = TGraph( n0, signal_eff_0, background_rej_0 )
    gr1 = TGraph( n1, signal_eff_1, background_rej_1 )
    gr2 = TGraph( n2, signal_eff_2, background_rej_2 )
    grf = TGraph( nf, signal_eff_f, background_rej_f )
    
    gr0.GetXaxis().SetTitle( 'Signal Efficiency' )
    gr0.GetYaxis().SetTitle( '1 - Background Efficiency' )
    if chisquare:
        gr0.SetTitle( 'ROC Curve for Chi2/NDF' )
    else:
        gr0.SetTitle( 'ROC Curve for Delta Theta' )
    
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

    grf.SetLineColor( 12 )
    grf.SetLineWidth( 3 )
    grf.SetMarkerStyle( 31 )
    grf.SetMarkerColor( 1 )

    gr0.Draw( 'APL' )
    gr1.Draw( 'PL' )
    gr2.Draw( 'PL' )
    grf.Draw( 'PL' )
    
    legend = ROOT.TLegend(0.1,0.3,0.48,0.5);
    legend.AddEntry( gr0, '1M events, 0 strip smearing', "lp" );
    legend.AddEntry( gr1, '1M events, 1 strip smearing', "lp");
    legend.AddEntry( gr2, '1M events, 2 strip smearing', "lp");
    legend.AddEntry( grf, '1M events, function smearing', "lp");
    legend.Draw()
    

    c1.Update()
    if chisquare:
        c1.SaveAs("%s.pdf" % (c1.GetName()+"_chi2"))
    else:
        c1.SaveAs("%s.pdf" % (c1.GetName()+"_dtheta"))


    if hist:

        c2 = TCanvas( 'signal_dtheta', 'signal_dtheta' )
        c2.cd()
        h_sig_0.Draw("hist")
        h_sig_1.SetLineColor(2)
        h_sig_1.Draw("hist same")
        h_sig_2.SetLineColor(3)
        h_sig_2.Draw("hist same")
        h_sig_f.SetLineColor(1)
        h_sig_f.Draw("hist same")
        legend2 = ROOT.TLegend(0.1,0.7,0.48,0.9);
        legend2.AddEntry( h_sig_0, '0 strip smearing', "l" );
        legend2.AddEntry( h_sig_1, '1 strip smearing', "l");
        legend2.AddEntry( h_sig_2, '2 strip smearing', "l");
        legend2.AddEntry( h_sig_f, 'function smearing', "l");
        legend2.Draw()
        c2.Update()
        c2.SaveAs("%s.pdf" % (c2.GetName()))

        c3 = TCanvas( 'background_dtheta', 'background_dtheta' )
        c3.cd()
        h_bkg_0.Draw("hist")
        h_bkg_1.SetLineColor(2)
        h_bkg_1.Draw("hist same")
        h_bkg_2.SetLineColor(3)
        h_bkg_2.Draw("hist same")
        h_bkg_f.SetLineColor(1)
        h_bkg_f.Draw("hist same")
        legend3 = ROOT.TLegend(0.1,0.7,0.48,0.9);
        legend3.AddEntry( h_bkg_0, '0 strip smearing', "l");
        legend3.AddEntry( h_bkg_1, '1 strip smearing', "l");
        legend3.AddEntry( h_bkg_2, '2 strip smearing', "l");
        legend3.AddEntry( h_bkg_f, 'function smearing', "l");
        legend3.Draw()
        c3.Update()
        c3.SaveAs("%s.pdf" % (c3.GetName()))

if __name__ == "__main__":
    main()
