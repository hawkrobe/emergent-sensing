
import os
import sys
import simulation
import numpy as np

from multiprocessing import Pool

from test_model import *
from rational_model import *

n_players = 1

pars = 100*(0.97)**np.array(range(500))
light_fields = ['0-1en01', '1-1en01', '2-1en01', '3-1en01']

out_dir = '../../modeling/'

try:
    os.makedirs(out_dir)
except:
    pass

def run(light_field):
    
    background_dir = '/home/pkrafft/couzin_copy/light-fields/' + light_field + '/'
    
    with open(out_dir + light_field + '_parameters.csv', 'w') as out_f:
        
        out_f.write('par,score\n')
        
        for par in pars:
            
            world = simulation.simulate(lambda x: RationalModel(x),
                                        background_dir, n_players, par_dist = [[par], [1.0]])
            
            score = world.players[0].avg_score_last_half
            out_f.write(str(par) + ',' + str(score) + '\n')
                        

p = Pool(4)
p.map(run, light_fields)
