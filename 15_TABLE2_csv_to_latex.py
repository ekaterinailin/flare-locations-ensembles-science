import pandas as pd

if __name__ == "__main__":

    # read in fit results table
    df = pd.read_csv('results/fit_parameters.csv')

    # give errors optionally
    with_errors = False
    
    # remodel table
    df = df.drop(0,axis=0).rename(index=str,columns={"Unnamed: 0":" "})
    df = df.set_index(" ").T.astype("float")
    
    # make texable strings
    if with_errors:

        df[r"$a_1$"]=df.apply(lambda x: fr"${x['a']:.0f} \pm {x['ar']:.0f}$",axis=1)
        df[r"$a_2$"]=df.apply(lambda x: fr"${x['b']:.0f} \pm {x['br']:.0f}$",axis=1)
        df[r"$b_1$"]=df.apply(lambda x: fr"${x['c']:.0f} \pm {x['cr']:.0f}$",axis=1)
        df[r"$b_2$"]=df.apply(lambda x: fr"${x['d']:.0f} \pm {x['dr']:.0f}$",axis=1)
        df[r"$c$"]=df.apply(lambda x: fr"${x['e']:.0f} \pm {x['er']:.0f}$",axis=1)

    else:
        df[r"$a_1$"]=df.apply(lambda x: fr"${x['a']:.0f}$",axis=1)
        df[r"$a_2$"]=df.apply(lambda x: fr"${x['b']:.0f}$",axis=1)
        df[r"$b_1$"]=df.apply(lambda x: fr"${x['c']:.0f}$",axis=1)
        df[r"$b_2$"]=df.apply(lambda x: fr"${x['d']:.0f}$",axis=1)
        df[r"$c$"]=df.apply(lambda x: fr"${x['e']:.0f}$",axis=1)

    # rename the columns
    string = df[[r"$a_1$",r"$a_2$",r"$b_1$",r"$b_2$",r"$c$"]]
    
    # make TeX table
    string = string.T.reset_index().to_latex(escape=False,index=False)

    # layout
    string = string.replace(" spots"," FR")
    string = string.replace("llllll","lccccc")
    string = string.replace("midrule","hline")
    string = string.replace("toprule","hline")
    string = string.replace("bottomrule","hline")

    # write to file
    path = "results/fit_parameters.tex"
    print("Write LaTeX table to file: ", path)
    with open(path,"w") as f:
        f.write(string)