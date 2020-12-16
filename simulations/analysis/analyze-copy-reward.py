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

in_dir = '../../processed-simulations/'

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

########  proportion good copies #########

x = group_good_copy/group_copy
y = group_performance

x = sm.add_constant(x)
model = sm.OLS(y,x)
results = model.fit()
print results.summary()
