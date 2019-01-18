import ROOT
from ROOT import TMVA, TFile, TCanvas, TGraph
from array import array


############# SET DNN
#cutofflist = [i*0.001 for i in range(0,11)]+[j*0.001 for j in range(10,1001,2)]
def FindCurveDNN(siglist, bkglist):
    sig_eff = array( 'd' )
    bkg_rej = array( 'd' )
    for icut in range(0,10001):
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


############## SET BDT
def FindCurveBDT(siglist, bkglist):
    sig_eff = array( 'd' )
    bkg_rej = array( 'd' )
    for icut in range(-1001,1001):
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

fsig = ROOT.TFile("smallfiles/hazel_sig_smearf_10k.root")
fbkg = ROOT.TFile("smallfiles/hazel_bkg_smearf_10k.root")

tr_sig   = fsig.Get("hazel")
tr_bkg   = fbkg.Get("hazel")

branches = {}
for branch in tr_sig.GetListOfBranches():
    branchName = branch.GetName()
    if "Hit" in branchName:
        branches[branchName] = array('f', [ 0.0 ])
        reader.AddVariable(branchName, branches[branchName])
        tr_sig.SetBranchAddress(branchName, branches[branchName])
        tr_bkg.SetBranchAddress(branchName, branches[branchName])

reader.BookMVA("DNN_1M_smearf","dataset/weights/TMVAClassification_DNN_1M_smearf.weights.xml")
reader.BookMVA("BDT_1M_smearf","dataset/weights/TMVAClassification_BDT_1M_smearf.weights.xml")
reader.BookMVA("MLP_1M_smearf","dataset/weights/TMVAClassification_MLP_1M_smearf.weights.xml")

sigdnn = []
sigbdt = []
sigmlp = []

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
    branches["Hit_n"][0] = tr_sig.Hit_n
    
    sigdnn.append( reader.EvaluateMVA("DNN_1M_smearf") )
    sigbdt.append( reader.EvaluateMVA("BDT_1M_smearf") )
    sigmlp.append( reader.EvaluateMVA("MLP_1M_smearf") )


bkgdnn = []
bkgbdt = []
bkgmlp = []

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
    branches["Hit_n"][0] = tr_bkg.Hit_n
    
    bkgdnn.append( reader.EvaluateMVA("DNN_1M_smearf") )
    bkgbdt.append( reader.EvaluateMVA("BDT_1M_smearf") )
    bkgmlp.append( reader.EvaluateMVA("MLP_1M_smearf") )

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



dnnCurve = FindCurveDNN(sigdnn, bkgdnn)
bdtCurve = FindCurveBDT(sigbdt, bkgbdt)
mlpCurve = FindCurveMLP(sigmlp, bkgmlp)

c1 = TCanvas( 'roc', 'roc', 200, 10, 700, 500 )
c1.cd()
c1.SetGrid()

gr0 = TGraph( len(dnnCurve[0]), dnnCurve[0], dnnCurve[1] )
gr1 = TGraph( len(bdtCurve[0]), bdtCurve[0], bdtCurve[1] )
gr2 = TGraph( len(mlpCurve[0]), mlpCurve[0], mlpCurve[1] )

gr0.GetXaxis().SetTitle( 'Signal Efficiency' )
gr0.GetYaxis().SetTitle( '1 - Background Efficiency' )
gr0.SetTitle( 'ROC Curve for Machine Learning, 10k w/ function smear' )


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
legend.AddEntry( gr0, 'DNN', "lp" );
legend.AddEntry( gr1, 'BDT', "lp");
legend.AddEntry( gr2, 'MLP', "lp");
legend.Draw()

c1.Update()

c1.SaveAs("%s.pdf" % (c1.GetName()+"_1Msf_smearf"))


'''
    c2 = TCanvas( 'bdt_1Ms1_s2', 'bdt_1Ms1_s2', 200, 10, 700, 500 )
    c2.cd()
    h_sig = ROOT.TH1F("signalbdt","signalbdt",10000,-10.0,1.0)
    h_bkg = ROOT.TH1F("backgroundbdt","backgroundbdt",10000,-10.0,1.0)
    for i in sigbdt:
    h_sig.Fill(i)
    for i in bkgbdt:
    h_bkg.Fill(i)
    h_sig.Draw("hist")
    h_bkg.SetLineColor(2)
    h_bkg.Draw("hist same")
    legend2 = ROOT.TLegend(0.1,0.7,0.48,0.9);
    legend2.AddEntry( h_sig, 'signal', "l" );
    legend2.AddEntry( h_bkg, 'background', "l");
    legend2.Draw()
    c2.Update()
    c2.SaveAs("%s.pdf" % (c2.GetName()))
    '''


