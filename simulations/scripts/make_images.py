# python make_images.py ../../processed-waits-all/ 2015-01-26-23-19-26-925_5_1-2en01_623635699972 None /Users/peter/Desktop/wait-videos/ augmented

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pylab
import os
import sys
import matplotlib.patheffects as PathEffects

in_dir = sys.argv[1] # '../../processed/'
background_dir = sys.argv[3] # '/Users/peter/Desktop/light-fields/0-1en01/'
out_dir = sys.argv[4] # '/Users/peter/Desktop/videos/'
if len(sys.argv) > 5:
    augmented = sys.argv[5] == 'augmented'

game = sys.argv[2] # 'game_2_2015-01-18-16-56-240'
moves_file = in_dir + game + '.csv'
this_out_dir = out_dir + game + '/images/'

try:
    os.makedirs(this_out_dir)
except:
    pass

data = pd.io.parsers.read_csv(moves_file)
ticks = list(set(data['tick']))
ticks.sort()



cm = plt.cm.get_cmap('YlOrRd')
for i in range(len(ticks)):
    sub = data[data['tick'] == ticks[i]]
    ax = pylab.subplot(111)
    if background_dir != "None":
        background = np.transpose(np.array(pd.read_csv(background_dir + 't' + str(i) + '.csv')))    
        plt.pcolormesh(background, alpha = 1, cmap = 'gray')#, edgecolor=(1.0, 1.0, 1.0, 0.3), linewidth=0.0015625)
    for j in list(sub.index):
        plt.scatter(sub['x_pos'][j] - 2.5,
                    sub['y_pos'][j] - 2.5,
                    s=155,
                    c='black',
                    #vmin = 0,
                    #vmax = 1,
                    #cmap=cm,
                    marker = (3, 0, (180 + sub['angle'][j]) % 360 )
                )        
        plt.scatter(sub['x_pos'][j] - 2.5,
                    sub['y_pos'][j] - 2.5,
                    s=150,
                    #c='white',
                    c=str(sub['bg_val'][j]),
                    #vmin = 0,
                    #vmax = 1,
                    #cmap=cm,
                    marker = (3, 0, (180 + sub['angle'][j]) % 360 )
                )
        
        #text = sub['state'][j]
        text = str(sub['pid'][j])[0:4]
        if augmented:
            if sub['state'][j] == 'exploring':
                text += ': R'
            if sub['state'][j] == 'exploiting':
                text += ': I'
            if sub['state'][j] == 'copying':
                text += ': C'
        txt = plt.text(sub['x_pos'][j] - 2.5 - 12,
                 sub['y_pos'][j] - 2.5 + 8,
                 text, color = '#8EACE8')
        txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='black')])
    #plt.axis([0, 480, 0, 275])
    plt.axis('scaled')
    ax.set_xlim([0,480])
    ax.set_ylim([0,275])
    #    if augmented:
    #        for j in list(sub.index):
    #            if sub['going_straight'][j]:
    #                axes = pylab.axes()
    #                circle = pylab.Circle((sub['x_pos'][j] - 2.5,sub['y_pos'][j] - 2.5), radius=40, alpha=0.5,color='black',fill=False)
    #                axes.add_patch(circle)

    if augmented:
        plt.xlabel('R: Exploring, I: Exploiting, C: Copying')

    plt.tick_params(
        which='both',      
        bottom=False,      
        top=False,
        left=False,
        right=False,
        labelbottom=False,
        labelleft=False)
        
    plt.savefig(this_out_dir + 'pos' + "%04d" % i +  '.png')
    plt.clf()
