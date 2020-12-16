import pandas as pd
import numpy as np
import scipy 
import os, sys
import matplotlib.pyplot as plt
import pylab
import matplotlib as mpl
import seaborn as sns

# in_dirs = {'data':'../../simulations-processed-1en01/'}
# synthetic_dir = '../../simulations-nonsocial-processed-1en01/'
# subset = '1en01'

in_dirs = {'data':'../../new-processed/'}
synthetic_dir = '../../new-synthetic-processed/'
#synthetic_dir = '../../new-synthetic-score-matched-processed/'
subset = '1en01'

reference_dir = in_dirs['data']

models = []
games = []
ns = []
xs = []
ys = []
zs = []
syns = []
                
for model in in_dirs:

    in_dir = in_dirs[model]

    for game in os.listdir(reference_dir):
        if game[-4:] != '.csv':
            continue
        if game.split('_')[-2].split('-')[1] != subset:
            continue    

        data = pd.io.parsers.read_csv(in_dir + game)
        syn_data = pd.io.parsers.read_csv(synthetic_dir + game)
        players = list(set(data[data['tick'] == 1440]['pid'].dropna()))
        syn_players = list(set(syn_data[syn_data['tick'] == 1440]['pid'].dropna()))
        assert len(players) == len(syn_players)
        assert len(data) == len(syn_data)
        n = len(players)
        vals_p = []
        vals_q = []
        
        if n == 1:
            continue
        
        for i,p in enumerate(players):
            sub_p = data[data['pid'] == p]
            if len(sub_p) < 1440:
                continue
            sub_p = sub_p.iloc[1440:].copy()
            sub_syn = syn_data[syn_data['pid'] == syn_players[i]].iloc[1440:].copy()

            if np.mean(sub_p['bg_val']) < 0.75 or np.mean(sub_syn['bg_val']) < 0.75:
                continue

            print np.mean(sub_p['bg_val']), np.mean(sub_syn['bg_val'])
            
            # sub_p = sub_p.loc[
            #     np.array(sub_p['bg_val'] > 0,dtype=bool)
            # ]
            # sub_syn = sub_syn.loc[
            #     np.array(sub_syn['bg_val'] > 0,dtype=bool)
            # ]
            
            #val_p = list(np.round(sub_p['uncertainty']/2500))
            #val_q = list(np.round(sub_syn['uncertainty']/2500))
            #val_p = list(map(int, sub_p['dist_to_mean_others']/10))
            #val_q = list(map(int, sub_syn['dist_to_mean_others']/10))

            val_p = list(sub_p['bg_val'])
            val_q = list(sub_syn['bg_val'])
            
            xs += val_p + val_q

            val_p = list(sub_p['copying_exploiting'])
            val_q = list(sub_syn['copying_exploiting'])
            
            ys += val_p + val_q

            val_p = list(sub_p['other_spinning'])
            val_q = list(sub_syn['other_spinning'])
            
            zs += val_p + val_q            
            
            syns += ['data']*len(val_p) + ['synthetic']*len(val_q)
            ns += [n]*(len(val_p) + len(val_q))
            models += [model]*(len(val_p) + len(val_q))
            games += [game]*(len(val_p) + len(val_q))
            
data = pd.DataFrame({'model':models,'game':games,'from':syns,'n_players':ns,'x':xs,'y':ys,'z':zs})

# x = []
# y = []
# w = []
# z = []
# for i in range(101):
#     sub = data[(data['x'] < (i+1)/100.0) & (data['x'] > (i-1)/100.0)]
#     val = np.sum(sub[sub['from'] == 'data']['y'])
#     syn = np.sum(sub[sub['from'] == 'synthetic']['y'])
#     x += [i]
#     y += [val - syn]
#     w += [val]
#     z += [syn]

# plt.plot(x,y)
# plt.plot([0, 100], [0, 0], 'k-', lw=2)
# plt.show()

sns.set(font = 'serif', context = 'paper', style = 'white')
sns.despine()

g = sns.factorplot('x', 'y', data = data, kind='point', order = sorted(set(data['x'].dropna())), col = 'n_players', hue = 'from', ci = None)

#plt.plot([0, 7], [0, 0], 'k-', lw=2)

fig = plt.gcf()

fig.savefig('../../plots/values.pdf')

