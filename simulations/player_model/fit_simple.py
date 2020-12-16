
import sys
import copy
import numpy as np
from scipy.misc import logsumexp

import utils

from canvas import *
from environment import *

class Fit():

    def __init__(self, game_data = None, background_dir = None, player = None, debug = False, out_dir = None, test = False, reps = 30, stop_and_click = False):

        if game_data is not None:
            
            self.game_data = game_data.set_index(game_data['tick'])
            self.player = player
            
            players = list(set(game_data['pid']))
            self.n_players = len(players)
            self.player_index = dict(zip(players,range(self.n_players)))
            
            self.world = World(noise_location = background_dir, n_players = self.n_players, stop_and_click = stop_and_click)
            
            self.window = 160
            self.start = self.world.game_length / 3 - 1
            self.stop_training = self.world.game_length * 2 / 3 - 1
            
        self.grid = 50
        self.offset = np.array(np.array([np.random.random(), np.random.random()]) * self.grid, dtype = 'int')

        self.out_dir = out_dir
        self.recording = out_dir is not None
        self.test = test

        self.reps = reps

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
    def fit_model(self, model_type, par_settings):

        self.models = [model_type(par_settings[i]) for i in range(len(par_settings))]
        self.errs = np.zeros(len(par_settings))
        
        self.first = True

        self.set_state(self.world, 0, initialize = True)
        
        for t in range(self.world.game_length):

            if t == self.stop_training:
                print
                print self.errs
                best_par = par_settings[self.get_best_values()]
                self.errs = [0]
            
            if t >= self.start:
                
                if t % 100 == 0:
                    sys.stdout.write('.')
                    
                if self.first and self.out_dir is not None:
                    self.canvas = Canvas(self.out_dir)
                    self.first = False
                
                if self.is_predict_time(t):
                    
                    self.make_predictions(t)

            # making predictions should not change models or world
            assert self.world.time == t
            for i in range(len(self.models)):
                assert self.models[i].time == t - 1

            if t < self.world.game_length - 1:
                self.observe_state() # observe state t positions, angles and speeds
                self.set_state(self.world, t) # correct state t positions, angles, speeds, set state t + 1 angles/speeds
                self.world.advance() # generage state t + 1 positions, state is now t + 1
            
        print self.errs
        print

        return best_par, self.errs[0]

    def predict_forwards(self, model_ind, start, debug = False, return_full = False):
        """
        >>> from baseline_model import *
        >>> import pandas as pd
        >>> f = Fit()
        >>> f.errs = np.array([0])
        >>> f.game_data = pd.read_csv('../test/data.csv')
        >>> f.window = 2; f.player = 0; f.n_players = 1; f.player_index = {'8605-9a6f4c83-affb-4f07-b33d-ffc725c9ec81':0}
        >>> f.world = World(debug = True)
        >>> f.world.players[0].pos = np.array([100,100])
        >>> f.world.players[0].angle = 0
        >>> f.world.players[0].turn_pref = 'left'
        >>> f.models = [BaselineModel('straight')]
        >>> w = f.predict_forwards(0, 0)
        >>> w.time
        2
        >>> w.players[0].pos
        array([ 100.  ,   95.75])
        >>> f.world.players[0].pos
        array([100, 100])
        >>> f.window = 4;
        >>> f.models = [BaselineModel('straight')]
        >>> w = f.predict_forwards(0, 0)
        >>> w.players[0].pos
        array([ 100. ,   91.5])
        >>> f.window = 14;
        >>> f.models = [BaselineModel('spin')]
        >>> w = f.predict_forwards(0, 0)
        >>> w.players[0].pos
        array([ 100.81320229,  104.08824401])
        >>> f.models = [BaselineModel('spin')]
        >>> y = [1,2]; f.models[0].x = y
        >>> w,m = f.predict_forwards(0, 0, debug = True)
        >>> y[0] = 10
        >>> f.models[0].x[0] == m.x[0]
        False
        >>> assert False # TODO: test errs
        """
        
        model = copy.deepcopy(self.models[model_ind])
        model_world = copy.deepcopy(self.world)
        real_world = copy.deepcopy(self.world)

        model_traj = []
        real_traj = []
        
        if self.recording:
            self.canvas.reset_objects()
        
        time = start
        
        for i in range(self.window):

            if time >= self.world.game_length - 2:
                break
            
            # observe state t positions, angles and speeds
            model.observe(*model_world.get_obs(self.player))

            # set state t + 1 angles/speeds
            model.act(model_world.players[self.player])
            self.set_state(model_world, time, self.player)
            self.set_state(real_world, time)
            
            # generage state t + 1 positions
            model_world.advance()
            real_world.advance()

            model_traj += [copy.deepcopy(model_world.players[self.player].pos)]
            real_traj += [copy.deepcopy(real_world.players[self.player].pos)]
            #err = self.check_predictions(real_world, model_world)
            #self.errs[model_ind] += err
            
            if self.recording:
                self.record_state(real_world, model_world, model, model_ind)
            
            time += 1
            
        if debug:
            return model_world, model
        else:
            if return_full:
                return np.array(model_traj), np.array(real_traj)
            else:
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
        
        #world.time = t

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
                p.pos = np.array([sub['x_pos'], sub['y_pos']])
                p.curr_background = sub['bg_val']
                p.angle = sub['angle']
                p.speed = sub['velocity']
            else:

                if self.test:
                    # make sure we are reading in the right backgrounds.
                    # one step observed positions should also be deterministic
                    assert np.linalg.norm( p.pos - np.array([ sub['x_pos'], sub['y_pos'] ]) ) < 0.01
                    assert abs(p.curr_background - sub['bg_val']) < 0.01
                
                p.pos = np.array([sub['x_pos'], sub['y_pos']])
                p.curr_background = sub['bg_val']
                
                p.angle = sub_plus.iloc[i]['angle']
                p.speed = sub_plus.iloc[i]['velocity']
    
    def record_state(self, real_world, model_world, model, model_ind):

        if model.model is not None:
            self.canvas.plot(copy.deepcopy(model.model.samples), 'beliefs')
        self.canvas.plot_previous()
        for j in range(len(model_world.players)):
            if j != self.player:
                self.canvas.plot(copy.deepcopy(model_world.players[j]), 'other')
        self.canvas.plot(copy.deepcopy(real_world.players[self.player]), 'real')#, str(int(err)) + ',' + str(int(self.errs[model_ind])))
        self.canvas.plot(copy.deepcopy(model_world.players[self.player]), 'simulated')
        self.canvas.advance()
    
    def observe_state(self):
        
        obs = self.world.get_obs(self.player)
        
        for i in range(len(self.models)):
            self.models[i].observe(*obs)
        
        return obs
    
    def get_best_values(self):
        """
        >>> f = Fit()
        >>> f.models = [['a'],['b'],['c','e'],['d']]
        >>> f.errs = np.array([1,3,0,5])
        >>> f.get_best_values()
        >>> f.models
        [['c', 'e']]
        """
        ind = utils.which_min(self.errs)
        self.models = [self.models[ind]]
        return ind
    
    def is_predict_time(self, t):
        """
        >>> f = Fit()
        >>> f.window = 10
        >>> f.world = World(debug = True)
        >>> f.world.game_length = 2880
        >>> f.is_predict_time(9)
        False
        >>> f.is_predict_time(10)
        True
        >>> f.is_predict_time(11)
        False
        >>> f.is_predict_time(20)
        True
        >>> f.is_predict_time(2870)
        True
        >>> f.is_predict_time(2880)
        False
        """
        return (t % self.window == 0) and (t + self.window <= self.world.game_length)
    
    def make_predictions(self, t):

        for i in range(len(self.models)):

            traj = None
            for j in range(self.reps):                
                model_traj, real_traj = self.predict_forwards(i, t, return_full = True)
                if traj is None:
                    traj = model_traj
                else:
                    traj += model_traj
            traj /= float(self.reps)
            
            self.errs[i] += np.sum(np.abs(traj - real_traj))
        
    def check_predictions(self, true_world, simulated_world, score = 'distance'):
        """
        >>> f = Fit()
        >>> f.player = 0
        >>> w1 = World(n_players = 2, debug = True)
        >>> w2 = copy.deepcopy(w1)
        >>> w1.players[0].pos = np.array([0,3])
        >>> w2.players[0].pos = np.array([4,0])
        >>> f.check_predictions(w1, w2)
        5.0
        >>> f.player = 1
        >>> f.check_predictions(w1, w2)
        0.0
        >>> f = Fit()
        >>> f.offset = np.array([0,0])
        >>> f.player = 0
        >>> w1 = World(n_players = 2, debug = True)
        >>> w2 = copy.deepcopy(w1)
        >>> w1.players[0].pos = np.array([0,3])
        >>> w2.players[0].pos = np.array([4,0])
        >>> f.check_predictions(w1, w2, score = 'binary')
        False
        >>> w1.players[0].pos = np.array([100,13])
        >>> w2.players[0].pos = np.array([4,0])
        >>> f.check_predictions(w1, w2, score = 'binary')
        True
        >>> f.player = 1
        >>> f.check_predictions(w1, w2, score = 'binary')
        False
        """
        if score == 'distance':
            return np.linalg.norm(true_world.players[self.player].pos - simulated_world.players[self.player].pos)
        elif score == 'binary':
            return self.get_grid_loc(true_world.players[self.player].pos) != self.get_grid_loc(simulated_world.players[self.player].pos)

    def get_grid_loc(self, pos):
        """
        >>> f = Fit()
        >>> f.offset = np.array([0,0])
        >>> f.get_grid_loc(np.array([1,0]))
        (0, 0)
        >>> f.grid = 10
        >>> f.offset = np.array([9,9])
        >>> f.get_grid_loc(np.array([1,0]))
        (1, 0)
        """
        return tuple((np.array(pos,dtype=int) + self.offset) / self.grid)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
