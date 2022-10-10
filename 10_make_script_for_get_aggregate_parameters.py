""" 


Ekaterina Ilin 
MIT License (2022)
"""

import numpy as np
import pandas as pd
from datetime import datetime
import sys

from flares.__init__ import (SCRIPT_NAME_GET_AGGREGATE_PARAMETERS,
							 SCRIPT_NAME_MERGE_FILES,
							)

if __name__ == "__main__":
    
    # timestamp2
    today = "2022_06_30_10_00"#datetime.now().strftime("%Y_%m_%d_%H_%M")
    
	# training data
    df_to_split_name = sys.argv[1]
    df_to_split = pd.read_csv(df_to_split_name)
    
	# split the data set
    nsplits = int(sys.argv[2])
    
	# split such that flare tables for individual LCs are kept together
    split_by = "starid"
    
	# apply the default script to apply to each split dataset
    applyscript = SCRIPT_NAME_GET_AGGREGATE_PARAMETERS
    
	# get the indices to the rows in each data set
    split_df_rows = np.array_split(df_to_split[split_by].unique(), nsplits)
    
	# get a list of DataFrames split by the above indices
    split_dfs = [df_to_split[df_to_split[split_by].isin(rows)] for rows in split_df_rows]
    print(f"Split DataFrame into {nsplits} smaller frames.")
    
	# define naming including timestamp1
    namecore = df_to_split_name[8:-4]

	# write a script to apply to all DataFrames
    scriptname = f"11_applyscript_{today}_{namecore}.sh"
    with open(scriptname, "w") as fin:
		# cycle over each split data set
        for i, df_ in enumerate(split_dfs):
			# define temporary input and output datasets
            finname = f"results/11_applyscript_{today}_{namecore}_{i}.csv"
            foutname = f"results/12_merge_{today}_{namecore}_{i}.csv"
			# write out the temporary split data set
            df_.to_csv(finname)
			# define the command to get aggregate parameters on this dataset			
            applyscript_command = f"python {applyscript} {finname} {foutname}\n"
			# add the command to the script
            fin.write(applyscript_command)
        

    print(f"Generated script to apply module {applyscript} to split frames:\n{scriptname}\n")
    
	# write a script to merge the aggregated temporary DataFrames back together
    scriptname = f"12_merge_{today}_{namecore}.sh"
    with open(scriptname, "w") as fout:
		# define the merging command and write it into the script
        merge_command = f"python {SCRIPT_NAME_MERGE_FILES} 12_merge_{today}_{namecore} {nsplits}\n"
        fout.write(merge_command)
		# delete temporary input and output files in the end
        for i in range(nsplits):
            delete_command = (f"rm results/11_applyscript_{today}_{namecore}_{i}.csv\n"
                              f"rm results/12_merge_{today}_{namecore}_{i}.csv\n")
            fout.write(delete_command)
    print(f"Generated script to merge results and delte split frames:\n{scriptname}\n")
