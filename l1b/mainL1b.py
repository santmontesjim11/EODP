
# MAIN FUNCTION TO CALL THE L1B MODULE

from l1b.src.l1b import l1b

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = "C:/Users/santi/Desktop/MSTR-2/PODT/gitt/gitttt/auxiliary"

indir = "C:/Users/santi/Desktop/MSTR-2/PODT/EODP-TS-E2E/myoutput"

outdir = "C:/Users/santi/Desktop/MSTR-2/PODT/EODP-TS-E2E/myoutput2"
# Initialise the ISM
myL1b = l1b(auxdir, indir, outdir)
myL1b.processModule()
