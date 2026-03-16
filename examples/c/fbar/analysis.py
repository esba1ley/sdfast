"""Import and plot SDFast fbar results"""

# Python standard packages (comes with Python)
import sys

# Open Source Python Imports (from pip/miniforge conda, etc.)
import pandas as pd
from matplotlib import pyplot as plt

# Local Organization Imports
# None

# Local Project Imports
# None


# grab program name from command line
data_fname = sys.argv[1]
exe_name = data_fname.split('.')[0]

# Ingest data using a CSV reader set to a white space separator, 
# skipping first row of captured STDOUT and using the second row 
# as the header column and the first column as the index.
data = pd.read_csv(
    f"{data_fname}",
    sep='\s+',  ## replaces deprecated delim_whitespace=True
    skiprows=0,
    header=1,
    index_col=0,
)

print(data)

# plot data
fig, ax = plt.subplots(2,1, figsize=(8,11), sharex=True)
data.loc[:,['crank_pos','crank_vel']].plot(ax=ax[0])
ax[0].grid()
data.iloc[:,2:].plot(ax=ax[1])
ax[1].grid()
fig.savefig(f'{exe_name}_output.pdf')
