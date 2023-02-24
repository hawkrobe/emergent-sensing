# python scripts/make_images.py output/predictions-emergent/spot-1-asocial-1-simulation.csv output/predictions-emergent/spot-1-asocial-1-bg.csv output/movies
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pylab
import os
import sys
import matplotlib.patheffects as PathEffects

moves_file = sys.argv[1]
background_file = sys.argv[2] 
out_dir = sys.argv[3]
this_out_dir = out_dir + '/images/'

try:
    os.makedirs(this_out_dir)
except:
    pass

data = pd.io.parsers.read_csv(moves_file)
ticks = list(set(data['tick']))
ticks.sort()
cm = plt.cm.get_cmap('YlOrRd')

# loop through time points and make image for each tick
for i in range(0, len(ticks), 4):
    sub = data[data['tick'] == ticks[i]]
    ax = pylab.subplot(111)

    # plot background -- when provided as csv, plot spotlight circle
    # otherwise need to pull in full field
    if background_file[-3:] == 'csv' :
        background = pd.read_csv(background_file).iloc[i]
        plt.scatter(background['x_pos'], background['y_pos'], s = 2500, c='grey')
    elif background_file != "None" :
        background = np.transpose(np.array(pd.read_csv(background_file + 't' + str(i) + '.csv')))    
        plt.pcolormesh(background, alpha = 1, cmap = 'gray')
    for j in list(sub.index):
        plt.scatter(sub['x_pos'][j] - 2.5,
                    sub['y_pos'][j] - 2.5,
                    s=155,
                    c='black',
                    marker = (3, 0, (180 + sub['angle'][j]) % 360 )
                )        
        plt.scatter(sub['x_pos'][j] - 2.5,
                    sub['y_pos'][j] - 2.5,
                    s=150,
                    c=str(sub['bg_val'][j]),
                    marker = (3, 0, (180 + sub['angle'][j]) % 360 )
                    )
        
        text = str(sub['pid'][j])[0:4]
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
    plt.axis('scaled')
    ax.set_xlim([0,480])
    ax.set_ylim([0,275])

    plt.xlabel('R: Exploring, I: Exploiting, C: Copying')
    plt.tick_params(which='both', bottom=False, top=False, left=False, right=False,
                    labelbottom=False, labelleft=False)
    plt.savefig(this_out_dir + 'pos' + "%04d" % i +  '.png')
    plt.clf()
