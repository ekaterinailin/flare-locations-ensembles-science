

### How to generate synthetic training data and use them to find properties that predict active latitude

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



