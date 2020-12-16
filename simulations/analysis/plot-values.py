import pandas as pd
import numpy as np
import scipy 
import os, sys
import matplotlib.pyplot as plt
import pylab
import matplotlib as mpl
import seaborn as sns

sys.path.append("../utils/")
from utils import *
from stats import *
from parse import *

#in_dirs = {'data':'../../processed/','social':'../../simulations/','nonsocial':'../../simulations-nonsocial/'}
in_dirs = {'data':'../../processed-waits-all/'}
subset = '1en01'

models = []
ns = []
scores = []

for model in in_dirs:

    in_dir = in_dirs[model]

    for game in os.listdir(in_dir):
        if game[-4:] != '.csv':
            continue

        if game.split('_')[-2].split('-')[1] != subset:
            continue    

        data = pd.io.parsers.read_csv(in_dir + game)

        if max(data['tick']) < 200:
            continue
        
        players = set(data[data['tick'] == max(data['tick'])]['pid'])
        n = len(players)
        for p in players:
            sub_p = data[data['pid'] == p]
            scores += [np.mean(sub_p['velocity'])]
            ns += [n]
            models += [model]

            
data = pd.DataFrame({'model':models,'n_players':ns,'score':scores})
        
sns.set(font = "serif", context = "poster", style = "white")
sns.despine()

g = sns.factorplot("n_players", "score", markers = ["o", "s"], linestyles = ["-","--"], data = data, kind="point", dodge = 0.15, x_order = sorted(set(data['n_players'])), col = 'model')

#g.set(ylim=(0.5, 0.9))

# fig,ax = plt.subplots()

# ax.scatter(ns, scores, s = 100,
#            facecolors='none', edgecolors='black', lw=3)
# ax.set_title(str(n) + ' Players', fontsize=40)
# ax.set_ylim([0, 1])
# ax.tick_params(axis='x', labelsize=30)
# ax.tick_params(axis='y', labelsize=30)

# x = sub['ggc']/sub['gc']
# y = sub['perf']
# slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x,y)    
# x_pred = np.linspace(0,1)
# y_pred = intercept + x_pred*slope
# ax.plot(x_pred, y_pred, c = 'black')

fig = plt.gcf()

#fig.set_size_inches(20,12)
fig.savefig('../../plots/scores.pdf')

