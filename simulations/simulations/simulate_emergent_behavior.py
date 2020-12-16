
import sys
sys.path.append('../player_model/')

from multiprocessing import Pool

import os
import sys

import emergent_simulation as simulation
import simulation_utils

import config
import exp_config

from basic_bot import *

from rectangular_world import RectangularWorld

reps = exp_config.simulation_reps

info, out_dir = exp_config.get_emergent_config(reps)

def func(exp_ind):

    experiment = info['experiments'][exp_ind]
    print experiment
    
    bg = info['background_types'][exp_ind]
    nbots = info['nums_bots'][exp_ind]
    group = info['groups'][exp_ind]
    noise = info['noises'][exp_ind]
    
    environment = get_environment(bg)
    
    centers = {'player':simulation_utils.random_walk_centers(environment)}

    log_f = open(out_dir + experiment + '-simulation.log', 'w')
    
    models = [BasicBot(environment, [True]*nbots, group, i, log_file = log_f) for i in range(nbots)]
    
    with open(out_dir + experiment + '-simulation.csv', 'w') as out_f:
        
        out_f.write('pid,tick,active,x_pos,y_pos,velocity,angle,bg_val,total_points,goal_x,goal_y\n')
        
        simulation.simulate(centers, models, environment, out_f,
                            out_dir, experiment)

    log_f.close()


def get_environment(bg):

    return lambda x: RectangularWorld(x,
                                      config.GAME_LENGTH,
                                      False,
                                      config.DISCRETE_BG_RADIUS,
                                      edge_goal = (bg == 'wall'))


p = Pool(exp_config.num_procs)
p.map(func, range(len(info['experiments'])))
#map(func, range(len(info['experiments'])))
