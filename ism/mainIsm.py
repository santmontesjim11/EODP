
# MAIN FUNCTION TO CALL THE ISM MODULE

from ism.src.ism import ism

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = "C:/Users/santi/Desktop/MSTR-2/PODT/gitt/gitttt/auxiliary"
indir = "C:/Users/santi/Desktop/MSTR-2/PODT/EODP-TS-E2E/sgm_out" # small scene
outdir = "C:/Users/santi/Desktop/MSTR-2/PODT/EODP-TS-E2E/myoutput"

# Initialise the ISM
myIsm = ism(auxdir, indir, outdir)
myIsm.processModule()
