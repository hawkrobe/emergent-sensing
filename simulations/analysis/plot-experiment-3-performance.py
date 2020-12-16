import pandas as pd
import numpy as np
import os, sys

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib.font_manager import FontProperties

#from parse import *

sys.path.append("../utils/")
from game_utils import *

data_dir = '../../out/'
games = []
games += get_games(data_dir, 'experiment-exploratory-2016')
games += get_games(data_dir, 'experiment-confirmatory-2016')
#games += get_games(data_dir, 'demo-exploratory')
#games += ['tmp']

data = get_data(data_dir, games)
#data = data[data['n_players'] < 6]
#data = data[data['score'] > 0.7]

game_df = data.groupby('game').mean()
game_df['game'] = game_df.index


game_df_max = []

comps = {}
reps = 10000
for n in range(1,7):
    comps[n] = {}
    for noise in ['0','1','2','3']:
        comps[n][noise] = 0
        for i in range(reps):
            comp = data.loc[(data['n_players'] == 1) & (data['noise'] == noise), 'score']
            comps[n][noise] += np.max(np.random.choice(comp, size = n))
        comps[n][noise] /= float(reps)

for g in set(data['game']):
    sub = data.loc[data['game'] == g]
    n = sub.iloc[0]['n_players']
    noise = sub.iloc[0]['noise']
    score = max(sub['score']) - comps[n][noise]
    game_df_max += [[g, n, score]]

game_df_max = pd.DataFrame(game_df_max)
game_df_max.columns = ['game','n_players','score']

# plt.rcParams.update(pd.tools.plotting.mpl_stylesheet)

# fig, ax = plt.subplots()
# ax.margins(0.05)

sns.set(font = "serif", context = "poster", style = "white")
sns.despine()

sns.pointplot("n_players", "score", data = data, kind="point", units = "game")#, order = [1,2,3,4,5,6])

plt.xlabel('Number of Players')#, fontsize=50)
plt.ylabel('Mean Score')#, fontsize=50)
# ax.tick_params(axis='x', labelsize=30)
# ax.tick_params(axis='y', labelsize=30)

fig = plt.gcf()
#fig.set_size_inches(18.5,10.5)
fig.savefig('../../../fish-plots/performance-summary-experiment-2.pdf')#,dpi=100)

#plt.show()

plt.close()


plt.scatter(data['n_players']+np.random.normal(size=len(data))*0.1,data['score'])
plt.xlabel('Number of Players')
plt.ylabel('Individual Score')

fig = plt.gcf()
fig.savefig('../../../fish-plots/performance-points.pdf', bbox_inches = 'tight')#,dpi=100)


plt.close()


plt.scatter(game_df['n_players'] + np.random.normal(size=len(game_df))*0.1,game_df['score'])
plt.xlabel('Number of Players')
plt.ylabel('Group Mean Score')

fig = plt.gcf()
fig.savefig('../../../fish-plots/performance-groups.pdf', bbox_inches = 'tight')#,dpi=100)


plt.close()


plt.scatter(game_df_max['n_players'] + np.random.normal(size=len(game_df_max))*0.1,game_df_max['score'])
plt.xlabel('Number of Players')
plt.ylabel('Group Max Score')

fig = plt.gcf()
fig.savefig('../../../fish-plots/performance-max-groups.pdf', bbox_inches = 'tight')#,dpi=100)


plt.close()


plt.scatter(game_df['assigned_n_players']+np.random.normal(size=len(game_df))*0.1, game_df['n_players']+np.random.normal(size=len(game_df))*0.1)
plt.xlabel('Assigned Number of Players')
plt.ylabel('Actual Number of Players')

fig = plt.gcf()
fig.savefig('../../../fish-plots/player-player.pdf', bbox_inches = 'tight')#,dpi=100)

plt.close()


aggs = [('Mean',np.mean), 
        ('Median', np.median), 
        ('Max',max), 
        ('Min',min), 
        ('25th Percentile',lambda x: np.percentile(x, 25)), 
        ('75th Percentile',lambda x: np.percentile(x, 75))]

for data_source in [('Individual',data), ('Group',game_df)]: 


    for agg in aggs:

        agg_name, agg_f = agg

        sns.set(font = "serif", context = "poster", style = "white")
        sns.despine()

        sns.pointplot("n_players", "score", data = data_source[1], kind="point", units = "game", order = [1,2,3,4,5,6], estimator = agg_f)

        plt.xlabel('Number of Players')#, fontsize=50)
        plt.ylabel(agg_name + ' ' + data_source[0] + ' Score')#, fontsize=50)
        # ax.tick_params(axis='x', labelsize=30)
        # ax.tick_params(axis='y', labelsize=30)

        fig = plt.gcf()
        #fig.set_size_inches(18.5,10.5)
        fig.savefig('../../../fish-plots/performance-summary-' + data_source[0] + '-' + '_'.join(agg_name.split(' ')) + '.pdf')#,dpi=100)

        #plt.show()

        plt.close()


import statsmodels.formula.api as smf


noises = []
game_ids = sorted(list(set(data['game'])))
for g in game_ids:
    noises += [(data.loc[data['game'] == g,'noise']).iloc[0]]
    
game_df['noise'] = noises

mod = smf.ols(formula='score ~ n_players + noise + wait', data=game_df)
res = mod.fit()
print(res.summary())

mod = smf.quantreg('score ~ n_players + noise + wait', game_df)
res = mod.fit(q=0.25)
print(res.summary())

mod = smf.quantreg('score ~ n_players + noise + wait', game_df)
res = mod.fit(q=0.5)
print(res.summary())

