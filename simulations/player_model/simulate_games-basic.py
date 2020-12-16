
import os
import sys
import numpy as np
import pandas as pd

from multiprocessing import Pool

import simulation

from test_model import *
from social_heuristic import *
import goal_inference

social_model = sys.argv[1] == 'True'
out_dir_base = sys.argv[2]

subset = '1en01'

in_dir = '../../new-processed/'
out_dir = '../../' + out_dir_base + '-simulations' + ('-nonsocial' if not social_model else '') + '/'
bg_dir = '/home/pkrafft/couzin_copy/light-fields/' 

try:
    os.makedirs(out_dir)
except:
    pass

def run(game):
    
    data = pd.io.parsers.read_csv(in_dir + game)
    players = list(set(data[data['tick'] == 1440]['pid'].dropna()))
    n_players = len(players)
    
    background_dir = bg_dir + game.split('_')[-2] + '/'

    positions = []
    for p in players:
        sub = data[(data['tick'] == 0)&(data['pid'] == p)]
        positions += [np.array(sub[['x_pos','y_pos']])[0]]
    
    out_f = open(out_dir + game, 'w')
    out_f.write('pid,tick,active,x_pos,y_pos,velocity,angle,bg_val,total_points\n')
    
    world = simulation.simulate(lambda x: SocialHeuristic(x, watch_others = social_model),
                                background_dir, n_players, par_settings = [0]*len(players),
                                init_pos = positions,
                                out_file = out_f, pids = players)
    
    out_f.close()    

pars = []
for game in os.listdir(in_dir):

    if game[-4:] != '.csv':
        continue

    if game.split('_')[-2].split('-')[1] != subset:
        continue
    
    pars += [game]

p = Pool(8)
p.map(run, pars)
