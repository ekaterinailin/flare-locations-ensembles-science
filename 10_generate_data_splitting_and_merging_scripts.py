""" 
Module to generate scripts to execute a module
on a split dataset, and merge the output files back 
together.

How to call:

python 11_generate_data_splitting_and_merging_scripts.py <dataframe you want to split> <desired number of splits> <column to split on> <module to apply to splitted frames>


e.g.:

python 11_generate_data_splitting_and_merging_scripts.py results/2022_01_10_flares_alpha_beta_rand.csv 100 starid 10_get_aggregate_parameters.py


Ekaterina Ilin 
MIT License (2022)
"""

import numpy as np
import pandas as pd
from datetime import date
import sys

if __name__ == "__main__":
    
    today = date.today().strftime("%Y_%m_%d")
    
    df_to_split_name = sys.argv[1]
    
    df_to_split = pd.read_csv(df_to_split_name, 
                              names=['istart','istop','tstart','tstop',                  
                              'ed_rec','ed_rec_err','ampl_rec',
                              'dur','total_n_valid_data_points','midlat_deg',
                              'inclination_deg','n_spots','beta_1',
                              'beta_2','beta_3','alpha_1',
                              'alpha_2','alpha_3','lons_1',
                              'lons_2','lons_3','starid'])
    
    nsplits = int(sys.argv[2])
    
    split_by = sys.argv[3]
    
    applyscript = sys.argv[4]
    
    split_df_rows = np.array_split(df_to_split[split_by].unique(), nsplits)
    
    split_dfs = [df_to_split[df_to_split[split_by].isin(rows)] for rows in split_df_rows]
    print(f"Split DataFrame into {nsplits} smaller frames.")
    
    namecore = df_to_split_name[8:-4]

    scriptname = f"11_applyscript_{today}_{namecore}.sh"
    with open(scriptname, "w") as fin:
        for i, df_ in enumerate(split_dfs):
            finname = f"results/11_applyscript_{today}_{namecore}_{i}.csv"
            foutname = f"results/12_merge_{today}_{namecore}_{i}.csv"
            df_.to_csv(finname)
            applyscript_command = f"python {applyscript} {finname} {foutname}\n"
            fin.write(applyscript_command)
    print(f"Generated script to apply module {applyscript} to split frames:\n{scriptname}\n")
    
    scriptname = f"12_merge_{today}_{namecore}.sh"
    with open(scriptname, "w") as fout:
        merge_command = f"python 12_merge_files.py 11_merge_{today}_{namecore} {nsplits}\n"
        fout.write(merge_command)
        for i in range(nsplits):
            delete_command = (f"rm results/11_applyscript_{today}_{namecore}_{i}.csv\n"
                              f"rm results/12_merge_{today}_{namecore}_{i}.csv\n")
            fout.write(delete_command)
    print(f"Generated script to merge results and delte split frames:\n{scriptname}\n")
