import pandas as pd
import numpy as np
from scipy import stats
import os, sys
import matplotlib.pyplot as plt
import pylab
import matplotlib as mpl

sys.path.append("../utils/")
from utils import *

in_dir = '../../processed/'
subset = '1en01'

scores = []
states = []

for game in os.listdir(in_dir):
    if game[-4:] != '.csv':
        continue

    if game.split('_')[-2].split('-')[1] != subset:
        continue    
    
    data = pd.io.parsers.read_csv(in_dir + game)
    players = set(data['pid'])
    n = len(players)
    if n < 2 or n > 5:
        continue
    for p in players:
        sub = data[data['pid'] == p]
        for j in list(sub.index):
            scores += [sub['bg_val'][j]]
            states += [sub['state'][j]]

df = pd.DataFrame(dict(score = scores,
                       state = states))

state_names = ['exploring', 'exploiting', 'copying']
x = []
y = dict([(s,[]) for s in state_names])


print
print 'states as a function of score'
for val in sorted(list(set(df['score']))):
    states = df[df['score'] == val]['state']
    x += [val]
    for s in state_names:
        y[s] += [np.mean(states == s)]

fig, ax = plt.subplots()
#plt.rcParams.update(pd.tools.plotting.mpl_stylesheet)
#ax.set_color_cycle(['b', 'g', 'y'])
mpl.rc('font',family='Times New Roman')

from seaborn import color_palette

with color_palette("colorblind"):
    for s in state_names:
        plt.plot(x,y[s],label = s, lw = 10)
mpl.rc('font',family='Times New Roman')
plt.xlabel('Score', fontsize=50)
plt.ylabel('Probability', fontsize=50)
plt.xlim((0,1))
plt.ylim((0,1))
pylab.legend(loc='upper left')
plt.setp(plt.gca().get_legend().get_texts(), fontsize='40')
ax.tick_params(axis='x', labelsize=40)
ax.tick_params(axis='y', labelsize=40)


fig = plt.gcf()
fig.set_size_inches(12.5,12.5)
fig.savefig('../../plots/states.pdf')#,dpi=100)

#plt.show()
