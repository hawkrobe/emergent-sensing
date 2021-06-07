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

spinners = []
time_spinning = []
firsts = []
ns = []
perfs = []

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

for game in os.listdir(in_dir):
    if game[-4:] != '.csv':
        continue

    game_tag = game.split('_')[3]
    
    data = pd.io.parsers.read_csv(in_dir + game)
    filter_spinning(data)
    wait_data = pd.io.parsers.read_csv(wait_dir + wait_locs[game_tag])
    players = set(wait_data['pid'])
    n = len(players)
    for p in players:
        ns += [n]
        sub = data[data['pid'] == p]
        sub_wait = wait_data[wait_data['pid'] == p]
        if len(sub) > 0:
            t = sum(sub['actually_spinning'])
            time_spinning += [t / float(len(sub)) / 8.0]
        else:
            t = np.nan
            time_spinning += [np.nan]
        if sum(sub_wait['spinning']) + sum(sub['actually_spinning']) > 0:
            spinners += [1]
        else:
            spinners += [0]
        if sum(sub_wait['spinning']) > 0:
            firsts += [np.argmax(sub_wait['spinning']) / 8.0]
        else:
            if sum(sub['actually_spinning']) > 0:
                firsts += [np.argmax(sub['actually_spinning']) / 8.0]
            else:
                firsts += [np.nan]
        if len(sub) > 0:
            points = list(sub['total_points'])
            perfs += [(points[-1] - points[0])/float(len(sub))*2880/1.25]
        else:
            perfs += [np.nan]
    
df = pd.DataFrame(dict(n = ns,
                       spinner = spinners,
                       first = firsts,
                       time = time_spinning,
                       perf = perfs))

########  proportion good copies #########

x = df['n']
y = df['first']

x = sm.add_constant(x)
model = sm.OLS(y,x)
results = model.fit()
print results.summary()

df['nn'] = df['n'] + np.random.randn(len(df))*0.1

plt.rcParams.update(pd.tools.plotting.mpl_stylesheet)

fig, ax = plt.subplots()
ax.plot(df['time'], df['perf'], marker='o', linestyle='', ms = 20)
plt.xlabel('Time Spent Spinning (Seconds)', fontsize=50)
plt.ylabel('Individual Score', fontsize=50)
fig = plt.gcf()
fig.set_size_inches(18.5,10.5)
fig.savefig('../../plots/time-spinning-perf.png',dpi=100)

fig, ax = plt.subplots()
ax.plot(df['nn'], df['time'], marker='o', linestyle='', ms = 10)
plt.xlabel('Number of Players', fontsize=20)
plt.ylabel('Time Spent Spinning (Seconds)', fontsize=20)
fig = plt.gcf()
fig.set_size_inches(18.5,10.5)
fig.savefig('../../plots/num-players-time-spinning.png',dpi=100)

fig, ax = plt.subplots()
ax.plot(df['nn'], np.log(df['first']), marker='o', linestyle='', ms = 10)
plt.xlabel('Number of Players', fontsize=20)
plt.ylabel('Log First Time Spinning Observed (Seconds)', fontsize=20)
fig = plt.gcf()
fig.set_size_inches(18.5,10.5)
fig.savefig('../../plots/num-players-first-time-spin.png',dpi=100)



x = []
y = []
for n in set(df['n']):
    sub = df[df['n'] == n]
    x += [n]
    y += [np.mean(sub['spinner'])]
