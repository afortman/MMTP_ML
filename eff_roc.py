import ROOT
from ROOT import TMVA, TFile, TCanvas, TGraph, TH1F
from array import array
import sys
from eff_roc_tools import FindPoint, FindCurveML, FindCurveDTheta, FindCurveChi2, MakeHists, MakeRoc

######## run like: python eff_roc.py -n 10k --hist --roc ###########

from optparse import OptionParser
parser = OptionParser()

parser.add_option('-n', type='string', action='store',
                  default= '10k',
                  dest='n',
                  help='number of events to evaluate over, 10k or 100k or 1M etc')

parser.add_option('--hist', action='store_true',
                  default=False,
                  dest='hist',
                  help='Do you want a ton of histograms to be made')

parser.add_option('--roc', action='store_true',
                  default=False,
                  dest='roc',
                  help='Do you want a ton of roc curves to be made')


(options, args) = parser.parse_args()
argv = []

effs = [90,91,92,93,94,95,96,97,98,99,100]

xlist = ["Hit_plane0","Hit_plane1","Hit_plane6","Hit_plane7"]
uvlist = ["Hit_plane2","Hit_plane3","Hit_plane4","Hit_plane5"]
planes = xlist + uvlist



bkgrej_dnn = array( 'd' )
bkgrej_bdt = array( 'd' )
bkgrej_mlp = array( 'd' )
bkgrej_knn = array( 'd' )
bkgrej_dtheta = array( 'd' )
bkgrej_chi2 = array( 'd' )
efficiencies = array( 'd' )

for eff in effs:
    
    TMVA.Tools.Instance()

    reader = ROOT.TMVA.Reader()

    fsig = ROOT.TFile("efftesting/hazel_both_smearf_"+str(options.n)+"_35ns_e"+str(eff)+".root")
    fbkg = ROOT.TFile("efftesting/hazel_bkg_smearf_"+str(options.n)+"_35ns_e"+str(eff)+".root")

    tr_sig   = fsig.Get("hazel")
    tr_bkg   = fbkg.Get("hazel")

    branches = {}
    for branch in tr_sig.GetListOfBranches():
        branchName = branch.GetName()
        if branchName in planes:
            branches[branchName] = array('f', [ 0.0 ])
            reader.AddVariable(branchName, branches[branchName])
            tr_sig.SetBranchAddress(branchName, branches[branchName])
            tr_bkg.SetBranchAddress(branchName, branches[branchName])

    reader.BookMVA("DNN","dataset_e"+str(eff)+"/weights/TMVAClassification_DNN.weights.xml")
    reader.BookMVA("BDT","dataset_e"+str(eff)+"/weights/TMVAClassification_BDT.weights.xml")
    reader.BookMVA("MLP","dataset_e"+str(eff)+"/weights/TMVAClassification_MLP.weights.xml")
    reader.BookMVA("kNN","dataset_e"+str(eff)+"/weights/TMVAClassification_kNN.weights.xml")

    sigdnn = []
    sigbdt = []
    sigmlp = []
    sigknn = []
    sigdtheta = []
    sigchi2 = []

    for ent1 in range(tr_sig.GetEntries()):
        _ = tr_sig.GetEntry(ent1)
        branches["Hit_plane0"][0] = tr_sig.Hit_plane0
        branches["Hit_plane1"][0] = tr_sig.Hit_plane1
        branches["Hit_plane2"][0] = tr_sig.Hit_plane2
        branches["Hit_plane3"][0] = tr_sig.Hit_plane3
        branches["Hit_plane4"][0] = tr_sig.Hit_plane4
        branches["Hit_plane5"][0] = tr_sig.Hit_plane5
        branches["Hit_plane6"][0] = tr_sig.Hit_plane6
        branches["Hit_plane7"][0] = tr_sig.Hit_plane7
        
        sigdnn.append( reader.EvaluateMVA("DNN") )
        sigbdt.append( reader.EvaluateMVA("BDT") )
        sigmlp.append( reader.EvaluateMVA("MLP") )
        sigknn.append( reader.EvaluateMVA("kNN") )
        sigdtheta.append( tr_sig.dtheta )
        sigchi2.append( tr_sig.chi2 )


    bkgdnn = []
    bkgbdt = []
    bkgmlp = []
    bkgknn = []
    bkgdtheta = []
    bkgchi2 = []

    for ent2 in range(tr_bkg.GetEntries()):
        _ = tr_bkg.GetEntry(ent2)
        branches["Hit_plane0"][0] = tr_bkg.Hit_plane0
        branches["Hit_plane1"][0] = tr_bkg.Hit_plane1
        branches["Hit_plane2"][0] = tr_bkg.Hit_plane2
        branches["Hit_plane3"][0] = tr_bkg.Hit_plane3
        branches["Hit_plane4"][0] = tr_bkg.Hit_plane4
        branches["Hit_plane5"][0] = tr_bkg.Hit_plane5
        branches["Hit_plane6"][0] = tr_bkg.Hit_plane6
        branches["Hit_plane7"][0] = tr_bkg.Hit_plane7
        
        bkgdnn.append( reader.EvaluateMVA("DNN") )
        bkgbdt.append( reader.EvaluateMVA("BDT") )
        bkgmlp.append( reader.EvaluateMVA("MLP") )
        bkgknn.append( reader.EvaluateMVA("kNN") )
        bkgdtheta.append( tr_bkg.dtheta )
        bkgchi2.append( tr_bkg.chi2 )

    dnnCurve = FindCurveML(sigdnn, bkgdnn, 0, 10001, 1, 0.0001)
    bdtCurve = FindCurveML(sigbdt, bkgbdt, -1001, 1001, 10, 0.001)
    mlpCurve = FindCurveML(sigmlp, bkgmlp, 0, 1001, 1, 0.001)
    knnCurve = FindCurveML(sigknn, bkgknn, 0, 10001, 1, 0.0001)
    dthetaCurve = FindCurveDTheta(sigdtheta, bkgdtheta)
    chi2Curve = FindCurveChi2(sigchi2, bkgchi2)
        
    if options.hist:

        (hsig_dnn, hbkg_dnn, canv_dnn ,legdnn) = MakeHists(sigdnn, bkgdnn,0.,1.,"dnn_"+str(options.n)+"_e"+str(eff))
        legdnn.Draw()
        canv_dnn.SaveAs("hists/%s.pdf" % (canv_dnn.GetName()))
        
        (hsig_bdt, hbkg_bdt, canv_bdt, legbdt) = MakeHists(sigbdt, bkgbdt,-1.,1.,"bdt_"+str(options.n)+"_e"+str(eff))
        legbdt.Draw()
        canv_bdt.SaveAs("hists/%s.pdf" % (canv_bdt.GetName()))
        
        (hsig_mlp, hbkg_mlp, canv_mlp, legmlp) = MakeHists(sigmlp, bkgmlp,0.,1.,"mlp_"+str(options.n)+"_e"+str(eff))
        legmlp.Draw()
        canv_mlp.SaveAs("hists/%s.pdf" % (canv_mlp.GetName()))
        
        (hsig_knn, hbkg_knn, canv_knn, legknn) = MakeHists(sigknn, bkgknn,0.,1.,"knn_"+str(options.n)+"_e"+str(eff))
        legknn.Draw()
        canv_knn.SaveAs("hists/%s.pdf" % (canv_knn.GetName()))
        
        (hsig_dtheta, hbkg_dtheta, canv_dtheta, legdtheta) = MakeHists(sigdtheta, bkgdtheta,-0.05,0.05,"dtheta_"+str(options.n)+"_e"+str(eff))
        legdtheta.Draw()
        canv_dtheta.SaveAs("hists/%s.pdf" % (canv_dtheta.GetName()))
        
        (hsig_chi2, hbkg_chi2, canv_chi2, legchi2) = MakeHists(sigchi2, bkgchi2,0.,5.,"chi2_"+str(options.n)+"_e"+str(eff))
        legchi2.Draw()
        canv_chi2.SaveAs("hists/%s.pdf" % (canv_chi2.GetName()))

    if options.roc:

        (roc_dnn, roc_canv_dnn) = MakeRoc(dnnCurve[0], dnnCurve[1],"dnn_"+str(options.n)+"_e"+str(eff))
        roc_canv_dnn.SaveAs("hists/%s.pdf" % (roc_canv_dnn.GetName()))
        (roc_bdt, roc_canv_bdt) = MakeRoc(bdtCurve[0], bdtCurve[1],"bdt_"+str(options.n)+"_e"+str(eff))
        roc_canv_bdt.SaveAs("hists/%s.pdf" % (roc_canv_bdt.GetName()))
        (roc_mlp, roc_canv_mlp) = MakeRoc(mlpCurve[0], mlpCurve[1] ,"mlp_"+str(options.n)+"_e"+str(eff))
        roc_canv_mlp.SaveAs("hists/%s.pdf" % (roc_canv_mlp.GetName()))
        (roc_knn, roc_canv_knn) = MakeRoc(knnCurve[0], knnCurve[1],"knn_"+str(options.n)+"_e"+str(eff))
        roc_canv_knn.SaveAs("hists/%s.pdf" % (roc_canv_knn.GetName()))
        (roc_dtheta, roc_canv_dtheta) = MakeRoc(dthetaCurve[0], dthetaCurve[1],"dtheta_"+str(options.n)+"_e"+str(eff))
        roc_canv_dtheta.SaveAs("hists/%s.pdf" % (roc_canv_dtheta.GetName()))
        (roc_chi2, roc_canv_chi2) = MakeRoc(chi2Curve[0], chi2Curve[1],"chi2_"+str(options.n)+"_e"+str(eff))
        roc_canv_chi2.SaveAs("hists/%s.pdf" % (roc_canv_chi2.GetName()))


    dnnPoint = FindPoint( dnnCurve[0], dnnCurve[1] )
    bdtPoint = FindPoint( bdtCurve[0], bdtCurve[1] )
    mlpPoint = FindPoint( mlpCurve[0], mlpCurve[1] )
    knnPoint = FindPoint( knnCurve[0], knnCurve[1] )
    dthetaPoint = FindPoint( list(reversed(dthetaCurve[0])), list(reversed(dthetaCurve[1])) )
    chi2Point = FindPoint( list(reversed(chi2Curve[0])), list(reversed(chi2Curve[1])) )

    #print("Efficiency = "+str(eff)+"%" )
    #print( dnnPoint[0], dnnPoint[1] )
    #print( bdtPoint[0], bdtPoint[1] )
    #print( mlpPoint[0], mlpPoint[1] )
    #print( knnPoint[0], knnPoint[1] )
    #print( dthetaPoint[0], dthetaPoint[1] )
    #print( chi2Point[0], chi2Point[1] )

############### PLOTTING BKG EFFICIENCY INSTEAD OF BKG REJECTION
    bkgrej_dnn.append( 1.0 - dnnPoint[1] )
    bkgrej_bdt.append( 1.0 - bdtPoint[1] )
    bkgrej_mlp.append( 1.0 - mlpPoint[1] )
    bkgrej_knn.append( 1.0 - knnPoint[1] )
    bkgrej_dtheta.append( 1.0 - dthetaPoint[1] )
    bkgrej_chi2.append( 1.0 - chi2Point[1] )
    efficiencies.append( eff*0.01 )


#print(efficiencies)
#print(bkgrej_dtheta)
#print(bkgrej_chi2)


c1 = TCanvas( 'detector_efficiency', 'detector_efficiency', 200, 10, 700, 500 )
c1.cd()
c1.SetGrid()

gr0 = TGraph( len(efficiencies), efficiencies, bkgrej_dnn )
gr1 = TGraph( len(efficiencies), efficiencies, bkgrej_bdt )
gr2 = TGraph( len(efficiencies), efficiencies, bkgrej_mlp )
gr3 = TGraph( len(efficiencies), efficiencies, bkgrej_knn )
gr4 = TGraph( len(efficiencies), efficiencies, bkgrej_dtheta )
gr5 = TGraph( len(efficiencies), efficiencies, bkgrej_chi2 )


gr0.GetXaxis().SetTitle( 'Detector Efficiency' )
gr0.GetYaxis().SetTitle( 'Background Efficiency' )
gr0.GetYaxis().SetRangeUser(0.0,1.0)
gr0.SetTitle( "Background Efficiency at 95% Signal Efficiency" )


gr0.SetLineColor( 46 )
gr0.SetLineWidth( 1 )
gr0.SetMarkerStyle( 4 )
gr0.SetMarkerColor( 2 )

gr1.SetLineColor( 30 )
gr1.SetLineWidth( 1 )
gr1.SetMarkerStyle( 21 )
gr1.SetMarkerColor( 3 )

gr2.SetLineColor( 38 )
gr2.SetLineWidth( 1 )
gr2.SetMarkerStyle( 29 )
gr2.SetMarkerColor( 4 )

gr3.SetLineColor( 12 )
gr3.SetLineWidth( 1 )
gr3.SetMarkerStyle( 31 )
gr3.SetMarkerColor( 1 )

gr4.SetLineColor( 6 )
gr4.SetLineWidth( 1 )
gr4.SetMarkerStyle( 49 )
gr4.SetMarkerColor( 6 )

gr5.SetLineColor( 7 )
gr5.SetLineWidth( 1 )
gr5.SetMarkerStyle( 39 )
gr5.SetMarkerColor( 7 )

gr0.Draw( 'APL' )
gr1.Draw( 'PL' )
gr2.Draw( 'PL' )
gr3.Draw( 'PL' )
gr4.Draw( 'PL' )
gr5.Draw( 'PL' )

legend = ROOT.TLegend(0.1,0.75,0.45,0.9);
legend.SetNColumns(2)
legend.AddEntry( gr0, 'DNN', "lp" );
legend.AddEntry( gr3, 'kNN', "lp");
legend.AddEntry( gr1, 'BDT', "lp");
legend.AddEntry( gr4, 'Delta Theta', "lp");
legend.AddEntry( gr2, 'MLP', "lp");
legend.AddEntry( gr5, 'Chi Squared', "lp");
legend.Draw()

c1.Update()

c1.SaveAs("%s.pdf" % (c1.GetName()+"_1M_"+str(options.n)))

