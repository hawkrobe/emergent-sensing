import pandas as pd
import numpy as np
import scipy 
import os, sys
import matplotlib.pyplot as plt
import pylab
import matplotlib as mpl
import seaborn as sns

sys.path.append('../utils/')
from utils import *
from stats import *
from parse import *

in_dirs = {'data':'../../new-processed/'}
subset = '1en01'

reference_dir = '../../new-processed/'
#synthetic_dir = '../../new-synthetic/'
synthetic_dir = '../../new-synthetic-score-matched/'

models = []
ns = []
vals = []

def pos_dist(data):

    dists = []
    
    players = set(data[data['tick'] == max(data['tick'])]['pid'])
    for p in players:
        sub_p = data[data['pid'] == p].iloc[1440:]
        for q in players:
            if q == p:
                continue
            sub_q = data[data['pid'] == q].iloc[1440:]

            p_pos = np.array([sub_p['x_pos'],sub_p['y_pos']])
            q_pos = np.array([sub_q['x_pos'],sub_q['y_pos']])            
            dists += [np.mean(np.apply_along_axis(np.linalg.norm, 0, list(p_pos - q_pos)))]
            
            #p_pos = np.array(sub_p['spinning'])
            #q_pos = np.array(sub_q['spinning'])
            #dists += [np.mean(map(np.linalg.norm, list(p_pos - q_pos)))]
    
    return np.array(dists)

for model in in_dirs:

    in_dir = in_dirs[model]

    for game in os.listdir(reference_dir):
        if game[-4:] != '.csv':
            continue
        
        if game.split('_')[-2].split('-')[1] != subset:
            continue    

        data = pd.io.parsers.read_csv(in_dir + game)
        dists = pos_dist(data)
        syn_dists = pos_dist(pd.io.parsers.read_csv(synthetic_dir + game))
        
        mean_score = np.mean(data[data['tick'] >= 1440]['bg_val'])
        
        if mean_score < 0.8:
            continue
        
        players = set(data[data['tick'] == max(data['tick'])]['pid'])
        n = len(players)
        vals += list(dists - syn_dists)
        ns += [n]*len(dists)
        models += [model]*len(dists)

data = pd.DataFrame({'model':models,'n_players':ns,'values':vals})

sns.set(font = 'serif', context = 'poster', style = 'white')
sns.despine()

g = sns.factorplot('n_players', 'values', markers = ['o', 's'], linestyles = ['-','--'], data = data, kind='point', dodge = 0.15, x_order = sorted(set(data['n_players'])), col = 'model')

plt.plot([0, 7], [0, 0], 'k-', lw=2)

fig = plt.gcf()

fig.savefig('../../plots/values.pdf')

