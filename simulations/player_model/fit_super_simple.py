
import sys
import copy
import numpy as np
from scipy.misc import logsumexp

import utils

from environment import *

class Fit():

    def __init__(self, game_data = None, background_dir = None, player = None, test = False, stop_and_click = False):
        
        if game_data is not None:
            
            self.game_data = game_data.set_index(game_data['tick'])
            self.player = player
            
            players = list(set(game_data['pid']))
            self.n_players = len(players)
            self.player_index = dict(zip(players,range(self.n_players)))
            self.player_set = set(players)
            self.removed = set([])
            
            self.world = World(noise_location = background_dir, n_players = self.n_players, stop_and_click = stop_and_click)
            
            self.start = self.world.game_length / 3 - 1
            
        self.test = test

    # action model (observe, act, record loop):
    #
    # pos        speed      angle
    # x_{t - 1}  s_{t - 1}  a_{t - 1}
    # x_{t}      s_{t}      a_{t}
    #
    # s_{t}, a_{t} = action(x_{t - 1}, s_{t - 1} * a_{t - 1})
    # x_{t} = x_{t - 1} * s_{t} * a_{t} 
    #
    # i.e.,
    # at t, players observe position (t - 1), angle (t - 1), speed (t - 1)
    # take new action s_{t},  a_{t}
    # world executes action t - 1 -> t
    # write to file: x_{t}, s_{t},  a_{t}
    # 
    def fit_model(self, model_type):
        
        self.model = model_type()
        self.err = np.zeros(2)
        
        self.set_state(self.world, 0, initialize = True)
        
        for t in range(self.start):
            
            self.observe_state() # observe state t positions, angles and speeds
            self.set_state(self.world, t) # correct state t positions, angles, speeds, set state t + 1 angles/speeds
            self.world.advance() # generage state t + 1 positions, state is now t + 1
        
        self.predict_forwards()
        
        return self.err

    def predict_forwards(self):
        
        model_world = copy.deepcopy(self.world)
        real_world = copy.deepcopy(self.world)
        
        for time in range(self.start, self.world.game_length - 1):
            
            # observe state t positions, angles and speeds
            self.model.observe(*model_world.get_obs(self.player))
            
            # set state t + 1 angles/speeds
            self.model.act(model_world.players[self.player])
            self.set_state(model_world, time, self.player)
            self.set_state(real_world, time)
            
            # generage state t + 1 positions
            model_world.advance()
            real_world.advance()
            
            err = self.check_predictions(real_world, model_world)
            self.err += err
                        
        return model_world
    
    def set_state(self, world, t, exclude = None, initialize = False):
        """
        >>> import pandas as pd
        >>> f = Fit()
        >>> f.world = World(debug = True); f.n_players = 1
        >>> f.player_index = {'8605-9a6f4c83-affb-4f07-b33d-ffc725c9ec81':0}
        >>> f.game_data = pd.read_csv('../test/data.csv')
        >>> f.set_state(f.world, 2)
        >>> f.world.time
        0
        >>> f.world.players[0].pos
        array([ 181.214,  156.038])
        >>> f.world.players[0].angle
        280
        >>> f.world.players[0].speed
        2.125
        >>> f.world.players[0].curr_background
        0.73999999999999999
        >>> assert False # TODO: test exclusion
        >>> assert False # TODO: test multiplayer and player dropout
        """
        
        sub_plus = self.game_data.loc[[t + 1]]
        
        # assert len(sub) == 0 or len(sub) == self.n_players # FIX games where players drop out
        # stop recording error after player drops out
        
        for i in range(len(sub_plus)):
            
            pid = sub_plus.iloc[i]['pid']
            p_ind = self.player_index[pid]
            if p_ind == exclude:
                continue
            
            p = world.players[p_ind]
            
            sub = self.game_data.loc[[t]]
            sub = sub[sub['pid'] == pid].iloc[0]

            if initialize:
                p.angle = sub['angle']
                p.speed = sub['velocity']
            else:
                if self.test:
                    # make sure we are reading in the right backgrounds.
                    # one step observed positions should also be deterministic
                    assert np.linalg.norm( p.pos - np.array([ sub['x_pos'], sub['y_pos'] ]) ) < 0.01
                    assert abs(p.curr_background - sub['bg_val']) < 0.01
                p.angle = sub_plus.iloc[i]['angle']
                p.speed = sub_plus.iloc[i]['velocity']

            p.pos = np.array([sub['x_pos'], sub['y_pos']])
            p.curr_background = sub['bg_val']
    
    def observe_state(self):        
        self.model.observe(*self.world.get_obs(self.player))
    
    def check_predictions(self, true_world, simulated_world):

        expected = true_world.get_obs(self.player)
        observed = simulated_world.get_obs(self.player)
        
        bg_err = expected[1] - observed[1]
        
        social_err = social_dist(expected[0],expected[2]) - social_dist(observed[0],observed[2])
        
        return np.array([bg_err, social_err])

def social_dist(pos, others):
    """
    >>> social_dist(np.array([1,2]), [{'position':[0,3]},{'position':[2,1]}])
    0.0
    """

    mean = np.mean(np.array([p['position'] for p in others]), 0)

    return np.linalg.norm(pos - mean)
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
