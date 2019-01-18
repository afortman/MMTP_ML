import ROOT
from ROOT import TFile, TTree, TGraph
from array import array
import sys
import random

###http://tuna.web.cern.ch/tuna/ForPatrick/find_tdo_bounds.py
###https://root.cern.ch/how/how-write-ttree-python
###https://root.cern.ch/root/html/tutorials/fit/fitLinear.C.html


####### Example command to run, for background only and smearing of 2 strips ########
############ python hazel.py -b bkg --smear 2 ###########

from optparse import OptionParser
parser = OptionParser()

parser.add_option('-b', type='string', action='store',
                  default= 'sig',
                  dest='bkg',
                  help='Convention could be bkg for background only, default means signal only, sigbkg or both for both')

parser.add_option('--smear', type='string', action='store',
                  default = "0",
                  dest='smear',
                  help='Position resolution in strips')

(options, args) = parser.parse_args()
argv = []


def main():
    f_in = TFile("output_"+str(options.bkg)+"_smear"+str(options.smear)+".root")
    f_out = TFile( 'hazel_'+str(options.bkg)+'_smear'+str(options.smear)+'.root', 'recreate' )
    
    tree = TTree( 'hazel', 'hazel' )
    
    
    tr   = f_in.Get("gingko")
 
    branches = {}
    for var in ["EventNumHazel",
                "EventNumGingko",
                "trigger_gingko",
                "iroad_x",
                "iroad_u",
                "iroad_v",
                "Hit_plane0",
                "Hit_plane1",
                "Hit_plane2",
                "Hit_plane3",
                "Hit_plane4",
                "Hit_plane5",
                "Hit_plane6",
                "Hit_plane7",
                "Hit_n",
                "dtheta",
                "chi2"
                ]:
        if var != "dtheta" and var != "chi2":
            branches[var] = array('i', [ 0 ])
            tree.Branch(var, branches[var], "%s/%s" % (var, "I"))
        elif var == "dtheta" or var == "chi2":
            branches[var] = array('d', [ 0.0 ])
            tree.Branch(var, branches[var], "%s/%s" % (var, "D"))
    
    
    offset_x = 0
    offset_u = -16
    offset_v = 17
    
    zplanes = [0.0, 11.2, 32.4, 43.6, 113.6, 124.8, 146.0, 157.2]
    planes_x = [0, 1, 6, 7]
    planes_u = [2, 4]
    planes_v = [3, 5]
    
    EventNumHazel = 0

    for ent in range(tr.GetEntries()):
        
        _ = tr.GetEntry(ent)
        
        
    ######### Choose the trigger with the maximum number of real muon hits
        realmuon = list(tr.N_muon)
        if realmuon == []:
            continue
        maxmuon = max(realmuon)
        nmax = realmuon.count(maxmuon)
        if nmax == 1:
            itr = realmuon.index(maxmuon)
    ########## if more than one trigger with the max number of muon hits, choose one randomly from those
        elif nmax > 1:
            trigs = []
            for ind, val in enumerate(realmuon):
                if val == maxmuon:
                    trigs.append(ind)
            itr = random.choice(trigs)
            
        branches["EventNumHazel"][0] = EventNumHazel
        branches["EventNumGingko"][0] = ent
        branches["trigger_gingko"][0] = itr
        branches["dtheta"][0] = tr.dtheta[itr]

        branches["Hit_plane0"][0] = -1
        branches["Hit_plane1"][0] = -1
        branches["Hit_plane2"][0] = -1
        branches["Hit_plane3"][0] = -1
        branches["Hit_plane4"][0] = -1
        branches["Hit_plane5"][0] = -1
        branches["Hit_plane6"][0] = -1
        branches["Hit_plane7"][0] = -1

        xroad = tr.iRoad_x[itr]
        uroad = tr.iRoad_u[itr]
        vroad = tr.iRoad_v[itr]


        branches["iroad_x"][0] = xroad
        branches["iroad_u"][0] = uroad
        branches["iroad_v"][0] = vroad


        strips = list(tr.Hit_strips[itr])
        planes = list(tr.Hit_planes[itr])

        branches["Hit_n"][0] = len(planes)

        for (strip, plane) in zip(strips, planes):
            if plane in planes_x:
                diffx = (strip+offset_x) - xroad*8
                branches["Hit_plane"+str(plane)][0] = diffx
            if plane in planes_u:
                diffu = (strip+offset_u) - uroad*8
                branches["Hit_plane"+str(plane)][0] = diffu
            if plane in planes_v:
                diffv = (strip+offset_v) - vroad*8
                branches["Hit_plane"+str(plane)][0] = diffv
        
        ######### Chi Square ##########
        xpos = array('d', [] )
        zpos = array('d', [] )
        for (strip, plane) in zip(strips, planes):
            if plane in planes_x:
                zpos.append( zplanes[plane] )
                xpos.append( strip*0.4 )
        gr = TGraph(len(xpos),zpos,xpos)
        gr.Fit("pol1")
        fit = gr.GetFunction("pol1")
        chi2 = fit.GetChisquare()
        NDF = fit.GetNDF()
        
        branches["chi2"][0] = chi2/NDF
        

        tree.Fill()

        EventNumHazel += 1
################ END OF LOOPS #####################
    
    f_out.Write()
    f_out.Close()



if __name__ == "__main__":
    main()

