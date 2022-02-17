import os
import sys
import copy

sys.path.append('./player_model/')
sys.path.append('./utils')

import config
import exp_config

import pandas as pd
import numpy as np

from multiprocessing import Pool
from bots import BasicBot
from rectangular_world import RectangularWorld
from environment import *

reps = exp_config.simulation_reps
info, out_dir = exp_config.get_emergent_config(reps)

def write(pid, p, model, tick, out_file, goal, experiment):
    nbots, composition, rep, prob_explore = experiment.split('-')
    out = [experiment, nbots, composition, pid, tick, 'true', model.state, p.pos[0], p.pos[1],
           p.speed, p.angle, p.curr_background, prob_explore, model.strategy,
           goal[0], goal[1]]
    out = list(map(str, out))
    out_file.write(','.join(out) + '\n')

def write_centers(centers, center_file):    
    centers = np.array([[np.nan,np.nan] if x is None else x for x in centers])
    df = pd.DataFrame(centers)
    df.columns = ['x_pos','y_pos']
    df.to_csv(center_file, index = False)
    
def write_final(experiment, models):    
    with open(out_dir + experiment + '-final.csv', 'w') as out_f:
        for i, m in enumerate(models) :
            out_f.write(','.join([experiment, str(i), m.strategy, str(m.total_score)]) + '\n')

def run_simulation(exp_ind):
    print(exp_ind)
    experiment = info['experiments'][exp_ind]    
    bots = info['bots'][exp_ind]
    environment = lambda bg: RectangularWorld(bg, config.GAME_LENGTH, False,
                                              config.DISCRETE_BG_RADIUS, False)
    nbots = len(bots)
    models = [BasicBot(environment, [True]*nbots, bot['strategy'], i,
                       prob_explore = bot['prob_explore'])
              for i, bot in enumerate(bots)]

    # Initialize world with random walk of spotlight
    world = World(environment, noise_location = None, n_players = len(models),
                  stop_and_click = config.STOP_AND_CLICK)
    world.random_walk_centers()

    # write centers to file
    write_centers(world.world_model.centers, out_dir + experiment + '-bg.csv')

    world.advance() 
    world.time = 0        

    with open(out_dir + experiment + '-simulation.csv', 'w') as out_f:
        out_f.write('exp,nbots,composition,pid,tick,active,state,x_pos,y_pos,velocity,angle,bg_val,' +
                     'prob_explore,strategy,goal_x,goal_y\n')

        # Write initial states
        for i in range(len(models)):
            p = world.players[i]
            write(i, p, models[i], 0, out_f, ['', ''], experiment)

        # simulate ticks
        for tick in range(1, world.game_length):
            simulate_tick(tick, models, world, out_f, experiment)

    write_final(experiment, models)
            
def simulate_tick(tick, models, world, out_file, experiment):
    models_copy = copy.deepcopy(models)
    goals = [['',''] for i in range(len(models))]
    for i in range(len(models)):        
        pos, bg_val, others, time = world.get_obs(i)
        models[i].observe(pos, bg_val, time)            
        goals[i], slow = models[i].act(world.players[i], models_copy)
        
    world.advance()
    for i in range(len(models)):
        write(i, world.players[i], models[i], tick, out_file, goals[i], experiment)
    

if __name__ == '__main__':
  p = Pool(exp_config.num_procs)
  p.map(run_simulation, range(len(info['experiments'])))
