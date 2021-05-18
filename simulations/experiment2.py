
import sys
sys.path.append('../player_model/')

from multiprocessing import Pool

import os
import sys
import micro_experiment_simulation as simulation
import numpy as np
import pandas as pd

import config
import exp_config

from basic_bot import *

from rectangular_world import RectangularWorld

reps = exp_config.simulation_reps

info, out_dir = exp_config.get_micro_config(exp_config.simulation_reps)

def func(exp_ind):
    
    experiment = info['experiments'][exp_ind]
    print(experiment)

    np.random.seed(info['seed'][exp_ind])
    
    bg = info['background_types'][exp_ind]
    close_second = info['locs'][exp_ind] == 'close_second'
    partner = info['partners'][exp_ind]
    group = info['groups'][exp_ind]
    noise = info['noises'][exp_ind]

    environments = get_environments()
    
    mismatch_bg = 'wall' if bg == 'spot' else 'spot'

    player_view = [True]*exp_config.num_players
    bot_view = [False] + [True]*(exp_config.num_players - 1)

    num_confederates = exp_config.num_players - 5

    file_prefix = experiment + '-social'

    log_f = open(out_dir + file_prefix + '-simulation.log', 'w')
    
    # TODO: using confederates would break downstream code currently
    player_model = BasicBot(environments[bg], player_view, group, 0, noise, log_file = log_f)
    confederates = [BasicBot(environments[bg], np.copy(bot_view), partner, i + 1, log_file = log_f) for i in range(num_confederates)]
    matched = [BasicBot(environments[bg], np.copy(bot_view), partner, num_confederates + 1, log_file = log_f) for i in range(2)]
    mismatch = [BasicBot(environments[mismatch_bg], np.copy(bot_view), partner, num_confederates + 3, log_file = log_f) for i in range(2)]
    
    models = [player_model] + confederates + matched + mismatch
    
    with open(out_dir + file_prefix + '-simulation.csv', 'w') as out_f:

        out_f.write('pid,tick,active,x_pos,y_pos,velocity,angle,bg_val,total_points,goal_x,goal_y,in_close,in_far\n')

        centroids = simulation.simulate(close_second, models,
                                        environments[bg],
                                        environments[mismatch_bg], out_f,
                                        out_dir, file_prefix, log_f)

    log_f.close()
    
    file_prefix = experiment + '-asocial'
    
    log_f = open(out_dir + file_prefix + '-simulation.log', 'w')

    player_model = BasicBot(environments[bg], player_view, 'asocial', 0, noise, log_file = log_f)
    confederates = [BasicBot(environments[bg], np.copy(bot_view), partner, i + 1, log_file = log_f) for i in range(num_confederates)]
    matched = [BasicBot(environments[bg], np.copy(bot_view), partner, num_confederates + 1, log_file = log_f) for i in range(2)]
    mismatch = [BasicBot(environments[mismatch_bg], np.copy(bot_view), partner, num_confederates + 3, log_file = log_f) for i in range(2)]
    
    models = [player_model] + confederates + matched + mismatch
    
    with open(out_dir + file_prefix + '-simulation.csv', 'w') as out_f:

        out_f.write('pid,tick,active,x_pos,y_pos,velocity,angle,bg_val,total_points,goal_x,goal_y,in_close,in_far\n')
        
        simulation.simulate(close_second, models,
                            environments[bg],
                            environments[mismatch_bg], out_f,
                            out_dir, file_prefix, log_f)

    log_f.close()


def get_environments():

    environments = {}

    environments['spot'] = lambda x: RectangularWorld(x,
                                                     config.GAME_LENGTH,
                                                     False,
                                                     config.DISCRETE_BG_RADIUS)
    environments['wall'] = lambda x: RectangularWorld(x,
                                                      config.GAME_LENGTH,
                                                      False,
                                                      config.DISCRETE_BG_RADIUS,
                                                      edge_goal = True)

    return environments
    
p = Pool(exp_config.num_procs)
p.map(func, range(len(info['experiments'])))
#map(func, range(len(info['experiments'])))
#print([x for x in map(func, range(len(info['experiments'])))])

