
import pandas as pd
import numpy as np
import scipy 
import os, sys
import matplotlib.pyplot as plt
import pylab
import matplotlib as mpl
import seaborn as sns

import analysis_utils

sys.path.append('../utils/')
from game_utils import *

# in_dirs = {'data':'../../goal-inference-attention-simulations-processed-1en01/'}
# synthetic_dir = '../../synthetic-goal-inference-attention-simulations-processed-1en01/'
# subset = '1en01'

in_dirs = {'data':'../../parset-simulations/'}
synthetic_dir = '../../parset-simulations/'
subset = '1en01'

#in_dirs = {'data':'../../social-heuristic-simulations-processed-1en01/'}
#synthetic_dir = '../../synthetic-social-heuristic-simulations-processed-1en01/'
#subset = '1en01'


# in_dirs = {'data':'../../new-processed-processed-1en01/'}
# synthetic_dir = '../../new-synthetic-processed-1en01/'
# #synthetic_dir = '../../new-synthetic-score-matched-processed-1en01/'
# subset = '1en01'

# in_dirs = {'data':'../../new-processed-2en01/'}
# synthetic_dir = '../../synthetic-2en01-processed-2en01/'
# subset = '2en01'

# in_dirs = {'data':'../../naive-goal-inference-simulations-processed-1en01/'}
# # synthetic_dir = '../../synthetic-noisy-goal-sharing-simulations-processed-1en01/'
# synthetic_dir = '../../new-synthetic-processed/'
# subset = '1en01'

start = 1440

reference_dir = in_dirs['data']

models = []
games = []
ns = []
values = []
scores = []
sources = []

def get_value(sub):
    ignore_state = lambda sub, i: sub.iloc[i]['spinning']
    this_state = lambda sub, i: sub.iloc[i]['ave_dist_others'] < sub.iloc[i]['dist_to_mean_others']
    next_state = lambda sub, i: sub.iloc[i]['copying_spinning']
    return analysis_utils.get_value(sub, ignore_state, this_state, next_state)

def get_while_value(sub):
    start_index = 5
    lookback = 3
    initial_condition = lambda sub, i: ~sub.iloc[i-1]['spinning'] and ~sub.iloc[i-1]['other_spinning'] and ~sub.iloc[i]['spinning'] and sub.iloc[i]['other_spinning'] and sub.iloc[i]['bg_val'] < 1.0
    while_condition = lambda sub, i: ~sub.iloc[i-(lookback+1)]['facing_spinning'] and sub.iloc[i-(lookback+1)]['bg_val'] < 1.0
    final_condition = lambda sub, i: sub.iloc[(i-lookback):(i+1)]['facing_spinning'].all() and (~sub.iloc[(i-lookback):(i+1)]['spinning']).all() and (sub.iloc[(i-lookback):(i+1)]['bg_val'] < 1.0).all()
    return analysis_utils.get_while_value(sub, initial_condition, while_condition, final_condition, start_index)

for model in in_dirs:

    in_dir = in_dirs[model]

    for game in os.listdir(reference_dir):
        if game[-4:] != '.csv':
            continue
        if game.split('_')[-2].split('-')[1] != subset:
            continue    

        data = pd.io.parsers.read_csv(in_dir + game)
        syn_data = pd.io.parsers.read_csv(synthetic_dir + game)
        players = list(set(data[data['tick'] == start]['pid'].dropna()))
        syn_players = list(set(syn_data[syn_data['tick'] == start]['pid'].dropna()))
        assert len(players) == len(syn_players)
        #assert len(data) == len(syn_data)
        n = len(players)

#        if n != 2 and n != 3:
#            continue
        if n == 6:
             n = 5#continue

        mean_score = np.mean(data[data['tick'] >= start]['bg_val'])

        #if mean_score < 0.75:
        #    continue

        print game, n, mean_score
        
        vals_p = []
        vals_q = []
        for i,p in enumerate(players):
            sub_p = data[data['pid'] == p]
            if len(sub_p) < start:
                continue
            sub_p = sub_p.iloc[start:].copy()
            sub_syn = syn_data[syn_data['pid'] == syn_players[i]].iloc[start:].copy()
            
            #if np.mean(sub_p['spinning']) == 0 or np.mean(sub_p['velocity']>3) == 0 :
            #    continue

            #if np.mean(sub_p['bg_val']) < 0.75 or np.mean(sub_syn['bg_val']) < 0.75:
            #    continue
            
            # val_p = np.mean(sub_p[
            #     np.array(sub_p['ave_dist_others'] < sub_p['dist_to_mean_others'],dtype=bool)
            #     &np.array(sub_p['other_spinning'],dtype=bool)]['facing'])
            # val_q = np.mean(sub_syn[
            #     np.array(sub_syn['ave_dist_others'] < sub_syn['dist_to_mean_others'],dtype=bool)
            #     &np.array(sub_syn['other_spinning'],dtype=bool)]['facing'])

            #val_p = get_while_value(sub_p)
            #val_q = get_while_value(sub_syn)
            
            val_p = np.mean(sub_p['bg_val'])
            val_q = np.mean(sub_p['bg_val'])#np.mean(sub_syn['spinning'])
            
            values += [val_p] + [val_q]
            ns += [n] + [n]
            models += [model] + [model]
            games += [game] + [game]
            scores += [np.mean(sub_p['bg_val'])] + [np.mean(sub_syn['bg_val'])]
            sources += ['data'] + ['syn']
            
data = pd.DataFrame({'model':models,'game':games,'score':scores,'n_players':ns,'value':values,'from':sources})

sns.set(font = 'serif', context = 'poster', style = 'white')
sns.despine()

g = sns.factorplot('n_players', 'value', markers = ['o', 's'], linestyles = ['-','--'], data = data, kind='point', dodge = 0.15, x_order = sorted(set(data['n_players'])), col = 'model', hue = 'from')

#g = sns.factorplot('from', 'value', markers = ['o', 's'], linestyles = ['-','--'], data = data, kind='point', dodge = 0.15, x_order = sorted(set(data['n_players'])), col = 'model')


#plt.plot([0, 7], [0, 0], 'k-', lw=2)

fig = plt.gcf()

fig.savefig('../../plots/values.pdf')

