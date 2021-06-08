
import os
import sys
import numpy as np
import pandas as pd

from multiprocessing import Pool

import simulation

from rational_model import *

social_model = sys.argv[1] == 'True'
out_dir_base = sys.argv[2]

in_dir = '../../new-processed/'
out_dir = '../../' + out_dir_base + '-simulations' + ('-nonsocial' if not social_model else '') + '/'
bg_dir = '/home/pkrafft/couzin_copy/light-fields/' 

try:
    os.makedirs(out_dir)
except:
    pass

in_file = '../../modeling/model-pars.csv'

df = pd.read_csv(in_file)

def run(game):

    sub = df[df['game'] == game]

    background_dir = bg_dir + game.split('_')[-2] + '/'

    n_players = len(sub)

    pars = list(sub['par'])
    
    positions = np.array(sub[['x_pos','y_pos']])
    pids = list(sub['pid'])
    
    out_f = open(out_dir + game, 'w')
    out_f.write('pid,tick,active,x_pos,y_pos,velocity,angle,bg_val,total_points\n')
    
    world = simulation.simulate(lambda x: RationalModel(x, watch_others = social_model), 
                                background_dir, n_players, par_settings = pars, init_pos = positions,
                                out_file = out_f, pids = pids)

    out_f.close()    

games = list(set(df['game']))

p = Pool(8)
p.map(run, games)
