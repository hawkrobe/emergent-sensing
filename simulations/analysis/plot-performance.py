import pandas as pd
import numpy as np
import os, sys
import matplotlib.pyplot as plt

from parse import *

sys.path.append("../utils/")
from utils import *

subset_noise = False
noise_level = '1-2en01'

subset_difficulty = True
diff_level = '1en01'

data_dir = '../../out/'
games = []
games += get_games(data_dir, 'experiment')
#games += ['tmp']

data = get_data(data_dir, games)
#data = data[data['n_players'] < 6]
#data = data[data['score'] > 0.7]

if subset_noise:
    data = data[data['noise'] == noise_level]
if subset_difficulty:
    data = data[data['difficulty'] == diff_level]

def get_shape(i):
    shapes = ['$a$',
              '$b$',
              '$c$',
              '$d$',
              '$e$',
              '$f$',
              '$g$',
              '$h$',
              '$i$',
              '$j$',
              '$k$',
              '$l$',
              '$m$',
              '$n$',
              '$o$',
              '$p$',
              '$q$',
              '$r$',
              '$s$',
              '$t$',
              '$u$',
              '$v$',
              '$w$',
              '$x$',
              '$y$',
              '$z$',
        (4,0,0), (3,0,0), (4,0,45), (0,3,0), (3,0,90),
              (3,0,180), (3,0,270),
              (5,0,0), (6,0,0), (6,0,90), (4,2,0), (4,3,0),
              (5,2,0), (5,3,0),
              "d", "*", "$a$"]
    return shapes[i % len(shapes)]

    
plt.rcParams.update(pd.tools.plotting.mpl_stylesheet)

fig, ax = plt.subplots()
ax.margins(0.05)

colors = ['#348ABD',  '#467821', '#E4C334', '#A60628']


counts = dict([(n,0) for n in set(data['n_players'])])

data['nn_players'] = data['n_players'] + np.random.randn(len(data))*0.1


i = 0
for noise in set(data['noise']):
    if not subset_noise or noise == noise_level:        
        noise_sub = data[data['noise'] == noise]
        x = sorted(set(noise_sub['n_players']))
        y = []
        for n in x:
            y += [np.mean(noise_sub[noise_sub['n_players'] == n]['score'])]
        ax.plot(x, y, c = colors[i], lw = 10, alpha = 0.5)
    i += 1

i = 0
j = 0
for noise in set(data['noise']):
    if not subset_noise or noise == noise_level:        
        noise_sub = data[data['noise'] == noise]
        for game in set(noise_sub['game']):
            sub = noise_sub[noise_sub['game'] == game]
            n = list(set(sub['n_players']))[0]
            ax.plot(sub['nn_players'], sub['score'], marker='o', linestyle='', ms = 20, c = colors[i])                    
            ax.plot(sub['nn_players'], sub['score'], marker=get_shape(counts[n]), linestyle='', ms = 10, c = 'black')
            counts[n] += 1
    i += 1

#legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), title = 'Background', numpoints=1)
#legend.get_title().set_fontsize('30')
#plt.setp(plt.gca().get_legend().get_texts(), fontsize='20')

plt.xlabel('Number of Players', fontsize=50)
plt.ylabel('Individual Score', fontsize=50)
ax.tick_params(axis='x', labelsize=30)
ax.tick_params(axis='y', labelsize=30)

fig = plt.gcf()
fig.set_size_inches(18.5,10.5)
if subset_difficulty:
    fig.savefig('../../plots/performance-' + diff_level + '.png',dpi=100)
elif subset_noise:
    fig.savefig('../../plots/performance-' + noise_level + '.png',dpi=100)
else:
    fig.savefig('../../plots/performance-all.png',dpi=100)

    
#plt.show()

