"""
https://github.com/scikit-hep/uproot
"""
import sys
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
    fname = "/home/net3/afortman/projects/hotpot/oct_sim/hazel_both_smearf_10M_35ns_e95.root"
    print("\n %30s :: %s" % ("Filename of interest", fname))

    # uprooted!
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
    brs  = {}
    for key in tree.keys():
        brs[key] = tree[key].lazyarray()
    for ent in range(ents):
        for key in tree.keys():
            print(" %30s :: ent = %3s, key = %20s, val = %s" % ("", ent, key, brs[key][ent]))
        print()
        if ent > 10:
            break


if __name__ == "__main__":
    main()
