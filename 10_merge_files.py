""" 
Script to merge dataframes that were previously split.
Used within 12_*.sh scripts.
Not for standalone use.


Ekaterina Ilin 
MIT License (2022)
"""
import pandas as pd

import sys

if __name__ == "__main__":

    mergename = sys.argv[1]
    nframes = int(sys.argv[2])
    
    list_of_dataframes = [pd.read_csv(f"results/{mergename}_{i}.csv") for i in range(nframes)]
    
    df = pd.concat(list_of_dataframes)
    
    df.to_csv(f"results/{mergename[9:]}_merged.csv", index=False)
    
    print(f"Saved final results to {mergename[9:]}_merged.csv\n")
    
    
