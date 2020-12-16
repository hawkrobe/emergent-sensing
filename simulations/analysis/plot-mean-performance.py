import pandas as pd
import numpy as np
import os, sys
import matplotlib.pyplot as plt
from scipy import stats

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

data = get_group_data(data_dir, games)
#data = data[data['n_players'] < 6]

if subset_noise:
    data = data[data['noise'] == noise_level]
if subset_difficulty:
    data = data[data['difficulty'] == diff_level]

x = data['n_players']
y = data['score']
slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
print
print 'regression slope:', slope, ', p:',  p_value

    
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

color_cycle = ax._get_lines.color_cycle

colors = [next(color_cycle) for i in range(4)]

data['nn_players'] = data['n_players'] + np.random.randn(len(data))*0.1

i = 0
j = 0
for noise in set(data['noise']):
    if not subset_noise or noise == noise_level:
        noise_sub = data[data['noise'] == noise]
        ax.plot(noise_sub['nn_players'], noise_sub['score'], marker='o', linestyle='', ms = 20, c = colors[i], label = noise)
    i += 1

#legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), title = 'Background', numpoints=1)
#legend.get_title().set_fontsize('30')
#plt.setp(plt.gca().get_legend().get_texts(), fontsize='20')

plt.xlabel('Number of Players', fontsize=35)
plt.ylabel('Individual Score', fontsize=35)

plt.show()

