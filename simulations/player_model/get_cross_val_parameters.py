
import os

import pandas as pd

from fit_simple import *
from social_heuristic import *
from baseline_model import *
from test_model import *

data = []

in_dir = '../../processed/'
out_dir = '../../modeling/'

for game in os.listdir(in_dir):

    if game.split('.')[-1] != 'csv' or game.split('_')[-2][2] != '1':
        continue

    print
    print game
    
    background_dir = '/home/pkrafft/couzin_copy/light-fields/' + game.split('_')[-2] + '/'
    
    df = pd.read_csv(in_dir + game)

    players = list(df[df['tick'] == max(df['tick'])]['pid'])

    for player in range(len(players)):

        pid = players[player]

        f = Fit(df, background_dir, player)
        #par,err = f.fit_model(SocialHeuristic, [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        par,err = f.fit_model(SocialHeuristic, [0, 20, 40, 80, 160, 320, np.inf])
        pos = np.array(df[(df['tick'] == 0)&(df['pid'] == pid)][['x_pos','y_pos']])[0]

        data += [[game, len(players), pid, par, err, pos[0], pos[1]]]
    
    out_df = pd.DataFrame(data)
    out_df.columns = ['game','n_players','pid','par','err','x_pos','y_pos']
    out_df.to_csv(out_dir + '/model-pars.csv', index = False)
