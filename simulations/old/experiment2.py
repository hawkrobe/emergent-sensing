import sys
sys.path.append('./player_model/')
sys.path.append('./utils/')

from multiprocessing import Pool

import os
import sys
import numpy as np
import pandas as pd

import config
import exp_config

from bots import BasicBot
from rectangular_world import RectangularWorld
from environment import *

reps = exp_config.simulation_reps
info, out_dir = exp_config.get_experiment2_config(exp_config.simulation_reps)

TELEPORT_TO = 0
FORCE_EXPLOIT = 1

# TODO: assumes 5 player fixed model

def is_in_it(tick, second):
    if second:
        player_spot = [38,39,40,43,44,47,48,50]
    else:
        player_spot = [8,9,10,13,14,17,18,20]
        
    in_it = False
    for i in range(len(player_spot)//2):
        if tick >= player_spot[2*i]*8 and tick < player_spot[2*i+1]*8:
            in_it = True

    return in_it            

def simulate(close_second, models, environment_model, second_environment,
             out_file, out_dir, file_prefix, log_file):

    n_players = len(models)    
    world_index = ['player','matched','matched','mismatch','mismatch']
    environments = {
        'player':environment_model,'matched':environment_model,'mismatch':second_environment
    }
    
    worlds = {
        'player':  World(environment_model, noise_location = None,
                         n_players = n_players, stop_and_click = config.STOP_AND_CLICK),
        'matched' : World(environment_model, noise_location = None, n_players = n_players,
                          stop_and_click = config.STOP_AND_CLICK),
        'mismatch' : World(second_environment, noise_location = None, n_players = n_players,
                           stop_and_click = config.STOP_AND_CLICK)
    }
    following = {
        'player' : [(None,None)],
        'matched' : [(None,None)],
        'mismatch' : [(None,None)]
    }    
        
    first_start = 10
    second_start = 4
    
    for tick in range(1, worlds['player'].game_length):
        print(tick)
        in_it = is_in_it(tick, close_second)        
        if in_it:
            following['player'] += [(0,None)]
        else:
            following['player'] += [(None,None)]        
        if tick == first_start * 8:
            following['matched'] += [(n_players - 4, None)]
            following['mismatch'] += [(n_players - 2, None)]
        elif tick > first_start * 8 and tick < (first_start + 10) * 8:
            following['matched'] += [(None, n_players - 4)]
            following['mismatch'] += [(None, n_players - 2)]            
        elif tick == second_start * 8:
            following['matched'] += [(n_players - 3, None)]
            following['mismatch'] += [(n_players - 1, None)]
        elif tick > second_start * 8 and tick < (second_start + 10) * 8:
            following['matched'] += [(None, n_players - 3)]
            following['mismatch'] += [(None, n_players - 1)]            
        else:
            following['matched'] += [(None,None)]
            following['mismatch'] += [(None,None)]
    
    centroids = dict([(k,Centroids(environments[k], worlds[k], log_file)) for k in worlds])
    worlds['player'].players[0].pos = worlds['player'].world_model.get_random_position()
    worlds['player'].players[1].pos = worlds['matched'].world_model.get_random_position()
    worlds['player'].players[2].pos = worlds['matched'].world_model.get_random_position()
    worlds['player'].players[3].pos = worlds['mismatch'].world_model.get_random_position()
    worlds['player'].players[4].pos = worlds['mismatch'].world_model.get_random_position()
        
    for k in worlds:        
        w = worlds[k]
        for i,p in enumerate(w.players):
            p.turn_pref = worlds['player'].players[i].turn_pref
            p.pos = copy.copy(worlds['player'].players[i].pos)
            p.angle = copy.copy(worlds['player'].players[i].angle)
            p.speed = copy.copy(worlds['player'].players[i].speed)
        
    pids = range(n_players)
    
    # TODO: this is a hack to have bg_vals set properly
    for k in worlds:        
        w = worlds[k]
        w.advance() 
        w.time = 0
    
    goals = [['',''] for i in range(n_players)]

    for i in range(n_players):
        p = worlds['player'].players[i]
        write(pids[i], p, 0, out_file, goals[i], p.curr_background, False, False)
    
    for tick in range(1, worlds['player'].game_length):
        print(tick)
        obs_bg_vals = [None for i in range(n_players)]
        models_copy = copy.deepcopy(models)
        for i in range(n_players):
            bg_vals = {}
            if i == 0:
                for k in worlds:
                    w = worlds[k]
                    pos, bg_vals[k], others, time = w.get_obs(i)
                bg_val = max([bg_vals[k] for k in bg_vals])
            else:
                pos, bg_val, others, time = worlds[world_index[i]].get_obs(i)
            
            obs_bg_vals[i] = bg_val
            models[i].observe(pos, bg_val, time)
            
            force_exploit = False
            exploit_world = 'player'

            for k in worlds:
                if following[k][tick][FORCE_EXPLOIT] == i:
                    force_exploit = True
                    exploit_world = k
                    
            goals[i],slow = models[i].act(worlds['player'].players[i], models_copy,
                                          force_exploit, centroids[exploit_world].centers[-1])
            
            for k in worlds:
                w = worlds[k]
                if k == 'player':
                    continue
                w.players[i].go_towards(goals[i])
                if slow:
                    w.players[i].go_slow()

        for k in worlds:
            add = (following[k][tick][TELEPORT_TO] is not None
                   or following[k][tick][FORCE_EXPLOIT] is not None)
            c = centroids[k]
            c.advance(following[k][tick][TELEPORT_TO], add)
        
        for k in worlds:
            w = worlds[k]
            w.advance()
        
        for i in range(n_players):
            for j in worlds:
                w = worlds[j]
                for k in worlds:
                    v = worlds[k]
                    assert np.linalg.norm(w.players[i].angle - v.players[i].angle) < 1e-8
                    assert np.linalg.norm(w.players[i].speed - v.players[i].speed) < 1e-8
                    assert np.linalg.norm(w.players[i].pos - v.players[i].pos) < 1e-8
                
            p = worlds['player'].players[i]
            if out_file is not None:
                write(pids[i], p, tick, out_file, goals[i], obs_bg_vals[i],
                      is_in_it(tick, close_second), is_in_it(tick, not close_second))
    
    for k in worlds:
        w = worlds[k]
        write_centers(w.world_model.centers, out_dir + file_prefix + '-' + k + '_bg.csv')
    
def write(pid, p, tick, out_file, goal, bg_val, in_close, in_far):
    out = [pid, tick, 'true', p.pos[0], p.pos[1], p.speed, p.angle, bg_val, '',
           goal[0], goal[1], in_close, in_far]
    out = map(str, out)
    out_file.write(','.join(out) + '\n')

def write_centers(centers, center_file):    
    centers = np.array([[np.nan,np.nan] if x is None else x for x in centers])
    df = pd.DataFrame(centers)
    df.columns = ['x_pos','y_pos']
    df.to_csv(center_file, index = False)

def run_simulation(exp_ind):
    
    experiment = info['experiments'][exp_ind]
    print(experiment)

    np.random.seed(info['seed'][exp_ind]) 
    bg = info['background_types'][exp_ind]
    close_second = info['locs'][exp_ind] == 'close_second'
    partner = info['partners'][exp_ind]
    strategy = info['strategies'][exp_ind]
    noise = info['noises'][exp_ind]

    environments = get_environments()    
    mismatch_bg = 'wall' if bg == 'spot' else 'spot'

    player_view = [True]*exp_config.num_players
    bot_view = [False] + [True]*(exp_config.num_players - 1)
    num_confederates = exp_config.num_players - 5
    file_prefix = experiment + strategy
    log_f = open(out_dir + file_prefix + '-simulation.log', 'w')
    
    # TODO: using confederates would break downstream code currently
    player_model = BasicBot(environments[bg], player_view, strategy, noise, log_file = log_f)
    confederates = [BasicBot(environments[bg], np.copy(bot_view), partner, i + 1, log_file = log_f)
                    for i in range(num_confederates)]
    matched = [BasicBot(environments[bg], np.copy(bot_view), partner,
                        num_confederates + 1, log_file = log_f) for i in range(2)]
    mismatch = [BasicBot(environments[mismatch_bg], np.copy(bot_view), partner,
                         num_confederates + 3, log_file = log_f) for i in range(2)]    
    models = [player_model] + confederates + matched + mismatch
    
    with open(out_dir + file_prefix + '-simulation.csv', 'w') as out_f:
        out_f.write('pid,tick,active,x_pos,y_pos,velocity,angle,bg_val,total_points,' +
                    'goal_x,goal_y,in_close,in_far\n')
        simulate(close_second, models, environments[bg], environments[mismatch_bg],
                             out_f, out_dir, file_prefix, log_f)

    log_f.close()

def get_environments():
    return {
        'spot': lambda x: RectangularWorld(x, config.GAME_LENGTH, False, config.DISCRETE_BG_RADIUS),
        'wall' : lambda x: RectangularWorld(x, config.GAME_LENGTH, False, config.DISCRETE_BG_RADIUS,
                                            edge_goal = True)
    }

if __name__ == '__main__':
    p = Pool(exp_config.num_procs)
    p.map(run_simulation, range(len(info['experiments'])))

