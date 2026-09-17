
# MAIN FUNCTION TO CALL THE L1B MODULE

from l1b.src.l1b import l1b

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = "C:/Users/santi/Desktop/MSTR-2/PODT/gitt/gitttt/auxiliary"

indir = "C:/Users/santi/Desktop/MSTR-2/PODT/EODP_TER_2021/EODP-TS-L1B/input"

outdir = "C:/Users/santi/Desktop/MSTR-2/PODT/EODP_TER_2021/EODP-TS-L1B/output_santi_noteq"
# Initialise the ISM
myL1b = l1b(auxdir, indir, outdir)
myL1b.processModule()
