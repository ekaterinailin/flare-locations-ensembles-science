# Flaring Latitudes in Ensembles of Low Mass Stars

*Ilin et al. (accepted to MNRAS)*

The contents of this repository can be divided in three parts:

- a preparatory part that can be run prior to producing synthetic flare light curves and waiting time distributions at scale,
- instructions on how to produce synthetic data at scale
- scripts that analyse and summarize the synthetic data

Scripts that produce figures and tables to appear in Ilin et al. (2023) are noted in the name of the script.

**If you just want the data: Simulation outputs, as well as Tables 2 and 3 can be found on [Zenodo](https://zenodo.org/record/7996929).**

## Scripts that can be run prior to generating synthetic data at scale

Scripts 01, 03, 05, 06 can be run prior to running simulations.

- Script 01 explores the night length distribution for different active latitudes at varying inclinations.
- Script 03 produces a **minimal example** of fleck usage with flares.
- Script 05 derives the empirical equivalent duration to amplitude to duration conversion based flaring ultracool dwarf systems observed with TESS.
- Script 06 produces model illustrations for the paper.

## How to generate synthetic training data and use them to find properties that predict active latitude

#### Generate training data

Open `09_make_script_for_generate_training_data.py` and check the parameters defined in the script. Don't change anything unless you know what you are doing!

Then run `python 09_make_script_for_generate_training_data.py <number of light curves> <batches>`

This will generate a bash script named `09_script_generate_data.sh` that calls `09_generate_training_data.py` a `<batches>` times to give you the desired total `<number of light curves>`. It will also store the input parameters from the script in a file called `results/overview_synthetic_data.csv`.

Additionally, `09_script_generate_data.sh` will also call `09_generate_training_data.py` a `<batches>` times to give you the desired total `<number of light curves>` / 10, which will serve as a validation data set.

However, we don't store the actual light curves, but only the flares we find in the data set. These flares appear modulated in brightness due to their latitude on the rotating star, which we hope to retrieve from the ensemble analysis.

In summary:

Input: `python 09_make_script_for_generate_training_data.py <number of light curves> <batches>`

Output:

- `09_script_generate_data.sh`
- two new rows in `results/overview_synthetic_data.csv`

Input: `bash 09_script_generate_data.sh`

Output:

- `results/<timestamp1>_flares_train.csv`
- `results/<timestamp1>_flares_validate.csv`

#### Get summary statistics

Now that we have our training and validation data sets, let's compute summary statistics. We do this because we don't want to use the information about individual flares, because they are randomly generated from a power law distribution, but statistics that give a single number for each light curve or even ensembles of light curves with similar active latitude, e.g., the total number of flares or the waiting times between flares.

Call `python 10_make_script_for_get_aggregate_parameters.py <training/validation data set> <number of splits>`


Input:

- `python 10_make_script_for_get_aggregate_parameters.py <training data set> <number of splits>`
- `python 10_make_script_for_get_aggregate_parameters.py <validation data set> <number of splits>`

Output:

- `11_applyscript_<timestamp2>_<timestamp1>_flares_train.sh`
- `12_merge_<timestamp2>_<timestamp1>_flares_train.sh`
- `11_applyscript_<timestamp2>_<timestamp1>_flares_validate.sh`
- `12_merge_<timestamp2>_<timestamp1>_flares_validate.sh`

If you are doing aggregate statistics for ensembles of light curves, take care not to split the training and validation data into too small chunks, in particular the validation set.  Divide `<total number of LCs> / <number of splits> / 200` to get the number of lc per ensemble. It should be at least 200 to effectively marginalize over inclinations, and get a decently narrow active latitude width. 

In the paper, we ran theses scripts for a number of different configurations (number of active regions, flare rates, active latitude widths). **You can find the outputs from the above procedure on [Zenodo](https://zenodo.org/record/7996929).**


## Scripts that can be run after the synthetic data have been created and processed

Scripts 13-18 can only be run after the synthetic data have been processed.

- Script 13 fits a polynomial expression to the data, and writes out best-fit parameters and **covariance matrices** to the ``results/`` folder.
- Script 14 plots the residuals of the fits done in Script 13 on a validation data set that was not used in 13.
- Script 15 just convert the fit parameters .csv table to a LaTeX document (Table 2).
- Script 16 shows the results for varying active latitude width.
- Script 17 shows the results for varying power law exponent alpha.
- Script 18 produces a figure that shows the parameter range covered by the mean and standard deviation of waiting time distributions.
- Script 19 produces Table 3 in the paper
- Script 20 produces Figure 9 that illustrates the flaring latitudes derived from the G dwarf flare sample in [Okamoto et al. (2021)](https://ui.adsabs.harvard.edu/abs/2021ApJ...906...72O/abstract), and convert Table 3 to LaTeX.

**Machine readable versions of Tables 2 and 3 can be found on [Zenodo](https://zenodo.org/record/7996929).**
