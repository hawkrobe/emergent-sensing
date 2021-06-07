import pandas as pd
import numpy as np
import scipy 
import os, sys
import matplotlib.pyplot as plt
import pylab

sys.path.append("../utils/")
from utils import *
from stats import *
from parse import *

in_dir = '../../processed/'
wait_dir = '../../processed-waits-all/'

threshold = 10*8 # x seconds * 8 ticks/second

def filter_spinning(data):
    data['actually_spinning'] = False
    for p in set(data['pid']):
        sub = data[data['pid'] == p]
        fst = sub.index[(sub['spinning'] & ~ sub['spinning'].shift(1).fillna(False)) == 1]
        lst = sub.index[(sub['spinning'] & ~ sub['spinning'].shift(-1).fillna(False)) == 1]
        pr = [(i, j) for i, j in zip(fst, lst) if j >= i + 8]
        for i,j in pr:
            data.loc[i:j]['actually_spinning'] = True

wait_locs = {}
for game in os.listdir(wait_dir):
    if game[-4:] != '.csv':
        continue
    game_tag = game.split('_')[3]
    wait_locs[game_tag] = game

all_games = dict([(n+1,[]) for n in range(5)])
    
for game in os.listdir(in_dir):
    if game[-4:] != '.csv':
        continue

    game_tag = game.split('_')[3]

    wait_data = pd.io.parsers.read_csv(wait_dir + wait_locs[game_tag])
    wait_players = set(wait_data['pid'])
    n_wait = len(wait_players)
    
    data = pd.io.parsers.read_csv(in_dir + game)
    game_players = set(data['pid'])
    n_game = len(game_players)
    
    if (n_wait == 1 and n_game == 1) or (n_wait == n_game and n_game > 1) and n_game < 6:
        filter_spinning(data)
        all_games[n_game] += [data]
    else:
        print n_wait, n_game

spinners = dict([(n,[]) for n in all_games])
perfs = dict([(n,[]) for n in all_games])

for n in all_games:
    
    for data in all_games[n]:

        players = set(data['pid'])

        for p in players:
            sub = data[data['pid'] == p]
            t = sum(sub['actually_spinning'])
            if t > threshold:
                spinners[n] += [1]
            else:
                spinners[n] += [0]
            points = list(sub['total_points'])
            perfs[n] += [(points[-1] - points[0])/float(len(sub))*2880/1.25]
        

for n in spinners:
    print n, np.mean(spinners[n]), 2*np.std(spinners[n])/np.sqrt(len(spinners[n]))

x = [n for j in range(len(spinners[n])) for n in spinners]
y = [s for s in spinners[n] for n in spinners]
x = sm.add_constant(x)
model = sm.OLS(y,x)
results = model.fit()
print results.summary()

# df['nn'] = df['n'] + np.random.randn(len(df))*0.1

# plt.rcParams.update(pd.tools.plotting.mpl_stylesheet)

# fig, ax = plt.subplots()
# ax.plot(df['time'], df['perf'], marker='o', linestyle='', ms = 20)
# plt.xlabel('Time Spent Spinning (Seconds)', fontsize=50)
# plt.ylabel('Individual Score', fontsize=50)
# fig = plt.gcf()
# fig.set_size_inches(18.5,10.5)
# fig.savefig('../../plots/time-spinning-perf.png',dpi=100)

