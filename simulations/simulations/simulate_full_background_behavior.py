
import sys
sys.path.append('../player_model/')

from multiprocessing import Pool

import os
import sys

import full_background_simulation as simulation
import simulation_utils

import config
import exp_config

from basic_bot import *

from rectangular_world import RectangularWorld

reps = exp_config.simulation_reps

info, out_dir = exp_config.get_full_background_config(reps)

def func(exp_ind):

    experiment = info['experiments'][exp_ind]
    print(experiment)
    
    nbots = info['nums_bots'][exp_ind]
    group = info['groups'][exp_ind]
    noise = info['noises'][exp_ind]

    bg_file = exp_config.full_bg_dir + noise + '/'
    
    
    environment = get_environment()
    
    log_f = open(out_dir + experiment + '-simulation.log', 'w')
    
    models = [BasicBot(environment, [True]*nbots, group, i, random_explore = True, log_file = log_f) for i in range(nbots)]
    
    with open(out_dir + experiment + '-simulation.csv', 'w') as out_f:
        
        out_f.write('pid,tick,active,x_pos,y_pos,velocity,angle,bg_val,total_points,goal_x,goal_y\n')
        
        simulation.simulate(bg_file, models, environment, out_f,
                            out_dir, experiment)

    log_f.close()


def get_environment():

    return lambda x: RectangularWorld(x,
                                      3.0,
                                      True,
                                      None,
                                      False)


p = Pool(exp_config.num_procs)
p.map(func, range(len(info['experiments'])))
#print([x for x in map(func, range(len(info['experiments'])))])
