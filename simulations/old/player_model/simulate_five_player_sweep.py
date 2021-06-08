
import os
import sys
import simulation
import pandas as pd
import numpy as np

from multiprocessing import Pool

from rational_model import *

n_players = 5
reps = 10
pars = [0] + list(2**np.array(range(10)))
light_fields = ['0-1en01', '1-1en01', '2-1en01', '3-1en01']

out_dir = '../../modeling/'

in_file = '../../modeling/model-pars.csv'

df = pd.read_csv(in_file)

par_dist = list(df.loc[df['n_players'] == 1,'par'])

try:
    os.makedirs(out_dir)
except:
    pass

def run(light_field):
    
    background_dir = '/home/pkrafft/couzin_copy/light-fields/' + light_field + '/'

    file_name = out_dir + light_field + '_five_player_parameters.csv'
    out_f = open(file_name, 'w')
    out_f.write('par,score\n')
    out_f.close()
        
    for par in pars:

        scores = []
        for rep in range(reps):
            
            noise = np.random.choice(par_dist, size = n_players)            
            world = simulation.simulate(lambda x: RationalModel(x, memory = par), 
                                        background_dir, n_players, par_settings = noise)
            
            scores += [np.mean([world.players[i].avg_score_last_half for i in range(n_players)])]

        out_f = open(file_name, 'a')
        out_f.write(str(par) + ',' + str(np.mean(scores)) + '\n')
        out_f.close()

p = Pool(4)
p.map(run, light_fields)
