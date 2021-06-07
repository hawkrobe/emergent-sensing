
from multiprocessing import Pool

import pandas as pd
import os
from model_based_analysis_tools import *

base_dir = '../../'
in_dirs = {
    'data':'new-processed-model-processed-1en01',
    'synthetic-data':'new-synthetic-model-processed-1en01',
    'score-matched-data':'new-synthetic-score-matched-model-processed-1en01'}
subset = '1en01'

data_dirs = {
    'data':'new-processed',
    'synthetic-data':'new-synthetic-processed',
    'score-matched-data':'new-synthetic-score-matched-processed'}

out_dir = base_dir + 'model-processed-results/'
try:
    os.makedirs(out_dir)
except:
    pass

def run(model):
    
    in_dir = in_dirs[model]
    data_dir = data_dirs[model]

    results = {}
    
    for game in os.listdir(base_dir + in_dir):
        
        if game[-4:] != '.out':
            continue
        if game.split('_')[-2].split('-')[1] != subset:
            continue    
        
        with open(base_dir + in_dir + '/' + game) as f:
            data = pickle.load(f)
        
        results[game] = get_all_divergences(data)
        
        with open(out_dir + model + '.out', 'w') as h:
            pickle.dump(results, h)

p = Pool(len(in_dirs))
p.map(run, in_dirs)
