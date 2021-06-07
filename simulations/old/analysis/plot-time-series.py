
import pandas as pd
import numpy as np

import seaborn as sns
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

out_dir = '../../plots/time-series/'

in_dir_bases = ['re-simulations','re-simulations-nonsocial','re-processed']

games = ['2015-01-30-20-58-46-738_5_3-1en01_490778852021.csv',
         '2015-01-30-12-1-4-89_5_2-1en01_578523323172.csv',
         '2015-01-30-14-13-5-238_5_0-1en01_850912750000.csv',
         '2015-01-30-19-13-16-753_5_1-1en01_254379808437.csv',
         '2015-01-29-20-50-9-4_5_2-1en01_619311067974.csv',
         '2015-01-30-20-58-46-738_5_3-1en01_490778852021.csv']

quantities = ['Score','Uncertainty']
copies = ['copying','copying_exploiting']

for in_dir_base in in_dir_bases:

    in_dir = '../../' + in_dir_base + '/'

    for game in games:
    
        for quantity in quantities:

            for copying in copies:

                df = pd.read_csv(in_dir + game)

                players = list(set(df['pid']))

                for player in range(len(players)):

                    pid = players[player]
                    
                    sub = df.loc[df['pid'] == pid].copy()

                    if len(sub) == 0:
                        continue
                    
                    if quantity == 'Score':
                        vals = sub['bg_val']
                    else:
                        assert quantity == 'Uncertainty'
                        vals = sub['uncertainty']

                    sub['masked-vals'] = vals.copy()
                    sub.loc[~np.array(sub[copying], dtype=bool),'masked-vals'] = np.nan

                    ax = sns.tsplot(data=vals)
                    sns.tsplot(data=sub['masked-vals'], color = 'red', ax = ax)

                    plt.xlabel('Time')#, fontsize=50)
                    plt.ylabel(quantity)#, fontsize=50)

                    out_file = out_dir + copying + '-' + quantity + '-' + game.split('.')[0] + '-' + str(player) + '-' + in_dir_base + '.pdf'

                    fig = plt.gcf()
                    fig.savefig(out_file)
                    plt.close()
