import pandas as pd
import numpy as np
import os, sys

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib.font_manager import FontProperties

#from parse import *

sys.path.append("../utils/")
from game_utils import *

data_dir = '../../out/'
games = []
games += get_games(data_dir, 'experiment')
#games += ['tmp']

data = get_data(data_dir, games)
#data = data[data['n_players'] < 6]
#data = data[data['score'] > 0.7]

data.rename(columns={'difficulty': 'Noise Level'}, inplace=True)
data["Noise Level"].replace({'1en01':'Low', '2en01':'Medium'}, inplace=True)

# plt.rcParams.update(pd.tools.plotting.mpl_stylesheet)

# fig, ax = plt.subplots()
# ax.margins(0.05)

sns.set(font = "serif", context = "poster", style = "white")
sns.despine()

sns.factorplot("n_players", "score", hue = "Noise Level", markers = ["o", "s"], linestyles = ["-","--"], data = data, kind="point", dodge = 0.15, units = "game", order = [1,2,3,4,5,6])

plt.xlabel('Number of Players')#, fontsize=50)
plt.ylabel('Mean Score')#, fontsize=50)
# ax.tick_params(axis='x', labelsize=30)
# ax.tick_params(axis='y', labelsize=30)

fig = plt.gcf()
#fig.set_size_inches(18.5,10.5)
fig.savefig('../../plots/performance-summary.pdf')#,dpi=100)
    
#plt.show()

