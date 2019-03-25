"""
Run me like:
> python test_root2numpy.py

Reading material:
http://lcginfo.cern.ch/release/94python3/
https://github.com/scikit-hep/uproot
"""
import pandas as pd
from collections import OrderedDict
import sys
from array import array
try:
    import uproot
except:
    sys.exit("""Please set up the python3 tools! Run:
setupATLAS
lsetup "lcgenv -p LCG_94python3 x86_64-slc6-gcc62-opt keras_preprocessing" && \\
lsetup "lcgenv -p LCG_94python3 x86_64-slc6-gcc62-opt keras_applications" && \\
lsetup "lcgenv -p LCG_94python3 x86_64-slc6-gcc62-opt keras" && \\
lsetup "lcgenv -p LCG_94python3 x86_64-slc6-gcc62-opt matplotlib" && \\
lsetup "lcgenv -p LCG_94python3 x86_64-slc6-gcc62-opt bleach" && \\
lsetup "lcgenv -p LCG_94python3 x86_64-slc6-gcc62-opt html5lib" && \\
lsetup "lcgenv -p LCG_94python3 x86_64-slc6-gcc62-opt astor" && \\
lsetup "lcgenv -p LCG_94python3 x86_64-slc6-gcc62-opt grpcio" && \\
lsetup "lcgenv -p LCG_94python3 x86_64-slc6-gcc62-opt termcolor" && \\
lsetup "lcgenv -p LCG_94python3 x86_64-slc6-gcc62-opt tensorflow" && \\
pip install uproot --user && \\
echo Done!""")

def main():

    # a hazel file chosen at random
    fname_sig = "/home/net3/afortman/projects/hotpot/oct_sim/nohit15/hazel_both_smearf_100k_35ns_e100_nohit15.root"
    print("\n %30s :: %s" % ("Signal filename of interest", fname_sig))
    fname_bkg = "/home/net3/afortman/projects/hotpot/oct_sim/nohit15/hazel_bkg_smearf_1M_35ns_e100_nohit15.root"
    print("\n %30s :: %s" % ("Background filename of interest", fname_bkg))
    
    files = []
    files.append(fname_sig)
    files.append(fname_bkg)
    
    all_brs = []

    # uprooted!
    for ifname, fname in enumerate(files):
        upfile = uproot.open(fname)
        print("\n %30s :: %s" % ("File of interest", upfile))

        # the "TTree"
        tree = upfile["hazel"]
        print("\n %30s :: %s" % ("Uprooted TTree",   tree))
        print("\n %30s :: %s" % ("tree.title",       tree.title))
        print("\n %30s :: %s" % ("tree.numbranches", tree.numbranches))
        print("\n %30s :: %s" % ("tree.numentries",  tree.numentries))

        # accessing the "branches"
        print()
        for key in tree.keys():
            print(" %30s :: %20s  %s" % ("Uprooted TBranch", key, type(tree.array(key))))

        # a quick event loop
        print("\n %30s" % ("Parsing the tree"))
        ents = tree.numentries
        brs = OrderedDict()
        brs['id']= array('i',[ifname]*ents)
        for key in tree.keys():
            brs[key] = tree[key].array()
        all_brs.append(brs)

    df_sig = pd.DataFrame(all_brs[0])
    df_bkg = pd.DataFrame(all_brs[1])
    dataset = pd.concat([df_sig, df_bkg])
    #print(dataset)
    mixed_data = dataset.sample(frac=1)
    print(mixed_data)

    mixed_data.to_csv('train.csv',index=False)

    #for ent in range(ents):
    #    for key in tree.keys():
    #        print(" %30s :: ent = %3s, key = %20s, val = %s" % ("", ent, key, brs[key][ent]))
    #    print()
    #    if ent > 10:
    #        break


if __name__ == "__main__":
    main()
