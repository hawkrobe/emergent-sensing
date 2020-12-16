
import sys
sys.path.append('../player_model/')

import numpy as np

from environment import *
from basic_bot import *

import config

class Centroids():

    def __init__(self, environment, external_world, log_file):

        self.players = external_world.players
        
        self.centers = []

        external_world.world_model.centers = self.centers

        self.environment = environment
        
        self.world = World(environment, noise_location = None, n_players = 1,
                      stop_and_click = True)

        self.world.world_model.centers = self.centers
        
        self.p = self.world.players[0]
        
        self.bot = BasicBot(environment, [False], 'asocial', 0, log_file = log_file)
        
        self.centers += [self.world.world_model.get_random_position()]
        
        self.p.pos = np.copy(self.centers[0])

        self.centers[-1] = None
    
    def advance(self, following, add = True):

        if np.random.random() < 0.005 and self.world.world_model.edge_goal:
            self.bot = BasicBot(self.environment, [False], 'asocial', 0)
        
        self.bot.observe(self.p.pos, 0.2, None)

        if following is not None:
            
            self.p.pos = self.players[following].pos
            
            self.bot = BasicBot(self.environment, [False], 'asocial', 0)

        else:
            
            self.bot.act(self.p, [])
            self.p.go_slow()
            
            self.world.advance()
        
        if add:
            self.centers += [np.copy(self.p.pos)]
        else:
            self.centers += [None]
