
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pylab
import os
import sys
import matplotlib.patheffects as PathEffects
import re
import goal_inference

augmented = False
nominal = False
stop_and_click = False

if nominal:
    in_dir = '../../new-synthetic-score-matched-processed/'
else:
    in_dir = '../../new-processed/'    

game = '2015-01-30-14-5-9-36_1_0-1en01_37758667487.csv'; player = 0
#game = '2015-01-30-14-36-41-645_1_2-1en01_358008759329.csv'; player = 0
#game = '2015-01-29-20-50-9-4_5_2-1en01_619311067974.csv'; player = 3
#game = '2015-01-30-11-35-13-145_5_3-1en01_233730632113.csv'; player = 3

#in_dir = '../../modeling/'
#game = '0-1en01_simulation.csv'

background_dir = '/Users/peter/Desktop/light-fields/0-1en01/'

out_dir = '/Users/peter/Desktop/goals/'

if nominal:
    this_out_dir = out_dir + 'nominal-' + game[:-4] + '/images/'
else:
    this_out_dir = out_dir + game[:-4] + '/images/'
    
try:
    os.makedirs(this_out_dir)
except:
    pass

df = pd.read_csv(in_dir + game)

players = list(set(df['pid']))
#np.random.shuffle(players)

model = goal_inference.Model(n_samples = 500, stop_and_click = stop_and_click)

cm = plt.cm.get_cmap('Greens')

ticks = list(set(df['tick']))

stl_angle = None
last_angle = None

for tick in range(max(ticks)+1):
    
    sub = df[df['tick'] == tick]
    
    for j in list(sub.index):
        
        p = sub['pid'][j]
        if p != players[player]:
            continue

        if tick >= 2:
            model.observe(np.array([sub['x_pos'][j], sub['y_pos'][j]]), stl_angle, last_angle, sub['angle'][j], sub['velocity'][j])

        stl_angle = last_angle
        last_angle = sub['angle'][j]
        
        beliefs = model.get_beliefs()
    
    ax = pylab.subplot(111)
    
    #background = np.transpose(np.array(pd.read_csv(background_dir + 't' + str(tick) + '.csv')))
    #plt.pcolormesh(background, alpha = 1, cmap = 'gray', linewidth=0, rasterized=True)
    plt.pcolormesh(np.transpose(beliefs), cmap = 'Blues')
    
    for j in list(sub.index):
        if sub['pid'][j] == players[player]:
            color = 'black'
            plt.title(sub['bg_val'][j], size = 32, color = cm(float(sub['bg_val'][j])))
        else:
            color = 'white'
        plt.scatter(sub['x_pos'][j] - 2.5,
                    sub['y_pos'][j] - 2.5,
                    s=150,
                    c=color,
                    marker = (3, 0, (180 + sub['angle'][j]) % 360 ),
        )
        if augmented:
            text = ''#str(sub['pid'][j])[0:4]
            if sub['spinning'][j]:
                text += 'spinning'
            elif sub['nearby_spinning'][j]:
                text += 'nearby_spinning'
            # if sub['state'][j] == 'exploring':
            #     text += ': exploring'
            # if sub['state'][j] == 'exploiting':
            #     text += ': exploiting'
            # if sub['state'][j] == 'copying':
            #     text += ': copying'
            txt = plt.text(sub['x_pos'][j] - 2.5 - 12,
                           sub['y_pos'][j] - 2.5 + 8,
                           text, color = '#8EACE8')
            txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='black')])
        plt.axis('scaled')
        ax.set_xlim([0,480])
        ax.set_ylim([0,275])
    
    plt.savefig(this_out_dir + 'pos' + "%04d" % tick +  '.png')
    plt.clf()
