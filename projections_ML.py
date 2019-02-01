import ROOT
from ROOT import TMVA, TFile, TCanvas, TH2F, gStyle, TGraph2D
import sys
from array import array
from random import randint


######### run like python -i projections_ML.py -n 1M --layers 4X4UV -e 100

f_out = ROOT.TFile("projection_plots.root", "recreate")

from optparse import OptionParser
parser = OptionParser()

parser.add_option('-n', type='string', action='store',
                  default= '10k',
                  dest='n',
                  help='number of events to evaluate over, 10k or 100k or 1M etc')

parser.add_option('--layers', type='string', action='store',
                  default= '',
                  dest='layers',
                  help='suffix')

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

folder = "projections_"+str(options.n)+"_"+str(options.layers)

#ML = str(options.ML)
eff = options.eff

gStyle.SetPadLeftMargin(0.1);
gStyle.SetPadBottomMargin(0.1)
gStyle.SetPadRightMargin(0.18);
gStyle.SetPadTopMargin(0.1)
gStyle.SetTitleX(0.3);
gStyle.SetTitleAlign(23);



planes = ["Hit_plane0","Hit_plane1","Hit_plane2","Hit_plane3","Hit_plane4","Hit_plane5","Hit_plane6","Hit_plane7"]
names = [("Hit_plane0","X0"),("Hit_plane1","X1"), ("Hit_plane2","U0"), ("Hit_plane3","V0"), ("Hit_plane4","U1"), ("Hit_plane5","V1"), ("Hit_plane6","X2"), ("Hit_plane7","X3")]
samples = [("sig","Signal"),("bkg","Background")]


MLlist = ["DNN","BDT","MLP"]
#MLlist = ["DNN"]

for ML in MLlist:
    
    d_out = f_out.mkdir("ProjectionPlots_"+ML)

    TMVA.Tools.Instance()
    reader = ROOT.TMVA.Reader()

    branches = {}
    for branch in planes:
        branches[branch] = array('f', [ 0.0 ])
        reader.AddVariable(branch, branches[branch])

    reader.BookMVA( ML,"dataset_"+str(options.n)+"_"+str(options.layers)+"/weights/TMVAClassification_"+ML+".weights.xml")

    for sample in samples:
        
        for iplanex, planex in enumerate(names):
            
            for jplaney, planey in enumerate(names):
                
                ########### avoid making more than one of the same plot
                if jplaney > iplanex:
                    
                    ###### set other 6 dimensions
                    allplanes = [n for n in names]
                    allplanes.remove(planex)
                    allplanes.remove(planey)
                    otherplanes = allplanes



                    ########## set up arrays for plotting
                    plane_x = array('f', [])
                    plane_y = array('f', [])
                    MLscores = array('f', [])

                    ######### for each strip in a layer, and each strip in another layer, find ML score
                    for strip1 in range(0,12):
                        branches[planey[0]][0] = float(strip1)
                        for strip2 in range(0,12):
                            branches[planex[0]][0] = float(strip2)
                            
                             ###### set other 6 dimensions
                            
                            if sample[0]=="sig":
                                scores = []
                                for s in range(0,12):
                                    for plane in otherplanes:
                                        branches[plane[0]][0] = float(s)
                                    scores.append( reader.EvaluateMVA( ML ) )
                                MLscore = sum(scores)/float(len(scores))

                            elif sample[0]=="bkg":
                                scores = []
                                for b in range(0,1000):
                                    for plane in otherplanes:
                                        branches[plane[0]][0] = float(randint(0, 11))
                                    scores.append( reader.EvaluateMVA( ML ) )
                                MLscore = sum(scores)/float(len(scores))
                            
                            plane_y.append( float(strip1) )
                            plane_x.append( float(strip2) )
                            MLscores.append( MLscore )
                    
                    ########## Make canvases, draw plots, and save them
                    c = TCanvas(sample[0]+"_"+planey[1]+"vs"+planex[1]+"vs"+ML,sample[0]+"_"+planey[1]+"vs"+planex[1]+"vs"+ML)
                    gr = TGraph2D( len(MLscores), plane_x, plane_y, MLscores)
                    gr.SetName(sample[1]+" "+planey[1]+" vs "+planex[1]+" vs "+ML+" score");
                    gr.Draw("COLZ")
                    c.Update()
                    gr.SetTitle( sample[1]+" "+planey[1]+" vs "+planex[1]+" vs "+ML+" score" )
                    gr.GetXaxis().SetTitle( planex[1] )
                    gr.GetYaxis().SetTitle( planey[1] )
                    gr.GetZaxis().SetTitle( ML+" score" )
                    gr.GetZaxis().SetTitleOffset(1.2)

                    d_out.cd()
                    c.Write()
                    c.SaveAs(folder+"/%s.pdf" % (c.GetName()))

    
