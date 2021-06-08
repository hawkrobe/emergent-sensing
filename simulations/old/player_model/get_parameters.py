
import os

import pandas as pd

from fit_simple import *
from social_heuristic import *
from baseline_model import *
from test_model import *

from sklearn import gaussian_process

data = []

in_dir = '../../new-processed/'
out_dir = '../../modeling/'

light_fields = ['0-1en01', '1-1en01', '2-1en01', '3-1en01']

pars = None
smoothed = {}
x = []
y = []
for light_field in light_fields:
    par_sweep = pd.read_csv(out_dir + light_field + '_parameters.csv')
    if pars is not None:
        assert set(pars) == set(par_sweep['par'])
    else:
        pars = par_sweep['par']
    x += list(np.log(pars))
    y += list(par_sweep['score'])

x = np.array(x)
y = np.array(y)
dim = 3
fit = np.polyfit(x, y, dim)[::-1]
x = np.log(pars)
smoothed = np.dot(np.transpose([x**i for i in range(dim+1)]), fit)

#smoothed[light_field] = gaussian_process.GaussianProcess(nugget = 1e-12)
#smoothed[light_field].fit(np.transpose(np.array([par_sweep['score']])), par_sweep['par'])

def predict(score):
    for i in range(len(pars)):
        if smoothed[i] > score:            
            return pars[max(i-1,0)]
    return pars[np.argmax(smoothed)]
#max(min(smoothed[background].predict(score, eval_MSE=True)[0][0], 1.0), 0.0)

scores = []
for game in os.listdir(in_dir):

    if game.split('.')[-1] != 'csv' or game.split('_')[-2][2] != '1':
        continue

    background = game.split('_')[-2]
    
    df = pd.read_csv(in_dir + game)

    players = list(set(df['pid'].dropna()))
    
    if len(players) == 1 and len(df) == 2880:
        
        print game

        pid = players[0]

        scores += [np.mean(df.loc[1440:,'bg_val'])]

par = predict(np.mean(scores))

scores = []
for game in os.listdir(in_dir):

    if game.split('.')[-1] != 'csv' or game.split('_')[-2][2] != '1':
        continue

    background = game.split('_')[-2]
    
    df = pd.read_csv(in_dir + game)
    
    players = list(set(df['pid'].dropna()))
    
    for pid in players:
        
        pos = np.array(df[(df['tick'] == 0)&(df['pid'] == pid)][['x_pos','y_pos']])[0]
        
        data += [[game, len(players), pid, par, pos[0], pos[1]]]
        
out_df = pd.DataFrame(data)
out_df.columns = ['game','n_players','pid','par','x_pos','y_pos']
out_df.to_csv(out_dir + '/model-pars.csv', index = False)
