import ROOT
from ROOT import TFile, TTree
from array import array

###http://tuna.web.cern.ch/tuna/ForPatrick/find_tdo_bounds.py
###https://root.cern.ch/how/how-write-ttree-python


def main():
 
    f_out = TFile( 'hazel.root', 'recreate' )
    tree = TTree( 'hazel', 'hazel' )
    
    f_in = TFile("output.root")
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
                "Hit_n"
                ]:
        branches[var] = array('i', [ 0 ])
        tree.Branch(var, branches[var], "%s/%s" % (var, "I"))
    
    
    offset_x = 0
    offset_u = -16
    offset_v = 17
    
    planes_x = [0, 1, 6, 7]
    planes_u = [2, 4]
    planes_v = [3, 5]
    
    EventNumHazel = 0
    for ent in range(tr.GetEntries()):
        
        _ = tr.GetEntry(ent)
        
        
        for itr in range(tr.Ntriggers):
            
            branches["EventNumHazel"][0] = EventNumHazel
            branches["EventNumGingko"][0] = ent
            branches["trigger_gingko"][0] = itr
            
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
            
        
            tree.Fill()
            EventNumHazel += 1
################ END OF LOOPS #####################
    f_out.Write()
    f_out.Close()



if __name__ == "__main__":
    main()
