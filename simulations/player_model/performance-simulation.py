
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib.font_manager import FontProperties

import pandas as pd
import numpy as np
import os
import sys
import simulation

from social_heuristic import *

if len(sys.argv) > 1:
    n_samples = int(sys.argv[1])
else:
    n_samples = 1

plot = False

#base_dir = '/Users/peter/Desktop/light-fields/'
base_dir = '/home/pkrafft/couzin_copy/light-fields/'
score_fields = ['0-1en01','1-1en01','2-1en01','3-1en01']

out_dir = '../../modeling/'

try:
    os.makedirs(out_dir)
except:
    pass

ns = [1,2,3,4,5]
#reps = [2,2,2,2,2]
reps = [25, 12, 8, 6, 5]
#reps = [2, 2, 2, 2, 2]
#reps = [0,10,0,0,0]

perfs = [[] for i in range(len(ns))]

for i in range(len(ns)):

    for r in range(reps[i]):

        print i

        n_players = ns[i]

        background_dir = base_dir + np.random.choice(score_fields) + '/' 
        
        world = simulation.simulate(SocialHeuristic, background_dir, n_players, par_dist = [[1,5], [0.5,0.5]])
        
        perfs[i] += [[p.total_points for p in world.players]]
        print np.mean([p.total_points for p in world.players])/1.25

print n_samples, [np.mean(p)/1.25 for p in perfs]

if plot:

    df = []

    for i in range(len(ns)):

        for j in range(reps[i]):

            for k in range(ns[i]):

                df += [[ns[i], perfs[i][j][k]/1.25]]

    df = pd.DataFrame(df)
    df.columns = ['n_players', 'score']

    sns.set(font = "serif", context = "poster", style = "white")
    sns.despine()

    sns.factorplot("n_players", "score", data = df, kind="point")

    plt.xlabel('Number of Players')
    plt.ylabel('Mean Score')

    fig = plt.gcf()
    fig.savefig('../../modeling/performance-summary.pdf')

