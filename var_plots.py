import ROOT
from ROOT import TMVA, TFile, TCanvas, TH2F
import sys
from array import array

######## run like: python -i var_plots.py -n 10k -e 95 --ML DNN ##########

from optparse import OptionParser
parser = OptionParser()

parser.add_option('-n', type='string', action='store',
                  default= '10k',
                  dest='n',
                  help='number of events to evaluate over, 10k or 100k or 1M etc')

parser.add_option('-e', type='string', action='store',
                  default= '',
                  dest='eff',
                  help='hit efficiency')

parser.add_option('--ML', type='string', action='store',
                  default= 'DNN',
                  dest='ML',
                  help='Which ML method? DNN, BDT, MLP, or kNN')

(options, args) = parser.parse_args()
argv = []


ML = str(options.ML)


TMVA.Tools.Instance()
reader = ROOT.TMVA.Reader()

fsig = ROOT.TFile("efftesting/hazel_both_smearf_"+str(options.n)+"_35ns_e"+str(options.eff)+".root")
fbkg = ROOT.TFile("efftesting/hazel_bkg_smearf_"+str(options.n)+"_35ns_e"+str(options.eff)+".root")

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

reader.BookMVA( str(options.ML),"dataset_e"+str(options.eff)+"/weights/TMVAClassification_"+ML+".weights.xml")

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
    
    sigML.append( reader.EvaluateMVA( str(options.ML) ) )


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

    bkgML.append( reader.EvaluateMVA( str(options.ML) ) )


############ make some 2D histograms of var vs ML score

signal_names = ["Signal X0","Signal X1","Signal X2","Signal X3","Signal U1","Signal U2","Signal V1","Signal V2"]
bkg_names = ["Background X0","Background X1","Background X2","Background X3","Background U1","Background U2","Background V1","Background V2"]
siglists = [ sigX0, sigX1, sigX2, sigX3, sigU1, sigU2, sigV1, sigV2 ]
bkglists = [ bkgX0, bkgX1, bkgX2, bkgX3, bkgU1, bkgU2, bkgV1, bkgV2 ]

for iname, name in enumerate(signal_names):
    bname = bkg_names[iname]
    hsig = TH2F( name, name+" vs "+ML+" score", 100, 0.0, 1.0, 13, -1.0, 12.0)
    hbkg = TH2F( bname, bname+" vs "+ML+" score", 100, 0.0, 1.0, 13, -1.0, 12.0)

    for iscore, score in enumerate(sigML):
        hsig.Fill( score, siglists[iname][iscore] )
    
    for iscore, score in enumerate(bkgML):
        hbkg.Fill( score, bkglists[iname][iscore] )

    c_sig = TCanvas( name, name )
    c_sig.cd()
    hsig.GetXaxis().SetTitle( ML+" Score")
    hsig.GetYaxis().SetTitle( name )
    hsig.Draw("COLZ")
    c_sig.SaveAs("varplots/%s.pdf" % (c_sig.GetName().replace(" ", "")+"_"+ML+"_"+str(options.n)+"_e"+str(options.eff)))

    c_bkg = TCanvas( bname, bname )
    c_bkg.cd()
    hbkg.GetXaxis().SetTitle( ML+" Score")
    hbkg.GetYaxis().SetTitle( bname )
    hbkg.Draw("COLZ")
    c_bkg.SaveAs("varplots/%s.pdf" % (c_bkg.GetName().replace(" ", "")+"_"+ML+"_"+str(options.n)+"_e"+str(options.eff)))



