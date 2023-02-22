import os
import sys
import copy

sys.path.append('./player_model/')
sys.path.append('./utils')

import config
import pandas as pd
import numpy as np

from multiprocessing import Pool
from bots import BasicBot
from rectangular_world import RectangularWorld
from environment import *

reps = 50
num_procs = 6
out_dir = './output/predictions-emergent/'
strategies = ['smart', 'move_to_center', 'naive_copy', 'asocial']
info = {'experiments' : [], 'bots' : [], 'strategies' : [], 'prob_explore' : [], 'noise' : []}
for strategy in strategies :
    for group_size in [1,2,3,4,5,6]: # 16,32,64,128
        for prob_explore in ([None] if strategy in ['asocial'] else [0,.05,.1,.15,.2,.25] if strategy in ['smart'] else [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]) :
            # This is confusing but 'noise' means something different for the smart model
            noise = prob_explore if strategy == 'smart' else 0
            composition = np.array([strategy == 'asocial', strategy == 'naive_copy',
                                    strategy == 'move_to_center', strategy == 'smart']) * group_size
            bots = ([{'strategy' : 'asocial', 'prob_explore' : prob_explore, 'noise' : noise}] * composition[0] +
                    [{'strategy' : 'naive_copy', 'prob_explore' : prob_explore, 'noise' : noise}] * composition[1] +
                    [{'strategy' : 'move_to_center', 'prob_explore' : prob_explore, 'noise' : noise}] * composition[2] +
                    [{'strategy' : 'smart', 'prob_explore' : prob_explore, 'noise' : noise}] * composition[3])
            info['experiments'] += ['-'.join(
                [str(len(bots)), '+'.join([str(i) for i in composition]), str(rep), str(prob_explore)]
            ) for rep in range(400,400+reps)]
            info['prob_explore'] += [prob_explore for rep in range(400, 400+reps)]
            info['noise'] += [noise for rep in range(400, 400+reps)]
            info['bots'] += [bots for rep in range(400,400+reps)]
            info['strategies'] += [composition for rep in range(400,400+reps)]


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
    experiment = info['experiments'][exp_ind]
    bots = info['bots'][exp_ind]
    print(exp_ind, experiment)
    environment = lambda bg: RectangularWorld(bg, config.GAME_LENGTH, False,
                                              config.DISCRETE_BG_RADIUS, False)
    nbots = len(bots)
    models = [BasicBot(environment, [True]*nbots, bot['strategy'], i,
                       prob_explore = bot['prob_explore'],
                       noise = bot['noise'])
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
        goals[i], slow = models[i].act(world.players[i], models_copy[:i] + models_copy[i+1:])
        
    world.advance()
    for i in range(len(models)):
        write(i, world.players[i], models[i], tick, out_file, goals[i], experiment)
    

if __name__ == '__main__':
    
    try:
        os.makedirs(out_dir)
    except OSError:
        pass
    
    p = Pool(num_procs)
    p.map(run_simulation, range(len(info['experiments'])))
