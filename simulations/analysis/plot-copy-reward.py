import pandas as pd
import numpy as np
import scipy 
import os, sys
import matplotlib.pyplot as plt
import pylab
import matplotlib as mpl

sys.path.append("../utils/")
from utils import *
from stats import *
from parse import *

in_dir = '../../processed-simulations/'
subset = '1en01'

group_good_copy = []
group_performance = []
lengths = []
ns = []

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
    good_copy = 0
    perf = 0
    length = 0
    for p in players:
        sub_p = data[data['pid'] == p]
        sub = sub_p[sub_p['state'] == 'copying']
        good_copy += sum(sub['copying_reward'] > sub['bg_val'])
        points = list(sub_p['total_points'])
        perf += (points[-1] - points[0])/float(len(sub_p))*2880/1.25
        length += len(sub)
    group_good_copy += [good_copy]
    group_performance += [perf/float(n)]
    lengths += [float(length)]
    ns += [n]

total_copy = sum(lengths)
total_good_copy = sum(group_good_copy)

print 'proportion copying exploiters', float(total_good_copy)/total_copy

group_copy = np.array(lengths, dtype = 'float')
group_good_copy = np.array(group_good_copy)

df = pd.DataFrame(dict(gc = group_copy,
                       ggc = group_good_copy,
                       perf = group_performance,
                       n = ns))

mpl.rc('font',family='Times New Roman')

colors = ['#348ABD',  '#467821', '#E4C334', '#A60628']

def plot_n(n, ax):
    sub = df[df['n'] == n]
    ax.scatter(sub['ggc']/sub['gc'], sub['perf'], s = 100,
               facecolors='none', edgecolors='black', lw=3)
    ax.set_title(str(n) + ' Players', fontsize=40)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.tick_params(axis='x', labelsize=30)
    ax.tick_params(axis='y', labelsize=30)

    x = sub['ggc']/sub['gc']
    y = sub['perf']
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x,y)    
    x_pred = np.linspace(0,1)
    y_pred = intercept + x_pred*slope
    ax.plot(x_pred, y_pred, c = 'black')

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex='col', sharey='row')
plot_n(2, ax1)
plot_n(3, ax2)
plot_n(4, ax3)
plot_n(5, ax4)

ax3.set_ylabel('                                 Group Performance', fontsize=50)
ax3.set_xlabel('                                                 Proportion of Copying that is of Higher Scores', fontsize=50)
ax3.xaxis.label.set_color('black')
ax3.yaxis.label.set_color('black')

fig.set_size_inches(20,12)
fig.savefig('../../plots/copy-true-proportion.pdf')#,dpi=100)

