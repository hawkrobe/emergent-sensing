
import matplotlib
matplotlib.use('Agg')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pylab
import os
import sys
import matplotlib.patheffects as PathEffects

def make_images(moves_file, this_out_dir, center_files = None,
                plot_names = False, plot_targets = False, colored = False, show_time =
                False, player_data = None):

    try:
        os.makedirs(this_out_dir)
    except:
        pass

    if moves_file is None:
        data = player_data
        player_data = None
    else:
        data = pd.io.parsers.read_csv(moves_file)
        
    if center_files is not None:
        centers = [pd.io.parsers.read_csv(f) for f in center_files]
    ticks = list(set(data['tick']))
    ticks.sort()

    cm = plt.cm.get_cmap('YlOrRd')
    for i in range(len(ticks)):
        
        sub = data[data['tick'] == ticks[i]]

        if player_data is not None:

            player_sub = player_data[player_data['tick'] == ticks[i]]
            
            sub = sub.append(player_sub)
        
        ax = pylab.subplot(111)
        
        if center_files is not None:
            for c in centers:
                x = c.iloc[i]['x_pos']
                y = c.iloc[i]['y_pos']
                circle = plt.Circle((x, y), 50, alpha = 0.3)
                ax.add_artist(circle)
        
        for j in range(len(sub.index)):
            
            if colored:
                col = sub['bg_val'].iloc[j]
            else:
                col = 'black'
            
            ax.scatter(sub['x_pos'].iloc[j] - 2.5,
                        sub['y_pos'].iloc[j] - 2.5,
                        s=100,
                        #c='white',
                        c=col,
                        vmin = 0,
                        vmax = 1,
                        cmap=cm,
                        marker = (3, 0, (180 + sub['angle'].iloc[j]) % 360 )
                    )
            if plot_names:
                plt.text(sub['x_pos'].iloc[j], sub['y_pos'].iloc[j], str(sub['pid'].iloc[j])[:4])
            if plot_targets:            
                if not np.isnan(sub['goal_x'].iloc[j]):
                    plt.text(sub['goal_x'].iloc[j], sub['goal_y'].iloc[j], str(sub['pid'].iloc[j])[:4]) 
        plt.axis('scaled')
        ax.set_xlim([0,485])
        ax.set_ylim([0,280])
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        if show_time:
            plt.title(str(i) + ", " + str(i/8))
        plt.savefig(this_out_dir + 'pos' + "%04d" % i +  '.png')
        plt.clf()
