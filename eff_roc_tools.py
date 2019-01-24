import ROOT
from array import array



########### Find bkgrejection at 95% signal efficiency

def FindPoint(sig_eff, bkg_rej):
    sigpoint = []
    bkgpoint = []
    while len(sigpoint) < 1:
        for ie, e in enumerate(sig_eff):
            if e < 0.95:
                sigpoint.append( sig_eff[ie-1] )
                bkgpoint.append( bkg_rej[ie-1] )
    return( sigpoint[0], bkgpoint[0] )




############# SET DNN

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


################ SET kNN

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


########## Find Delta Theta

def FindCurveDTheta(sig_dtheta, bkg_dtheta):
    ########## scan over different cutoff angles and prepare arrays for plotting ##
    sig_eff = array( 'd' )
    bkg_rej = array( 'd' )
    for iangle in range(0,1000):
        cutoff = iangle*0.0001
        sig = 0
        bkg = 0
        for theta_sig in sig_dtheta:
            if abs(theta_sig) < cutoff:
                sig += 1
        for theta_bkg in bkg_dtheta:
            if abs(theta_bkg) < cutoff:
                bkg += 1
        sig_eff.append( float(sig)/len(sig_dtheta) )
        bkg_rej.append( 1.0 - float(bkg)/len(bkg_dtheta) )
    
    return [sig_eff, bkg_rej]



########## Find Chi2

def FindCurveChi2(sig_chi2, bkg_chi2):
    ########## scan over different chi2/NDF and prepare arrays for plotting ##
    sig_eff = array( 'd' )
    bkg_rej = array( 'd' )
    chiscan = [k*0.0001 for k in range(0,11)]+[i*0.001 for i in range(1,1001)]+[j*0.01 for j in range(101,1200)]
    for cutoff in chiscan:
        #cutoff = ichi2*0.001
        sig = 0
        bkg = 0
        for chi2_sig in sig_chi2:
            if abs(chi2_sig) < cutoff:
                sig += 1
        for chi2_bkg in bkg_chi2:
            if abs(chi2_bkg) < cutoff:
                bkg += 1
        sig_eff.append( float(sig)/len(sig_chi2) )
        bkg_rej.append( 1.0 - float(bkg)/len(bkg_chi2) )
    
    return [sig_eff, bkg_rej]


