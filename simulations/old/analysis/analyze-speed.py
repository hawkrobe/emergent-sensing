import pandas as pd
import numpy as np
from scipy import stats
import os, sys
import matplotlib.pyplot as plt

from parse import *

in_dir = '../../out/'

games = get_games(in_dir, 'experiment')

vels = []
scores = []

for game_id in games:

    data_dir = in_dir + game_id + '/games/'

    inactive = get_inactive(game_id)

    for game in os.listdir(data_dir):
        if game[-4:] != '.csv':
            continue

        data = pd.io.parsers.read_csv(data_dir + game)
        players = set(data['pid'])
        n = len(players)    
        for p in players:
            if p in inactive:
                continue
            sub = data[data['pid'] == p]
            if sum(1-np.isnan(sub['x_pos'])) > 2000:
                sub = sub[(sub['tick'] >= 0)*(sub['tick'] <= 2880)]
                for j in list(sub.index):
                    vels += [sub['velocity'][j]]
                    scores += [sub['bg_val'][j]]

data = pd.DataFrame(dict(velocity = vels,
                       score = scores))

print
print 'score as a function of speed'
for v in set(data['velocity']):
    bs = data[data['velocity'] == v]['score']
    print v, np.mean(bs), np.std(bs), len(bs), 2*np.std(bs)/np.sqrt(len(bs))

x = data['velocity']
y = data['score']
slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

print
print 'regression slope, p:', slope, p_value

x = []
y = []
s = []

print
print 'speed as a function of score'
for b in set(data['score']):
    bs = data[data['score'] == b]['velocity']
    x += [b]
    y += [np.mean(bs)]
    s += [2*np.std(bs)/np.sqrt(len(bs))]

slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

print
print 'regression slope, p:', slope, p_value


plt.rcParams.update(pd.tools.plotting.mpl_stylesheet)
plt.scatter(x,y)
plt.xlabel('Score', fontsize=24)
plt.ylabel('Average Velocity', fontsize=24)
plt.show()
