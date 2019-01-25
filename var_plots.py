import ROOT
from ROOT import TMVA, TFile, TCanvas, TH2F
import sys
from array import array

######## run like: python var_plots.py -n 10k -e 100 ##########



######## This is so ugly and long. I'm sorry ###########

from optparse import OptionParser
parser = OptionParser()

parser.add_option('-n', type='string', action='store',
                  default= '10k',
                  dest='n',
                  help='number of events to evaluate over, 10k or 100k or 1M etc')

parser.add_option('-e', type='string', action='store',
                  default= '100',
                  dest='eff',
                  help='hit efficiency')

#parser.add_option('--ML', type='string', action='store',
#                  default= 'DNN',
#                  dest='ML',
#                  help='Which ML method? DNN, BDT, MLP, or kNN')

(options, args) = parser.parse_args()
argv = []


#ML = str(options.ML)
eff = options.eff


TMVA.Tools.Instance()
reader = ROOT.TMVA.Reader()

fsig = ROOT.TFile("efftesting/hazel_both_smearf_"+str(options.n)+"_35ns_e"+str(eff)+".root")
fbkg = ROOT.TFile("efftesting/hazel_bkg_smearf_"+str(options.n)+"_35ns_e"+str(eff)+".root")

xlist = ["Hit_plane0","Hit_plane1","Hit_plane6","Hit_plane7"]
uvlist = ["Hit_plane2","Hit_plane3","Hit_plane4","Hit_plane5"]
planes = xlist + uvlist


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



########### START LOOP OVER ML METHODS #########


MLlist = ["DNN","BDT","MLP","kNN"]
for ML in MLlist:
    
    reader.BookMVA( ML,"dataset_e"+str(eff)+"/weights/TMVAClassification_"+ML+".weights.xml")

    ### Get ML scores and hit planes info

    sigML = []
    sigX0 = []
    sigX1 = []
    sigX2 = []
    sigX3 = []
    sigU1 = []
    sigU2 = []
    sigV1 = []
    sigV2 = []

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
        
        sigX0.append( branches["Hit_plane0"][0] )
        sigX1.append( branches["Hit_plane1"][0] )
        sigX2.append( branches["Hit_plane6"][0] )
        sigX3.append( branches["Hit_plane7"][0] )
        sigU1.append( branches["Hit_plane2"][0] )
        sigU2.append( branches["Hit_plane4"][0] )
        sigV1.append( branches["Hit_plane3"][0] )
        sigV2.append( branches["Hit_plane5"][0] )
        
        sigML.append( reader.EvaluateMVA( ML ) )


    bkgML = []
    bkgX0 = []
    bkgX1 = []
    bkgX2 = []
    bkgX3 = []
    bkgU1 = []
    bkgU2 = []
    bkgV1 = []
    bkgV2 = []


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
        
        bkgX0.append( branches["Hit_plane0"][0] )
        bkgX1.append( branches["Hit_plane1"][0] )
        bkgX2.append( branches["Hit_plane6"][0] )
        bkgX3.append( branches["Hit_plane7"][0] )
        bkgU1.append( branches["Hit_plane2"][0] )
        bkgU2.append( branches["Hit_plane4"][0] )
        bkgV1.append( branches["Hit_plane3"][0] )
        bkgV2.append( branches["Hit_plane5"][0] )

        bkgML.append( reader.EvaluateMVA( ML ) )

    ################# Make 2d histograms ###############
    # Numbered according to this list:
    #
    #[ Comment: I think these next 8 variables will be uncorrelated with the ML score. But we need to check! ]
    #01. X0
    #02. X1
    #03. X2
    #04. X3
    #05. U1
    #06. U2
    #07. V1
    #08. V2
    #
    #[ Comment: I think these will be interesting. ]
    #09. X0 - X1
    #10. X2 - X3
    #11. X0 - (X1 + X2 + X3)/3
    #12. X1 - (X0 + X2 + X3)/3
    #13. X2 - (X0 + X1 + X3)/3
    #14. X3 - (X0 + X1 + X2)/3
    #15. (X0 + X1)/2 - (X2 + X3)/2
    #16. (X0 + X1 + X2 + X3)/4
    #17. U1 - U2
    #18. V1 - V2
    #19. (U1 + U2)/2 - (V1 + V2)/2
    #20. (U1 + U2 + V1 + V2)/4
    #21. (X0 + X1 + X2 + X3)/4  - (U1 + U2 + V1 + V2)/4
    #
    #[ Comment: The hammer. ]
    #22. N(hits)
    #23. N(X hits)
    #24. N(UV hits)
    #25. N(U hits)
    #26. N(V hits)

    sig_name_dict = {"sig01":"Signal X0", "sig02":"Signal X1", "sig03":"Signal X2", "sig04":"Signal X3", "sig05":"Signal U1", "sig06":"Signal U2", "sig07":"Signal V1", "sig08":"Signal V2", "sig09":"Signal X0 - X1", "sig10":"Signal X2 - X3", "sig11":"Signal X0 - (X1 + X2 + X3)/3", "sig12":"Signal X1 - (X0 + X2 + X3)/3", "sig13":"Signal X2 - (X0 + X1 + X3)/3", "sig14":"Signal X3 - (X0 + X1 + X2)/3", "sig15":"Signal (X0 + X1)/2 - (X2 + X3)/2", "sig16":"Signal (X0 + X1 + X2 + X3)/4", "sig17":"Signal U1 - U2", "sig18":"Signal V1 - V2", "sig19":"Signal (U1 + U2)/2 - (V1 + V2)/2", "sig20":"Signal (U1 + U2 + V1 + V2)/4", "sig21":"Signal (X0 + X1 + X2 + X3)/4  - (U1 + U2 + V1 + V2)/4", "sig22":"Signal N(hits)", "sig23":"Signal N(X hits)", "sig24":"Signal N(UV hits)", "sig25":"Signal N(U hits)", "sig26":"Signal N(V hits)"}
    bkg_name_dict = {"bkg01":"Background X0", "bkg02":"Background X1", "bkg03":"Background X2", "bkg04":"Background X3", "bkg05":"Background U1", "bkg06":"Background U2", "bkg07":"Background V1", "bkg08":"Background V2", "bkg09":"Background X0 - X1", "bkg10":"Background X2 - X3", "bkg11":"Background X0 - (X1 + X2 + X3)/3", "bkg12":"Background X1 - (X0 + X2 + X3)/3", "bkg13":"Background X2 - (X0 + X1 + X3)/3", "bkg14":"Background X3 - (X0 + X1 + X2)/3", "bkg15":"Background (X0 + X1)/2 - (X2 + X3)/2", "bkg16":"Background (X0 + X1 + X2 + X3)/4", "bkg17":"Background U1 - U2", "bkg18":"Background V1 - V2", "bkg19":"Background (U1 + U2)/2 - (V1 + V2)/2", "bkg20":"Background (U1 + U2 + V1 + V2)/4", "bkg21":"Background (X0 + X1 + X2 + X3)/4  - (U1 + U2 + V1 + V2)/4", "bkg22":"Background N(hits)", "bkg23":"Background N(X hits)", "bkg24":"Background N(UV hits)", "bkg25":"Background N(U hits)", "bkg26":"Background N(V hits)"}



    ######## making and labelling histograms


    sighists = {}
    bkghists = {}
    sigcanvs = {}
    bkgcanvs = {}

    minML = 0.0
    if ML == "BDT":
        minML = -1.0

    canvstring = "_"+ML+"_"+str(options.n)+"_e"+str(eff)

    for name in sig_name_dict:
        hsig = TH2F( name, sig_name_dict[name] +" vs "+ML+" score", 100, minML, 1.0, 13, -1.0, 12.0)
        hsig.GetXaxis().SetTitle( ML+" Score")
        hsig.GetYaxis().SetTitle( sig_name_dict[name] )
        sighists[name] = hsig
        c_sig = TCanvas( name+canvstring, name+canvstring )
        sigcanvs[name] = c_sig

    for name in bkg_name_dict:
        hbkg = TH2F( name, bkg_name_dict[name] +" vs "+ML+" score", 100, minML, 1.0, 13, -1.0, 12.0)
        hbkg.GetXaxis().SetTitle( ML+" Score")
        hbkg.GetYaxis().SetTitle( bkg_name_dict[name] )
        bkghists[name] = hbkg
        c_bkg = TCanvas( name+canvstring, name+canvstring )
        bkgcanvs[name] = c_bkg


    ######### filling histograms

    for iscore, score in enumerate(sigML):
        X0 = sigX0[iscore]
        X1 = sigX1[iscore]
        X2 = sigX2[iscore]
        X3 = sigX3[iscore]
        U1 = sigU1[iscore]
        U2 = sigU2[iscore]
        V1 = sigV1[iscore]
        V2 = sigV2[iscore]
        
        sighists["sig01"].Fill( score, X0 )
        sighists["sig02"].Fill( score, X1 )
        sighists["sig03"].Fill( score, X2 )
        sighists["sig04"].Fill( score, X3 )
        sighists["sig05"].Fill( score, U1 )
        sighists["sig06"].Fill( score, U2 )
        sighists["sig07"].Fill( score, V1 )
        sighists["sig08"].Fill( score, V2 )
        sighists["sig09"].Fill( score, X0 - X1 )
        sighists["sig10"].Fill( score, X2 - X3 )
        sighists["sig11"].Fill( score, X0 - (X1 + X2 + X3)/3.0 )
        sighists["sig12"].Fill( score, X1 - (X0 + X2 + X3)/3.0 )
        sighists["sig13"].Fill( score, X2 - (X0 + X1 + X3)/3.0 )
        sighists["sig14"].Fill( score, X3 - (X0 + X1 + X2)/3.0 )
        sighists["sig15"].Fill( score, (X0 + X1)/2.0 - (X2 + X3)/2.0 )
        sighists["sig16"].Fill( score, (X0 + X1 + X2 + X3)/4.0 )
        sighists["sig17"].Fill( score, U1 - U2 )
        sighists["sig18"].Fill( score, V1 - V2 )
        sighists["sig19"].Fill( score, (U1 + U2)/2.0 - (V1 + V2)/2.0 )
        sighists["sig20"].Fill( score, (U1 + U2 + V1 + V2)/4.0 )
        sighists["sig21"].Fill( score, (X0 + X1 + X2 +X3)/4.0 - (U1 + U2 + V1 + V2)/4.0 )
        
        
        xhits = 0
        for i in [X0, X1, X2, X3]:
            if i > -0.5:
                xhits += 1
        uhits = 0
        for i in [U1, U2]:
            if i > -0.5:
                uhits += 1
        vhits = 0
        for i in [V1, V2]:
            if i > -0.5:
                vhits +=1

        uvhits = uhits + vhits
        nhits = xhits + uhits + vhits

        sighists["sig22"].Fill( score, nhits )
        sighists["sig23"].Fill( score, xhits )
        sighists["sig24"].Fill( score, uvhits )
        sighists["sig25"].Fill( score, uhits )
        sighists["sig26"].Fill( score, vhits )




    for iscore, score in enumerate(bkgML):
        X0 = bkgX0[iscore]
        X1 = bkgX1[iscore]
        X2 = bkgX2[iscore]
        X3 = bkgX3[iscore]
        U1 = bkgU1[iscore]
        U2 = bkgU2[iscore]
        V1 = bkgV1[iscore]
        V2 = bkgV2[iscore]

        bkghists["bkg01"].Fill( score, X0 )
        bkghists["bkg02"].Fill( score, X1 )
        bkghists["bkg03"].Fill( score, X2 )
        bkghists["bkg04"].Fill( score, X3 )
        bkghists["bkg05"].Fill( score, U1 )
        bkghists["bkg06"].Fill( score, U2 )
        bkghists["bkg07"].Fill( score, V1 )
        bkghists["bkg08"].Fill( score, V2 )
        bkghists["bkg09"].Fill( score, X0 - X1 )
        bkghists["bkg10"].Fill( score, X2 - X3 )
        bkghists["bkg11"].Fill( score, X0 - (X1 + X2 + X3)/3.0 )
        bkghists["bkg12"].Fill( score, X1 - (X0 + X2 + X3)/3.0 )
        bkghists["bkg13"].Fill( score, X2 - (X0 + X1 + X3)/3.0 )
        bkghists["bkg14"].Fill( score, X3 - (X0 + X1 + X2)/3.0 )
        bkghists["bkg15"].Fill( score, (X0 + X1)/2.0 - (X2 + X3)/2.0 )
        bkghists["bkg16"].Fill( score, (X0 + X1 + X2 + X3)/4.0 )
        bkghists["bkg17"].Fill( score, U1 - U2 )
        bkghists["bkg18"].Fill( score, V1 - V2 )
        bkghists["bkg19"].Fill( score, (U1 + U2)/2.0 - (V1 + V2)/2.0 )
        bkghists["bkg20"].Fill( score, (U1 + U2 + V1 + V2)/4.0 )
        bkghists["bkg21"].Fill( score, (X0 + X1 + X2 +X3)/4.0 - (U1 + U2 + V1 + V2)/4.0 )

        xhits = 0
        for i in [X0, X1, X2, X3]:
            if i > -0.5:
                xhits += 1
        uhits = 0
        for i in [U1, U2]:
            if i > -0.5:
                uhits += 1
        vhits = 0
        for i in [V1, V2]:
            if i > -0.5:
                vhits +=1

        uvhits = uhits + vhits
        nhits = xhits + uhits + vhits

        bkghists["bkg22"].Fill( score, nhits )
        bkghists["bkg23"].Fill( score, xhits )
        bkghists["bkg24"].Fill( score, uvhits )
        bkghists["bkg25"].Fill( score, uhits )
        bkghists["bkg26"].Fill( score, vhits )


    ######## drawing and saving histograms

    for name in sig_name_dict:
        c = sigcanvs[name]
        c.cd()
        sighists[name].Draw("COLZ")
        c.SaveAs("varplots/%s.pdf" % (c.GetName()))

    for name in bkg_name_dict:
        c = bkgcanvs[name]
        c.cd()
        bkghists[name].Draw("COLZ")
        c.SaveAs("varplots/%s.pdf" % (c.GetName()))
