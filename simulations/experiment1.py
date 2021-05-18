import os
import sys
sys.path.append('./player_model/')
sys.path.append('./simulations/')
sys.path.append('./utils/')

import simulations.experiment1_simulation as simulation
import simulation_utils
import config
import exp_config

from multiprocessing import Pool
from basic_bot import *
from rectangular_world import RectangularWorld

reps = exp_config.simulation_reps
info, out_dir = exp_config.get_emergent_config(reps)

def run_simulation(exp_ind):
    experiment = info['experiments'][exp_ind]    
    bg = info['background_types'][exp_ind]
    nbots = info['nums_bots'][exp_ind]
    strategy = info['strategies'][exp_ind]

    print('running', experiment)
    environment = get_environment(bg)
    centers = {'player': simulation_utils.random_walk_centers(environment)}
    models = [BasicBot(environment, [True]*nbots, strategy, i) for i in range(nbots)]    
    with open(out_dir + experiment + '-simulation.csv', 'w') as out_f:
        out_f.write('exp,pid,tick,active,state,x_pos,y_pos,velocity,angle,bg_val,goal_x,goal_y\n')        
        simulation.simulate(centers, models, environment, out_f, out_dir, experiment)

def get_environment(bg):
    return lambda x: RectangularWorld(
        x,
        config.GAME_LENGTH,
        False,
        config.DISCRETE_BG_RADIUS,
        edge_goal = (bg == 'wall')
    )

if __name__ == '__main__':
   p = Pool(exp_config.num_procs)
   p.map(run_simulation, range(len(info['experiments'])))
