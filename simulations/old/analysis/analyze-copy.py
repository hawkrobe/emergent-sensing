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

group_copy = []
group_good_copy = []
group_performance = []
lengths = []
ns = []

for game in os.listdir(in_dir):
    if game[-4:] != '.csv':
        continue
    
    data = pd.io.parsers.read_csv(in_dir + game)
    players = set(data['pid'])
    n = len(players)
    if n < 2:
        continue
    copy = 0
    good_copy = 0
    perf = 0
    length = 0
    for p in players:
        sub_p = data[data['pid'] == p]
        sub = sub_p[sub_p['state'] != 'exploiting']
        copy += sum(sub['copying'])
        good_copy += sum(sub['copying_exploiting'])
        points = list(sub_p['total_points'])
        perf += (points[-1] - points[0])/float(len(sub_p))*2880/1.25
        length += len(sub)
    group_copy += [copy]
    group_good_copy += [good_copy]
    group_performance += [perf/float(n)]
    lengths += [float(length)]
    ns += [n]
    if good_copy/float(copy) < 0.6:
        print game, n, good_copy/float(copy)

total_copy = sum(group_copy)
total_good_copy = sum(group_good_copy)

print 'proportion copying exploiters', float(total_good_copy)/total_copy

group_copy = np.array(group_copy, dtype = 'float')
group_good_copy = np.array(group_good_copy)
lengths = np.array(lengths)

df = pd.DataFrame(dict(gc = group_copy,
                       ggc = group_good_copy,
                       perf = group_performance,
                       n = ns,
                       length = lengths))

########  all copies #########

x = group_copy/lengths
x_mat = np.column_stack((np.ones(len(x)),x, x**2))
y = group_performance

fit = sm.OLS(y, x_mat).fit()
print fit.summary()

x_pred = np.array(sorted(x))
x_mat = np.array([np.ones(len(x_pred)), x_pred,x_pred**2])
y_pred = np.dot(np.transpose(x_mat),fit.params)


plt.rcParams.update(pd.tools.plotting.mpl_stylesheet)

fig, ax = plt.subplots()
ax.margins(0.05)

color_cycle = ax._get_lines.color_cycle

colors = [next(color_cycle) for i in range(5)]

i = 0
j = 0
for n in set(ns):
    sub = df[df['n'] == n]
    ax.plot(sub['gc']/sub['length'], sub['perf'], marker='o', linestyle='', ms = 10, c = colors[i], label = n)
    i += 1
#ax.plot(x_pred, y_pred, c = 'black')

    
legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),
          title = 'Players', numpoints=1)
legend.get_title().set_fontsize('20')
plt.setp(plt.gca().get_legend().get_texts(), fontsize='20')
plt.xlabel('Proportion of Time Not Exploiting Spent Copying Any Individuals', fontsize=24)
plt.ylabel('Group Performance', fontsize=24)

plt.show()

########  good copies #########

x = group_good_copy/lengths
y = group_performance
slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x,y)

print
print 'good copy regression slope:', slope, ', p:',  p_value

x_pred = np.array(sorted(x))
y_pred = intercept + x_pred*slope

plt.rcParams.update(pd.tools.plotting.mpl_stylesheet)

fig, ax = plt.subplots()
ax.margins(0.05)

color_cycle = ax._get_lines.color_cycle

colors = [next(color_cycle) for i in range(5)]

i = 0
j = 0
for n in set(ns):
    sub = df[df['n'] == n]
    ax.plot(sub['ggc']/sub['length'], sub['perf'], marker='o', linestyle='', ms = 10, c = colors[i], label = n)
    i += 1
#ax.plot(x_pred, y_pred, c = 'black')
    
legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),
          title = 'Players', numpoints=1)
legend.get_title().set_fontsize('20')
plt.setp(plt.gca().get_legend().get_texts(), fontsize='20')

plt.xlabel('Proportion of Time Not Exploiting Spent Copying Exploiting Individuals', fontsize=24)
plt.ylabel('Group Performance', fontsize=24)

plt.show()

########  proportion good copies #########

x = group_good_copy/group_copy
y = group_performance
slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x,y)

print
print 'proportion good copy regression slope:', slope, ', p:',  p_value

x_pred = np.array(sorted(x))
y_pred = intercept + x_pred*slope

plt.rcParams.update(pd.tools.plotting.mpl_stylesheet)

fig, ax = plt.subplots()
ax.margins(0.05)

color_cycle = ax._get_lines.color_cycle

colors = [next(color_cycle) for i in range(5)]

i = 0
j = 0
for n in set(ns):
    sub = df[df['n'] == n]
    ax.plot(sub['ggc']/sub['gc'], sub['perf'], marker='o', linestyle='', ms = 10, c = colors[i], label = n)
    i += 1
#ax.plot(x_pred, y_pred, c = 'black')
    
legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),
          title = 'Players', numpoints=1)
legend.get_title().set_fontsize('20')
plt.setp(plt.gca().get_legend().get_texts(), fontsize='20')

plt.xlabel('Proportion of Copying that is of Exploiting Individuals', fontsize=24)
plt.ylabel('Group Performance', fontsize=24)

plt.show()

