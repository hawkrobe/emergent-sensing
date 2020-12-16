import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pylab

groups = ['naive-social', 'non-social', 'smart-social']
colors = ['blue','green','orange']
reps = 30

in_dir = '../../predictions/'

#experiment = 'start-apart-come-together-alt'
experiment = 'start-apart-stay-apart-alt'

out_dir = '../../predictions/'

goals = {}
for g in groups:

    goals[g] = None
    
    for rep in range(reps):
        
        df = pd.read_csv(in_dir + experiment + '_simulation-' + str(rep) + '-' + g + '.csv')
        sub = df.loc[df['pid'] == 0]
        this_goals = np.array(sub[['goal_x','goal_y']])
        if goals[g] is None:
            goals[g] = this_goals
        else:
            goals[g] += this_goals
    
    goals[g] /= float(reps)

for i in range(len(groups)):
    plt.scatter(goals[groups[i]][:,0], goals[groups[i]][:,1], color = colors[i], alpha = 0.2)
pylab.xlim([0,485])
pylab.ylim([0,280])
plt.show()

