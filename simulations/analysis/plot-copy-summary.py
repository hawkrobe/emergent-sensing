
import pandas as pd
import numpy as np

import seaborn as sns
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

out_dir = '../../plots/time-series/'

in_dir_bases = ['re-simulations','re-simulations-nonsocial','re-processed']
non_social_dir = 're-simulations-nonsocial'

games = ['2015-01-30-20-58-46-738_5_3-1en01_490778852021.csv',
         '2015-01-30-12-1-4-89_5_2-1en01_578523323172.csv',
         '2015-01-30-14-13-5-238_5_0-1en01_850912750000.csv',
         '2015-01-30-19-13-16-753_5_1-1en01_254379808437.csv',
         '2015-01-29-20-50-9-4_5_2-1en01_619311067974.csv',
         '2015-01-30-20-58-46-738_5_3-1en01_490778852021.csv']

quantities = ['Score','Uncertainty']
copies = ['copying','copying_exploiting']

results = []

for in_dir_base in in_dir_bases:

    in_dir = '../../' + in_dir_base + '/'
    
    for copying in copies:
        
        for game in games:

            df = pd.read_csv(in_dir + game)

            players = list(set(df['pid']))

            for player in range(len(players)):

                pid = players[player]

                sub = df.loc[df['pid'] == pid].copy()

                if len(sub) == 0:
                    continue
                
                results += [[in_dir_base, copying, game, game+'-'+str(pid), np.mean(sub[copying])]]
                
df = pd.DataFrame(results)
df.columns = ['in_dir','copying','game','pid','amount']

diffs = []

# TODO: switch this to per PID
for game in set(df['game']):

    for copying in copies:

        
        sub = df.loc[(df['game'] == game)&(df['copying'] == copying)&(df['in_dir'] == non_social_dir)].copy()

        nonsocial_amount = np.mean(sub['amount'])
        
        for in_dir in in_dir_bases:

            if in_dir == non_social_dir:
                continue
            
            sub = df.loc[(df['game'] == game)&(df['copying'] == copying)&(df['in_dir'] == in_dir)].copy()

            norm_amount = np.mean(sub['amount']) - nonsocial_amount
            diffs += [[in_dir, copying, norm_amount]]

            
df = pd.DataFrame(diffs)
df.columns = ['in_dir','copying','amount']


sns.factorplot('in_dir', 'amount', col = 'copying',  data = df, kind = 'bar')
