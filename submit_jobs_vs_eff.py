"""
Run me like:
 > cd /path/to/your/MMTP_ML/
 > python submit_jobs_vs_eff.py
"""
import os
import sys
import time

def main():

    # setup
    now = time.strftime("%Y-%m-%d-%Hh%Mm%Ss")
    top = "/gpfs3/harvard/mmtp_ml/batch-%s" % (now)
    job = "job.sh"
    exe = os.path.abspath("./tmvatest.py")
    if not os.path.isfile("./tmvatest.py"):
        fatal("Please run this script from a directory which contains tmvatest.py!")

    # announce
    print
    print "Launching jobs here: %s" % (top)
    print

    # loop over efficiencies
    effs = range(90, 101, 1)
    for eff in effs:

        # create the output dir
        jobdir = os.path.join(top, "%03i" % (eff))
        os.makedirs(jobdir)

        # create the job file
        jobname = os.path.join(jobdir, job)
        jobconf = {"eff": eff, "exe": exe, "jobdir": jobdir}
        jobfile = open(jobname, "w")
        jobfile.write(template() % (jobconf))
        jobfile.close()

        # launch!
        cmd = "qsub -V -q tier3 %s" % (jobname)
        os.system(cmd)
        time.sleep(1)
        
    # done cat
    print
    print "Done! <^.^>"
    print

def template():
    return """
#$ -o %(jobdir)s/stdout_$JOB_ID.txt
#$ -e %(jobdir)s/stderr_$JOB_ID.txt
cd %(jobdir)s
python %(exe)s -e %(eff)s
"""

def fatal(msg):
    sys.exit("Fatal error: %s" % (msg))

if __name__ == "__main__":
    main()
