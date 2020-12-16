
import numpy as np
import utils
import copy

import sys
sys.path.append("../utils/")
import stats

import pandas as pd

class CircularWorld():

    def __init__(self, noise_location):
        
        self.shape = 'circle'

        if noise_location is not None:
            self.centers = np.array(pd.read_csv(noise_location))
        
        self.tick_frequency = 125
        self.ticks_per_sec = 1000/125
        self.us_min_wage_per_tick = 7.25 / (60*60*(1000 / self.tick_frequency))
	self.round_length = 0.5
        self.max_bonus = 1.25
        self.game_length = int(self.round_length * 60 * self.ticks_per_sec)
        
        self.min_speed = 17 / float(self.ticks_per_sec)
        self.max_speed = 57 / float(self.ticks_per_sec)
        
        self.pos_limits = {
    	    "radius": 207.9098
        }
        
        self.center_radius = 20
        
    def get_random_position(self):
        """
        >>> w = CircularWorld('../test/')
        >>> len(w.get_random_position())
        2
        """
        return stats.random_circle(self.pos_limits['radius'], 1)[0]
    
    def get_random_angle(self):
        """
        >>> np.random.seed(1)
        >>> w = CircularWorld('../test/')
        >>> np.max([w.get_random_angle() for i in range(10000)])
        359.0
        >>> np.min([w.get_random_angle() for i in range(10000)])
        0.0
        """
        return np.floor(np.random.random() * 360)
    
    def get_score(self, pos, time):
        """
        >>> w = CircularWorld('../test/')
        >>> w.get_score(np.array([2.1,2.9]), 0)
        0.0
        """

        return utils.calculate_score(pos, self.centers[time], self.center_radius, self.pos_limits)
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
