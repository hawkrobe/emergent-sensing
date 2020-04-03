
import numpy as np
import pandas as pd
import utils
import copy

import config

class RectangularWorld():
    
    def __init__(self, noise_location, round_length = 6, full_noise_file = True, center_radius = None, edge_goal = False):
        
        if noise_location is not None:
            if full_noise_file:
                self.noise_location = noise_location + '/'
                with open(self.noise_location + 't0.csv') as f:
                    self.noise_line_width = len(f.readline())
                assert not edge_goal
            else:
                self.centers = np.array(pd.read_csv(noise_location))
        
        self.center_radius = center_radius
        self.edge_goal = edge_goal
        
        self.full_noise_file = full_noise_file
        
        self.world = config.WORLD
        self.shape = 'rectangle'
        
        self.tick_frequency = 125
        self.ticks_per_sec = 1000/125
        self.us_min_wage_per_tick = 7.25 / (60*60*(1000 / self.tick_frequency))
        self.round_length = round_length
        self.max_bonus = 1.25*6/self.round_length
        self.game_length = int(self.round_length * 60 * self.ticks_per_sec)
        
        self.min_speed = 17 / float(self.ticks_per_sec)
        self.max_speed = 57 / float(self.ticks_per_sec)
        
        self.size = config.SIZE
        
        self.pos_limits = config.POS_LIMITS
    
    def get_random_position(self):
        """
        >>> np.random.seed(1)
        >>> w = RectangularWorld('../test/')
        >>> np.round(np.max([w.get_random_position()[0] for i in range(10000)]))
        482.0
        >>> round(np.min([w.get_random_position()[0] for i in range(10000)]))
        3.0
        >>> round(np.min([w.get_random_position()[1] for i in range(10000)]))
        3.0
        >>> round(np.max([w.get_random_position()[1] for i in range(10000)]))
        277.0
        """
        
        pos = None
        
        if self.edge_goal:
            while True:
                pos = np.array([np.random.uniform(self.pos_limits["x_min"], self.pos_limits["x_max"]),
                                np.random.uniform(self.pos_limits["y_min"], self.pos_limits["y_max"])])
                if utils.check_collision(pos, self.pos_limits, self.shape, update = False, extended = True):
                    break
        else:
            pos = np.array([np.random.uniform(self.pos_limits["x_min"], self.pos_limits["x_max"]),
                            np.random.uniform(self.pos_limits["y_min"], self.pos_limits["y_max"])])
        
        return pos
    
    def get_random_angle(self):
        """
        >>> np.random.seed(1)
        >>> w = RectangularWorld('../test/')
        >>> np.max([w.get_random_angle() for i in range(10000)])
        359.0
        >>> np.min([w.get_random_angle() for i in range(10000)])
        0.0
        """
        return np.floor(np.random.random() * 360)
    
    
    def get_score(self, pos, time):
        """
        >>> w = RectangularWorld('../test/')
        >>> w.get_score(np.array([2.1,2.9]), 0)
        0.0
        """

        if self.full_noise_file:
            return utils.get_score(pos, time, self.noise_location, self.pos_limits, self.noise_line_width)
        else:
            if self.edge_goal:
                return utils.wall_score(pos, self.centers[time], self.center_radius, self.pos_limits, self.shape)
            else:
                return utils.calculate_score(pos, self.centers[time], self.center_radius, self.pos_limits, self.shape)
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
