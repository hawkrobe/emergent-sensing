
import numpy as np
import utils
import scipy.stats
from scipy.misc import logsumexp
import environment
import copy

import sys
sys.path.append("../utils/")
import stats

class Model():

    def __init__(self, model_type, sizes = [484,280], min_speed = 2.125, max_speed = 7.125, n_samples = 5):

        self.sizes = sizes
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.n_samples = n_samples
        self.last_weights = None
        self.pos_limits = environment.World().pos_limits
        self.second_to_last_angle = None
        self.last_angle = None
        self.last_loc = None
        self.last_speed = None

        self.samples = np.array([model_type() for i in range(n_samples)])
        self.pars = np.array([self.prior() for i in range(n_samples)])
        #self.likelihoods = np.zeros(n_samples)
        self.marginal_like = 0.0

    
    # implementing rasample requires being careful about where second_to_last and last angle
    # are set. can't set them in observe, because then resample will be wrong.
    #
    # def resample(self, loc, second_to_last_angle, last_angle, this_angle, speed, goal):
    #     """
    #     >>> m = Model()
    #     >>> m.resample(np.array([10.0,10.0]), 0.0, 0.0, 0.0, 7, None) is not None
    #     True
    #     >>> m.resample(np.array([10.0,10.0]), 10.0, 20.0, 30.0, 2.125, np.array([10.0,10.0]))
    #     array([ 10.,  10.])
    #     >>> sum(abs(m.resample(np.array([10.25,10.25]), 0.0, 0.0, 0.0, 7, np.array([10.25,10.25])) - np.array([10.25,10.25]))) > 1e-8
    #     True
    #     """

    #     if goal is None:
    #         prob_resample = 1
    #     else:
    #         prob_resample = 1 - np.exp(self.likelihood(loc, second_to_last_angle, last_angle, this_angle, speed, goal))
    #     if np.random.random() < prob_resample:
    #         return self.samples[np.random.choice(len(self.samples))].copy()
    #     else:
    #         return goal

    # takes in current location, angle, and speed before next action
    # (per observation model, described in README, current location is
    # the one that resulted from the last angle and speed)
    def observe(self, loc, this_angle, speed, bg_val, others, time):
        
        if self.second_to_last_angle is None:
            self.second_to_last_angle = self.last_angle
            self.last_angle = this_angle
            self.last_loc = loc
            self.last_speed = speed
            return

        self.transition()
        
        new_samples = []
        weights = []
        #likelihoods = []
        #new_weights = []
        for i in range(len(self.samples)):
            #w = []
            #for attention in [True, False]:
            #    for social in [True, False]:
            new_samples += [copy.deepcopy(self.samples[i])]
            new_samples[-1].observe(loc, bg_val, others, time)#, attention, social)
            lik = self.likelihood(self.last_loc, self.second_to_last_angle, self.last_angle, this_angle, self.last_speed, speed,
                                  new_samples[-1], self.pars[i])
            #prior = new_samples[-1].atom_log_prob(attention, social)
            #likelihoods += [self.likelihoods[i] + lik]
            weights += [lik]# + prior]
            #w += [lik + prior]
            #new_weights += [logsumexp(w)]

        weights = np.array(weights)

        # new_weights = np.array(new_weights)
        #if self.last_weights is None:
        self.marginal_like += logsumexp(weights - len(weights))
        #else:
        #    self.marginal_like += logsumexp(self.last_weights + weights)
        
        norm = logsumexp(weights)
        weights -= norm
        weights = np.exp(weights)
        
        #self.last_weights = copy.deepcopy(weights)
        
        inds = np.random.choice(len(new_samples), size = self.n_samples, p = weights)
        #from collections import Counter
        #c = Counter(inds)
        #print c[max(c)]
        
        new_samples = np.array(new_samples)
        #likelihoods = np.array(likelihoods)
        
        #self.likelihoods = likelihoods[inds]
        self.samples = copy.deepcopy(new_samples[inds])
        self.pars = copy.deepcopy(self.pars[inds])
        
        self.second_to_last_angle = copy.copy(self.last_angle)
        self.last_angle = copy.copy(this_angle)
        self.last_loc = copy.copy(loc)
        self.last_speed = copy.copy(speed)
    
    def likelihood(self, loc, second_to_last_angle, last_angle, this_angle, last_speed, speed, sample, par, verbose = False):

        obs_loc = utils.get_new_pos(loc, this_angle, speed, self.pos_limits)
        
        last_change = utils.angle_between(second_to_last_angle, last_angle)
        
        last_turn = self.get_turn(last_change)
        goal = sample.act(None)#, par)
        
        last_toward = utils.get_new_pos(loc, (last_angle + last_change) % 360, last_speed, self.pos_limits)
        if np.linalg.norm(last_toward - goal) < np.linalg.norm(loc - goal):
            expected_loc = last_toward
        else:
            expected_move = utils.get_move_towards(loc, last_angle, goal, self.min_speed, self.max_speed, last_turn, self.world.pos_limits, self.world.shape)
            expected_speed = self.min_speed if expected_move['speed'] == 'slow' else self.max_speed
            expected_loc = utils.get_new_pos(loc, (last_angle + expected_move['angle']) % 360, expected_speed, self.world.pos_limits, self.world.shape)
            
        model_like = -sum((obs_loc - expected_loc)**2) / 7.125
        dummy_like = -sum((obs_loc - last_toward)**2) / 7.125
        
        p = 1.0/(1 + np.exp(-par))
        return logsumexp([model_like + np.log(p), dummy_like + np.log(1 - p)])

    def prior(self):
        return np.log(np.random.random()) # * np.sqrt(np.sum(np.array(self.sizes)**2))
    
    def transition(self):
        self.pars += np.random.normal(size = self.n_samples) * 0.01
            
    def get_turn(self, angle):
        """
        >>> m = Model(lambda: None)
        >>> m.get_turn(30)
        'left'
        >>> m.get_turn(-30)
        'right'
        >>> m.get_turn(0)
        'none'
        """
        
        if abs(angle) < 1:
            turn = 'none'
        elif angle % 360 > 180:
            turn = 'right'
        else:
            turn = 'left'
        return turn
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
