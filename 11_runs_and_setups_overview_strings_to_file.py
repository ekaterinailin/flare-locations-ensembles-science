""" 
Python3.8 -- UTF-8

Ekaterina Ilin 
MIT License (2022)

Script to put all manually added runs into a table, and save it as a csv file.

"""

import numpy as np

if __name__ == "__main__":

    #all are 5 deg wide
    tstampsmeta = [
        ([("2022_03_30_20_21_2022_03_30_19_47", "1 spot, bi-hem., 40-60", "grey"),
            ("2022_03_29_10_44_2022_03_29_09_43", "1 spot, bi-hem., 20-40", "grey"),
            ("2022_03_30_20_42_2022_03_30_20_25", "1 spot, bi-hem., 17-28", "grey"),
            ("2022_03_24_15_52_2022_03_24_15_18", "1 spot, bi-hem.,10-20", "grey"),
            ("2022_03_30_21_00_2022_03_30_20_44", "1 spot, bi-hem., 8-15", "grey"),
            ("2022_03_29_11_08_2022_03_29_10_49", "1 spot, bi-hem., 5-10", "grey"),
            ("2022_03_30_21_17_2022_03_30_21_04", "1 spot, bi-hem., 4-7", "grey"),
            ("2022_03_31_15_45_2022_03_31_15_25", "1 spot, bi-hem., 2-4", "grey"),
        
        ], "#E69F00"),

        ([("2022_03_30_21_38_2022_03_30_21_20", "1-3 spots, bi-hem., 20-30", "orange"),
            ("2022_03_28_20_55_2022_03_28_20_38", "1-3 spots, bi-hem., 10-20", "orange"),
            ("2022_03_30_21_58_2022_03_30_21_41", "1-3 spots, bi-hem., 9-14", "orange"),
            ("2022_03_25_09_15_2022_03_25_08_58", "1-3 spots, bi-hem.,5-10", "orange"),
            ("2022_03_30_22_17_2022_03_30_22_00", "1-3 spots, bi-hem., 4-8", "orange"),
            ("2022_03_28_22_09_2022_03_28_21_53", "1-3 spots, bi-hem., 2.5-5", "orange"),
            ("2022_03_31_08_25_2022_03_31_08_09", "1-3 spots, bi-hem., 2-4", "orange"),
            ("2022_03_31_17_44_2022_03_31_17_29", "1-3 spots, bi-hem., 1-2", "grey"),
        
        ], "#CC79A7"),

        ([("2022_03_31_10_18_2022_03_31_09_59", "1-3 spots, mono-hem., 20-30", "orange"),
            ("2022_03_28_22_55_2022_03_28_22_36", "1-3 spots, mono-hem., 10-20", "magenta"),
            ("2022_03_31_09_49_2022_03_31_09_27", "1-3 spots, mono-hem., 9-14", "orange"),
            ("2022_03_26_07_30_2022_03_26_07_09", "1-3 spots, mono-hem., 5-10", "r"),
            ("2022_03_31_09_19_2022_03_31_08_48", "1-3 spots, mono-hem., 4-8", "orange"),
            ("2022_03_28_23_41_2022_03_28_23_21", "1-3 spots, mono-hem., 2.5-5", "orange"),
            ("2022_03_31_08_45_2022_03_31_08_27", "1-3 spots, mono-hem., 2-4", "orange"),
            ("2022_03_31_17_25_2022_03_31_17_08", "1-3 spots, mono-hem., 1-2", "grey"),
            
        ], "#56B4E9"),
            
        ([("2022_03_31_18_11_2022_03_31_17_47", "3-5 spots, bi-hem., 15-25", "r"),
            ("2022_03_31_13_46_2022_03_31_13_23", "3-5 spots, bi-hem., 10-15", "r"),
            ("2022_03_28_21_18_2022_03_28_20_59", "3-5 spots, bi-hem., 5-10", "r"),
            ("2022_03_31_14_33_2022_03_31_14_13", "3-5 spots, bi-hem., 4-7", "r"),
            ("2022_03_25_09_55_2022_03_25_09_36","3-5 spots, bi-hem., 2.5-5", "r"),
            ("2022_03_31_15_00_2022_03_31_14_41", "3-5 spots, bi-hem., 2-4", "r"),
            ("2022_03_28_22_32_2022_03_28_22_14", "3-5 spots, bi-hem., 1.25-2.5", "r"),
            ("2022_03_31_15_22_2022_03_31_15_04", "3-5 spots, bi-hem., 1-2", "r"),
            
        ], "#230072B2"),
            
        ([("2022_03_31_10_42_2022_03_31_10_22", "3-5 spots, mono-hem., 10-15", "r"),
            ("2022_03_28_23_17_2022_03_28_22_57", "3-5 spots, mono-hem., 5-10", "magenta"),
            ("2022_03_31_11_21_2022_03_31_10_48", "3-5 spots, mono-hem., 4-7", "r"),
            ("2022_03_25_19_35_2022_03_25_19_16","3-5 spots,  mono-hem., 2.5-5", "r"),
            ("2022_03_31_11_50_2022_03_31_11_23", "3-5 spots, mono-hem., 2-4", "r"),
            ("2022_03_29_00_08_2022_03_28_23_49", "3-5 spots, mono-hem.,  1.25-2.5", "orange"),
            ("2022_03_31_12_11_2022_03_31_11_52", "3-5 spots, mono-hem., 1-2", "r"),
            ("2022_03_31_18_39_2022_03_31_18_16", "3-5 spots, mono-hem., 1", "r"),
        
        ], "#009E73"), 

            ]
            
            
    # save results to a file

    # write header
    with open("results/2022_05_all_runs.csv","w") as f:
        f.write("tstamp,nspots,hem,nflares,color\n")

    # write data

    # loop over setups
    for setup in range(5):

        # loop over runs
        for run in range(8):

            with open("results/2022_05_all_runs.csv","a") as f:
        
                # timestamp
                a = str(np.array(tstampsmeta)[setup][0][run][0])
        
                # values
                b = str(np.array(tstampsmeta)[setup][0][run][1])
                b = b.replace(" ", "").replace("spots", "").replace("spot", "")
        
                # color
                c = str(np.array(tstampsmeta)[setup][1])
        
                # compose string
                string = f"{a},{b},{c}\n"

                # write to file
                f.write(string)