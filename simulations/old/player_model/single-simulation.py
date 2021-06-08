
import os
import sys
import simulation
import numpy as np

from test_model import *
from rational_model import *

from rectangular_world import RectangularWorld
from spotlight_background_model import SpotlightBackground

if len(sys.argv) > 1:
    n_players = int(sys.argv[1])
    pars = float(sys.argv[2])
    write = sys.argv[3] == 'True'
else:
    n_players = 4
    pars = 50#, 0.25)
    write = True

light_field = '0-1en01'
#background_dir = '/Users/peter/Desktop/light-fields/' + light_field + '/'
background_dir = '/home/pkrafft/couzin_copy/light-fields/' + light_field + '/'

if write:
    out_dir = '../../modeling/'
    
    try:
        os.makedirs(out_dir)
    except:
        pass
    
    out_f = open(out_dir + light_field + '_simulation.csv', 'w')
    out_f.write('pid,tick,active,x_pos,y_pos,velocity,angle,bg_val,total_points\n')
else:
    out_f = None

#world = simulation.simulate(TestModel, background_dir, n_players, par_dist = [[20], [1.0]], out_file = out_f)
world = simulation.simulate(lambda x: RationalModel(x, SpotlightBackground, RectangularWorld), RectangularWorld,
                            background_dir, n_players, par_dist = [[0.4, 0.7], [0.5, 0.5]], out_file = out_f, second_bg_dir = background_dir)

for p in world.players:
    #print p.avg_score_last_half
    print p.total_points/1.25    

if write:
    out_f.close()    
