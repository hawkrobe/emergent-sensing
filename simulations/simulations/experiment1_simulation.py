import sys
sys.path.append('player_model/')
sys.path.append('simulations/')

import pandas as pd
import numpy as np

from environment import *
from centroid_manager import *

import copy

import config

def simulate(centers, models, environment_model, out_file, out_dir, file_prefix):
    
    n_players = len(models)
    world = World(environment_model, noise_location = None, n_players = n_players,
                  stop_and_click = config.STOP_AND_CLICK)
    world.world_model.centers = centers['player']
    pids = range(n_players)
    
    # TODO: this is a hack to have bg_vals set properly
    world.advance() 
    world.time = 0
    
    goals = [['',''] for i in range(n_players)]    
    for i in range(n_players):
        p = world.players[i]
        write(pids[i], p, models[i], 0, out_file, goals[i], file_prefix)
    
    for tick in range(1, world.game_length):
        models_copy = copy.deepcopy(models)        
        for i in range(n_players):        
            pos, bg_val, others, time = world.get_obs(i)
            models[i].observe(pos, bg_val, time)            
            goals[i],slow = models[i].act(world.players[i], models_copy)
        
        world.advance()
        for i in range(n_players):
            if out_file is not None:
                write(pids[i], world.players[i], models[i], tick, out_file, goals[i], file_prefix)
    
    write_centers(world.world_model.centers, out_dir + file_prefix + '-bg.csv')

def write(pid, p, model, tick, out_file, goal, file_prefix):
    out = [file_prefix, pid, tick, 'true', model.state, p.pos[0], p.pos[1], p.speed, p.angle, p.curr_background, goal[0], goal[1]]
    out = list(map(str, out))
    out_file.write(','.join(out) + '\n')

def write_centers(centers, center_file):    
    centers = np.array([[np.nan,np.nan] if x is None else x for x in centers])
    df = pd.DataFrame(centers)
    df.columns = ['x_pos','y_pos']
    df.to_csv(center_file, index = False)

