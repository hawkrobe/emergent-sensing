# Emergent collective sensing in human groups

* `experiments` contains the code to reproduce all of the behavioral experiments. 
* `data` contains the raw data from these experiments. 
* `analyses` contains R notebooks to produce all figures and statistics reported in the paper. run from the top level directory after installing necessary R libraries
* `simulations` contains the code to reproduce the simulations with different computational models.

# Raw data

Raw data files for Exp. 1 and Exp. 3 are too large to be checked into this repository. 

To reproduce full Exp. 1 preprocessing pipeline, unzip the raw tick-by-tick data [stored here](https://emergent-sensing.s3.us-east-2.amazonaws.com/exp1_raw_games.zip) and place it in `/data/experiment1/`.

To reproduce full Exp. 3 preprocessing pipeline, unzip the state-annotated data [stored here](https://emergent-sensing.s3.us-east-2.amazonaws.com/exp3_processed_data.zip) and place it in `/data/experiment3`.

# Supplementary videos

Reconstructed videos in .mp4 format are available for:

* [Experiment 1 (model simulations)](https://emergent-sensing.s3.us-east-2.amazonaws.com/simulations.zip)
* [Experiment 1 (empirical)](https://emergent-sensing.s3.us-east-2.amazonaws.com/exp1.zip)
* [Experiment 2 (empirical)](https://emergent-sensing.s3.us-east-2.amazonaws.com/exp2.zip)
* [Experiment 3 (empirical)](https://emergent-sensing.s3.us-east-2.amazonaws.com/exp3.zip)

# Errata 

* The interaction between group size and noise in Experiment 3 is reported as "t(81.6) = 2.3, p = 0.02, b = 0.43, 95% CI = [−0.78, −0.07]". The signs of b and t were omitted: the correct values are b = −0.43, t(81.6) = −2.3. 

* The selective-copying interaction in Experiment 2 is reported as "t(25.5) = 2.5, p = 0.02, b = 47.6, 95% CI = [7.5, 85.4]". The coefficient should read as b = 47.3. We discovered that the value 47.6 comes from an earlier version of the analysis with an off-by-one error where the goal-manipulation windows ended at ticks 159 and 399 rather than 160 and 400. This changed the assignment of a single click event and moved the estimate from 47.56 to 47.31. The reported t, degrees of freedom, p-value, and confidence interval all correspond to the current code and were unaffected.
