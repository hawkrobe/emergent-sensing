
import sys
sys.path.append('../player_model/')

import numpy as np

from environment import *

import config

def random_walk_centers(environment, super_slow = False):

    centers = []

    world = World(environment, noise_location = None, n_players = 1,
                  stop_and_click = True)
    
    world.world_model.centers = centers
    
    p = world.players[0]
    
    centers += [world.world_model.get_random_position()]
    
    p.pos = np.copy(centers[0])
    
    goal = world.world_model.get_random_position()
    
    for t in range(1, world.game_length):
        
        move = p.get_move_towards(goal, None)
        
        if move['speed'] == 'stop':

            goal = world.world_model.get_random_position()
            
            # if np.random.random() < config.SPOT_JUMP_PROB:
            #     p.pos = world.world_model.get_random_position()
        
        p.go_towards(goal)
        if super_slow:
            p.go_super_slow()
        else:
            p.go_slow()
        
        world.advance()
        
        centers += [np.copy(p.pos)]
    
    return centers

    
