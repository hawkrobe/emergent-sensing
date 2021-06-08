
import matplotlib
matplotlib.use('Agg')


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import collections  as mc
import pylab
import os
import sys
import matplotlib.patheffects as PathEffects
import re
import smart_particle
from jumping_background_discrete_model import JumpingBackgroundDiscrete
from side_background_discrete_model import SideBackgroundDiscrete


augmented = False
nominal = False
micro_experiments = True
alt_background = True

if nominal:
    in_dir = '../../new-synthetic-score-matched-processed/'
else:
    if micro_experiments:
        in_dir = '../../predictions/'
    else:
        in_dir = '../../new-processed/'

#game = '2015-01-30-14-5-9-36_1_0-1en01_37758667487.csv'
#game = '2015-01-30-14-36-41-645_1_2-1en01_358008759329.csv'
#game = '2015-01-29-20-50-9-4_5_2-1en01_619311067974.csv'; player = 3
#game = '2015-01-30-11-35-13-145_5_3-1en01_233730632113.csv'; player = 3
if micro_experiments:
    experiment = sys.argv[1]
    game = experiment + '_simulation-0-' + sys.argv[2] + '.csv'

#in_dir = '../../modeling/'
#game = '0-1en01_simulation.csv'

#background_dir = '/Users/peter/Desktop/light-fields/0-1en01/'

out_dir = os.path.expanduser('~') + '/beliefs/'

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

if micro_experiments:
    player = 1
    if alt_background:
        model = smart_particle.Model(lambda: SideBackgroundDiscrete(noise = 0.1), n_samples = 1000)
    else:
        model = smart_particle.Model(lambda: JumpingBackgroundDiscrete(noise = 0.1), n_samples = 1000)
else:
    models = {}
    for p in players:
        models[p] = smart_particle.Model(n_samples = 1000)

cm = plt.cm.get_cmap('Greens')

ticks = list(set(df['tick']))

for tick in range(max(ticks)+1):

    if micro_experiments:
        if tick > 0:
            last_sub = df[(df['tick'] == tick-1)&(df['pid'] == 1)]
            sub = df[(df['tick'] == tick)&(df['pid'] == 1)]
            model.observe((float(last_sub['x_pos']), float(last_sub['y_pos'])), float(sub['bg_val']))
        beliefs = model.get_beliefs()
    else:
        
        sub = df[df['tick'] == tick]
        
        for j in list(sub.index):

            p = sub['pid'][j]

            others = []

            for k in list(sub.index):

                if k == j:
                    continue

                others += [{'position':np.array([sub['x_pos'][k], sub['y_pos'][k]]),
                            'angle':sub['angle'][k],
                            'speed':sub['velocity'][k]}]

            models[p].observe((sub['x_pos'][j], sub['y_pos'][j]), sub['bg_val'][j])
            if p == players[player]:
                beliefs = models[p].get_beliefs()

    sub = df[df['tick'] == tick]
                
    ax = pylab.subplot(111)
    
    #background = np.transpose(np.array(pd.read_csv(background_dir + 't' + str(tick) + '.csv')))
    #plt.pcolormesh(background, alpha = 1, cmap = 'gray', linewidth=0, rasterized=True)
    #plt.pcolormesh(np.transpose(beliefs), cmap = 'Blues', size = 10)

    lines = [[(0, 0), (485, 0)], [(0, 0), (0, 280)], [(485, 0), (485, 280)], [(0, 280), (485, 280)]]
    lc = mc.LineCollection(lines, colors = 'grey')
    ax.add_collection(lc)
    
    plt.scatter(beliefs[:,0], beliefs[:,1], s = 5, c = 'blue', alpha = 0.2)
    
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
    ax.set_xlim([-10,495])
    ax.set_ylim([-10,290])        
    #ax.set_xlim([0,485])
    #ax.set_ylim([0,280])
    ax.axis('off')
    
    plt.savefig(this_out_dir + 'pos' + "%04d" % tick +  '.png')
    plt.clf()
