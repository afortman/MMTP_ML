import ROOT
from ROOT import TMVA, TFile, TCanvas, TGraph
from array import array


############# SET DNN
#cutofflist = [i*0.001 for i in range(0,11)]+[j*0.001 for j in range(10,1001,2)]
def FindCurveDNN(siglist, bkglist):
    sig_eff = array( 'd' )
    bkg_rej = array( 'd' )
    for icut in range(0,10001,10):
        #for cutoff in cutofflist:
        cutoff = icut*0.0001
        sig = 0
        bkg = 0
        for output in siglist:
            if output > cutoff:
                sig += 1
        for output in bkglist:
            if output > cutoff:
                bkg += 1
        sig_eff.append( float(sig)/len(siglist) )
        bkg_rej.append( 1.0 - float(bkg)/len(bkglist) )
    return [sig_eff, bkg_rej]


def FindCurvekNN(siglist, bkglist):
    sig_eff = array( 'd' )
    bkg_rej = array( 'd' )
    for icut in range(0,2001):
        #for cutoff in cutofflist:
        cutoff = icut*0.001
        sig = 0
        bkg = 0
        for output in siglist:
            if output > cutoff:
                sig += 1
        for output in bkglist:
            if output > cutoff:
                bkg += 1
        sig_eff.append( float(sig)/len(siglist) )
        bkg_rej.append( 1.0 - float(bkg)/len(bkglist) )
    return [sig_eff, bkg_rej]


############## SET BDT
def FindCurveBDT(siglist, bkglist):
    sig_eff = array( 'd' )
    bkg_rej = array( 'd' )
    for icut in range(-1001,1001,10):
        #for cutoff in cutofflist:
        cutoff = icut*0.001
        sig = 0
        bkg = 0
        for output in siglist:
            if output > cutoff:
                sig += 1
        for output in bkglist:
            if output > cutoff:
                bkg += 1
        sig_eff.append( float(sig)/len(siglist) )
        bkg_rej.append( 1.0 - float(bkg)/len(bkglist) )
    return [sig_eff, bkg_rej]

##############  SET MLP
def FindCurveMLP(siglist, bkglist):
    sig_eff = array( 'd' )
    bkg_rej = array( 'd' )
    for icut in range(0,1001):
        #for cutoff in cutofflist:
        cutoff = icut*0.001
        sig = 0
        bkg = 0
        for output in siglist:
            if output > cutoff:
                sig += 1
        for output in bkglist:
            if output > cutoff:
                bkg += 1
        sig_eff.append( float(sig)/len(siglist) )
        bkg_rej.append( 1.0 - float(bkg)/len(bkglist) )
    return [sig_eff, bkg_rej]

TMVA.Tools.Instance()

reader = ROOT.TMVA.Reader()

fsig = ROOT.TFile("efftesting/hazel_both_smearf_10k_35ns_e90.root")
fbkg = ROOT.TFile("efftesting/hazel_bkg_smearf_10k_35ns_e90.root")

tr_sig   = fsig.Get("hazel")
tr_bkg   = fbkg.Get("hazel")

xlist = ["Hit_plane0","Hit_plane1","Hit_plane6","Hit_plane7"]
uvlist = ["Hit_plane2","Hit_plane3","Hit_plane4","Hit_plane5"]
planes = xlist + uvlist

branches = {}
for branch in tr_sig.GetListOfBranches():
    branchName = branch.GetName()
    if branchName in planes:
        branches[branchName] = array('f', [ 0.0 ])
        reader.AddVariable(branchName, branches[branchName])
        tr_sig.SetBranchAddress(branchName, branches[branchName])
        tr_bkg.SetBranchAddress(branchName, branches[branchName])

reader.BookMVA("DNN","dataset_e90/weights/TMVAClassification_DNN.weights.xml")
reader.BookMVA("BDT","dataset_e90/weights/TMVAClassification_BDT.weights.xml")
reader.BookMVA("MLP","dataset_e90/weights/TMVAClassification_MLP.weights.xml")
reader.BookMVA("kNN","dataset_e90/weights/TMVAClassification_kNN.weights.xml")

sigdnn = []
sigbdt = []
sigmlp = []
sigknn = []

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


bkgdnn = []
bkgbdt = []
bkgmlp = []
bkgknn = []

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

print("DNN Max/min")
print(max(sigdnn))
print(min(sigdnn))
print()
print(max(bkgdnn))
print(min(bkgdnn))
print()
print("BDT Max/min")
print(max(sigbdt))
print(min(sigbdt))
print()
print(max(bkgbdt))
print(min(bkgbdt))
print()
print("MLP Max/min")
print(max(sigmlp))
print(min(sigmlp))
print()
print(max(bkgmlp))
print(min(bkgmlp))
print()
print("kNN Max/min")
print(max(sigknn))
print(min(sigknn))
print()
print(max(bkgknn))
print(min(bkgknn))



dnnCurve = FindCurveDNN(sigdnn, bkgdnn)
bdtCurve = FindCurveBDT(sigbdt, bkgbdt)
mlpCurve = FindCurveMLP(sigmlp, bkgmlp)
knnCurve = FindCurvekNN(sigknn, bkgknn)

c1 = TCanvas( 'roc', 'roc', 200, 10, 700, 500 )
c1.cd()
c1.SetGrid()

gr0 = TGraph( len(dnnCurve[0]), dnnCurve[0], dnnCurve[1] )
gr1 = TGraph( len(bdtCurve[0]), bdtCurve[0], bdtCurve[1] )
gr2 = TGraph( len(mlpCurve[0]), mlpCurve[0], mlpCurve[1] )
gr3 = TGraph( len(knnCurve[0]), knnCurve[0], knnCurve[1] )

gr0.GetXaxis().SetTitle( 'Signal Efficiency' )
gr0.GetYaxis().SetTitle( '1 - Background Efficiency' )
gr0.SetTitle( "ROC Curve, 100k events, eff=90%" )


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

gr0.Draw( 'APL' )
gr1.Draw( 'PL' )
gr2.Draw( 'PL' )
gr3.Draw( 'PL' )

legend = ROOT.TLegend(0.1,0.3,0.48,0.5);
legend.AddEntry( gr0, 'DNN', "lp" );
legend.AddEntry( gr1, 'BDT', "lp");
legend.AddEntry( gr2, 'MLP', "lp");
legend.AddEntry( gr3, 'kNN', "lp");
legend.Draw()

c1.Update()

c1.SaveAs("dataset_e90/%s.pdf" % (c1.GetName()+"_1M_100k"))

