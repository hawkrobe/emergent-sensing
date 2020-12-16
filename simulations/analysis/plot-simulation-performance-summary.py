import pandas as pd
import numpy as np
import os, sys

import matplotlib
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib.font_manager import FontProperties

#from parse import *


data_dir = '../../predictions-full-background/'

games = os.listdir(data_dir)


noises = []
n_players = []
scores = []
for game in games:
    if game[-4:] != '.csv':
        continue
    df = pd.read_csv(data_dir + game)
    pars = game.split('-')
    noises += [pars[1]]
    n_players += [pars[2]]
    scores += [df['bg_val'].mean()]

data = pd.DataFrame({'Noise Level':noises,'n_players':n_players,'score':scores})

data["Noise Level"].replace({'1en01':'Low', '2en01':'Medium'}, inplace=True)

# plt.rcParams.update(pd.tools.plotting.mpl_stylesheet)

# fig, ax = plt.subplots()
# ax.margins(0.05)

sns.set(font = "serif", context = "poster", style = "white")
sns.despine()

sns.factorplot("n_players", "score", hue = "Noise Level", data = data)#, linestyles = ["-","--"], data = data, kind="point", dodge = 0.15, order = [1,2,3,4,5])

plt.xlabel('Number of Players')#, fontsize=50)
plt.ylabel('Mean Score')#, fontsize=50)
# ax.tick_params(axis='x', labelsize=30)
# ax.tick_params(axis='y', labelsize=30)

fig = plt.gcf()
#fig.set_size_inches(18.5,10.5)
fig.savefig('../../plots/simulated-performance-summary.pdf')#,dpi=100)
    
#plt.show()

