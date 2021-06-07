import pandas as pd
import numpy as np
from scipy import stats
import os, sys
import matplotlib.pyplot as plt
import pylab

sys.path.append("../utils/")
from utils import *

from parse import *

in_dir = '../../processed/'

times = []
states = []

for game in os.listdir(in_dir):
    if game[-4:] != '.csv':
        continue
    
    data = pd.io.parsers.read_csv(in_dir + game)
    players = set(data['pid'])
    n = len(players)
    if n != 5:
        continue
    for p in players:
        sub = data[data['pid'] == p]
        for j in list(sub.index):
            if sub['state'][j] != 'exploiting' and sub['have_been_nearby'][j]:
                times += [int(np.log(sub['since_nearby'][j] + 1))]
                states += [sub['state'][j]]

df = pd.DataFrame(dict(time = times,
                       state = states))

state_names = ['exploring', 'copying']
x = []
y = dict([(s,[]) for s in state_names])


print
print 'states as a function of time'
for val in sorted(list(set(df['time']))):
    states = df[df['time'] == val]['state']
    x += [val]
    for s in state_names:
        y[s] += [np.mean(states == s)]

plt.figure()        
plt.rcParams.update(pd.tools.plotting.mpl_stylesheet)
for s in state_names:
    plt.plot(x,y[s], label = s)
plt.xlabel('Log Time Since Last with Group', fontsize=24)
plt.ylabel('Probability Given Not Exploiting', fontsize=24)
pylab.legend(loc='upper left')
plt.setp(plt.gca().get_legend().get_texts(), fontsize='20')
plt.show()
