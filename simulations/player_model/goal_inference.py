
import numpy as np
import utils
import scipy.stats
from scipy.misc import logsumexp
import environment

import sys
sys.path.append("../utils/")
import stats

class Model():

    def __init__(self, world, min_speed = 2.125, max_speed = 7.125, n_samples = 5, stop_and_click = False):

        self.world = world
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.n_samples = n_samples
        self.samples = self.prior_sample(n_samples)
        self.second_to_last_angle = None
        self.last_angle = None
        self.last_loc = None
        self.stop_and_click = stop_and_click
        
    def prior_sample(self, n = 1):
        """
        >>> from rectangular_world import RectangularWorld
        >>> m = Model(RectangularWorld('../test/'))
        >>> np.min(m.prior_sample(10000)[:,0])
        0.0
        >>> np.max(m.prior_sample(10000)[:,0])
        483.0
        >>> np.min(m.prior_sample(10000)[:,1])
        0.0
        >>> np.max(m.prior_sample(10000)[:,1])
        279.0
        """
        return np.array([self.world.get_random_position() for i in range(n)])

    def sample(self):
        """
        >>> from rectangular_world import RectangularWorld
        >>> m = Model(RectangularWorld('../test/'))
        >>> m.samples = np.array([[1,2],[3,4]])
        >>> set([tuple(m.sample()) for i in range(100)]) == set([(1,2),(3,4)])
        True
        >>> m.samples = np.array([[1.0,2.0],[1.0,2.0]])
        >>> x = m.sample()
        >>> tmp = [m.observe(np.array([100.0,100.0]), 30.0, 2.125) for i in range(10)]
        >>> x
        array([ 1.,  2.])
        """
        return self.samples[np.random.choice(len(self.samples))].copy()
    
    # implementing rasample requires being careful about where second_to_last and last angle
    # are set. can't set them in observe, because then resample will be wrong.
    #
    # def resample(self, loc, second_to_last_angle, last_angle, this_angle, speed, goal):
    #     """
    #     >>> m = Model(RectangularWorld('../test/'))
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
    def observe(self, loc, this_angle, speed):
        """
        >>> from environment import *
        >>> from rectangular_world import RectangularWorld
        >>> p = World(RectangularWorld, debug = True).players[0]
        >>> p.turn_pref = 'left'
        >>> p.pos = np.array([100.0,250.0])
        >>> p.angle = 0
        >>> p.speed = 0
        >>> pos = []
        >>> angle = []
        >>> speed = []
        >>> for i in range(10):
        ...     p.go_towards(np.array([100.0,250.0]))
        ...     p.update_pos()
        ...     pos += [p.pos]
        ...     angle += [p.angle]
        ...     speed += [p.speed]
        >>> m = Model(RectangularWorld('../test/'), n_samples = 100)
        >>> x = [m.observe(pos[i], angle[i], speed[i]) for i in range(len(pos)-2)]
        >>> np.linalg.norm(np.mean(m.samples,0) - np.array([100.0,250.0])) < 25
        True
        """

        if self.second_to_last_angle is None:
            self.second_to_last_angle = self.last_angle
            self.last_angle = this_angle
            self.last_loc = loc
            return
        
        samples = self.transition(self.samples)
        
        weights = []
        for i in range(len(samples)):
            weights += [self.likelihood(self.last_loc, self.second_to_last_angle, self.last_angle, this_angle, speed, samples[i])]
        
        weights = np.array(weights)
        norm = logsumexp(weights)
        weights -= norm
        weights = np.exp(weights)
        
        samples = np.array(samples)
        
        inds = np.random.choice(len(samples), size = self.n_samples, p = weights)

        #import pdb; pdb.set_trace()
        
        self.samples = samples[inds]

        self.second_to_last_angle = self.last_angle
        self.last_angle = this_angle
        self.last_loc = loc

    # prove mixed exact/sampled particle filter is valid by showing a
    # sample from p(x)p(y|x) = p(y|x) sum_z p(x | z) p(z) can be
    # achieved by enumerating z, then sampling an x within each z and
    # weighting based on the likelihood
    def transition(self, samples):
        """
        >>> from rectangular_world import RectangularWorld
        >>> m = Model(RectangularWorld('../test/'))
        >>> x = m.transition([[1,2]])[:-1]
        >>> x
        array([[0, 2],
               [1, 1],
               [2, 2],
               [1, 3],
               [1, 2]])
        >>> x = m.transition([[1,2],[3,4]])
        >>> x[0:5]
        array([[0, 2],
               [1, 1],
               [2, 2],
               [1, 3],
               [1, 2]])
        >>> x[6:11]
        array([[2, 4],
               [3, 3],
               [4, 4],
               [3, 5],
               [3, 4]])
        >>> assert np.sum(abs(x[5] - x[11])) > 0 # will fail with low probability 
        """
        n_moves = 6
        x = np.reshape(np.tile( np.array(samples), n_moves), (n_moves*len(samples),2))
        inds = np.array(range(len(x)))
        x[(np.array(inds) % n_moves) == 0,0] -= 1
        x[(np.array(inds) % n_moves) == 1,1] -= 1
        x[(np.array(inds) % n_moves) == 2,0] += 1
        x[(np.array(inds) % n_moves) == 3,1] += 1
        x[(np.array(inds) % n_moves) == 5,:] = self.prior_sample(n = len(samples))
        
        return x
            
    def likelihood(self, loc, second_to_last_angle, last_angle, this_angle, speed, x, verbose = False):
        """
        >>> from rectangular_world import RectangularWorld
        >>> m = Model(RectangularWorld('../test/'))
        >>> l1 = m.likelihood(np.array([100.0,100.0]),0.0,0.0,0.0,7.125,np.array([100.0,100.0]))
        >>> l2 = m.likelihood(np.array([100.0,100.0]),0.0,0.0,0.0,2.125,np.array([100.0,100.0]))
        >>> l3 = m.likelihood(np.array([100.0,100.0]),350.0,0.0,40.0,2.125,np.array([100.0,100.0]))
        >>> l4 = m.likelihood(np.array([100.0,100.0]),350.0,0.0,320.0,2.125,np.array([100.0,100.0]))
        >>> l5 = m.likelihood(np.array([100.0,100.0]),60.0,40.0,0.0,2.125,np.array([100.0,100.0]))
        >>> assert l1 < l2 and l2 < l3 and l4 < l3
        >>> l3
        -0.0
        >>> l5
        -0.0
        >>> l1 = m.likelihood(np.array([100.0,100.0]),125.0,125.0,125.0,7.125,np.array([120.0,120.0])) 
        >>> l2 = m.likelihood(np.array([100.0,100.0]),135.0,135.0,135.0,7.125,np.array([120.0,120.0])) 
        >>> l3 = m.likelihood(np.array([100.0,100.0]),125.0,125.0,135.0,7.125,np.array([120.0,120.0])) 
        >>> l4 = m.likelihood(np.array([100.0,100.0]),155.0,145.0,135.0,7.125,np.array([120.0,120.0])) 
        >>> print l2, l3, l4
        -0.0 -0.0 -0.0
        >>> assert l3 > l1
        >>> assert l2 > l1
        """
        
        #assert loc.dtype == float and x.dtype == float
        
        last_turn = self.get_turn(self.angle_between(second_to_last_angle, last_angle))
        expected_move = utils.get_move_towards(loc, last_angle, x, self.min_speed, self.max_speed, last_turn, self.world.pos_limits, self.world.shape, stop_and_click = self.stop_and_click)
        if expected_move['speed'] == 'stop':
            expected_speed = 0
        else:
            expected_speed = self.min_speed if expected_move['speed'] == 'slow' else self.max_speed
        expected_loc = utils.get_new_pos(loc, (last_angle + expected_move['angle']) % 360, expected_speed, self.world.pos_limits, self.world.shape)
        
        obs_loc = utils.get_new_pos(loc, this_angle, speed, self.world.pos_limits, self.world.shape)
        if verbose:
            print expected_move, expected_loc, obs_loc
        
        return -sum((obs_loc - expected_loc)**2) / 7.125

    def angle_between(self, last_angle, this_angle):
        """
        >>> from rectangular_world import RectangularWorld
        >>> m = Model(RectangularWorld('../test/'))
        >>> m.angle_between(50.0, 50.0)
        0.0
        >>> m.angle_between(60.0, 50.0)
        -10.0
        >>> m.angle_between(50.0, 60.0)
        10.0
        >>> m.angle_between(350.0, 5.0)
        15.0
        >>> m.angle_between(5.0, 350.0)
        -15.0
        """
        
        turn_angle = (this_angle - last_angle) % 360
        turn_angle = turn_angle - 360 if turn_angle > 180 else turn_angle
        
        return turn_angle
            
    def get_turn(self, angle):
        """
        >>> from rectangular_world import RectangularWorld
        >>> m = Model(RectangularWorld('../test/'))
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
    
    # def get_beliefs(self):
    #     """
    #     >>> from rectangular_world import RectangularWorld
    #     >>> m = Model(RectangularWorld('../test/',sizes = [3,4]))
    #     >>> m.samples = np.array([[0.0,0.1],[1.3,2.5]])
    #     >>> m.get_beliefs()
    #     array([[ 0.5,  0. ,  0. ,  0. ],
    #            [ 0. ,  0. ,  0. ,  0.5],
    #            [ 0. ,  0. ,  0. ,  0. ]])
    #     """
    #     beliefs = np.zeros(self.sizes)
    #     for s in self.samples:
    #         x = min(max(0.0,round(s[0])),self.sizes[0]-1)
    #         y = min(max(0.0,round(s[1])),self.sizes[1]-1)
    #         beliefs[x,y] += 1
    #     beliefs = beliefs / np.sum(beliefs)
    #     return beliefs

    def get_normal_fit(self):
        
        return stats.get_normal_fit(self.samples)
    
    def get_uncertainty(self):
        """
        >>> from rectangular_world import RectangularWorld
        >>> m = Model(RectangularWorld('../test/'))
        >>> u1 = m.get_uncertainty()
        >>> x = [m.observe(np.array([100.0,250.0]), i*20 % 360.0, 2.125) for i in range(10)]
        >>> u2 = m.get_uncertainty()
        >>> u2 < u1
        True
        """
        
        return stats.bounding_oval(self.samples) 
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
