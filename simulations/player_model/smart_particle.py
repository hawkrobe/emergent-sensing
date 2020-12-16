
import numpy as np
import utils
import scipy.stats
from scipy.special import logsumexp

import sys
sys.path.append("../utils/")
import stats

from spotlight_background_model import SpotlightBackground

class Model():

    def __init__(self, world_model = SpotlightBackground, n_samples = 1000):
        
        self.world_model = world_model()
        self.n_samples = n_samples
        self.samples = self.world_model.prior_sample(n_samples)

    def resample(self, loc, obs, goal):
        """
        >>> m = Model()
        >>> m.resample([10.25,10.25], 1, None) is not None
        True
        >>> m.resample([10.25,10.25], 1, [10.25,10.25])
        [10.25, 10.25]
        >>> sum(m.resample([10.25,10.25], 1, [100.25,100.25]) == [10.25, 10.25]) == 0
        True
        """

        if goal is None:
            prob_resample = 1
        else:
            prob_resample = 1 - np.exp(self.world_model.likelihood(loc, obs, [goal])[0])
        if np.random.random() < prob_resample:
            return self.samples[np.random.choice(len(self.samples))].copy()
        else:
            return goal
            
    def observe(self, loc, obs, others = None):
        """
        >>> m = Model(n_samples = 500)
        >>> x = [m.observe([100,250],1.0) for i in range(10)]
        >>> np.linalg.norm(np.mean(m.samples,0) - np.array([100,250])) < 25
        True
        >>> m = Model(n_samples = 500)
        >>> x = [m.observe([[100,250],[100,250]],[1.0,1.0]) for i in range(10)]
        >>> np.linalg.norm(np.mean(m.samples,0) - np.array([100,250])) < 25 # multi match, TODO: fix
        True
        >>> m = Model(n_samples = 500)
        >>> x = [m.observe([[100,250],[0,0]],[1.0,1.0]) for i in range(10)]
        >>> np.linalg.norm(np.mean(m.samples,0) - np.array([100,250])) < 25 # multi mismatch, TODO: fix
        False
        """
        
        # samples = []
        
        # if others is not None and len(others) > 0:
        #     assert False # TODO: fix
        #     samples += list(others)

        samples = self.world_model.transition(self.samples)
        
        if len(np.array(loc).shape) == 1:
            weights = self.world_model.likelihood(loc, obs, samples)
        else:
            assert False # TODO: fix
            weights = []
            for i in range(len(samples)):
                weights += np.sum(np.array([self.world_model.likelihood(loc[j], obs[j], samples[i]) for j in range(len(loc))]))
        
        weights = np.array(weights)
        norm = logsumexp(weights)
        weights -= norm
        weights = np.exp(weights)
        
        samples = np.array(samples)

        inds = np.random.choice(len(samples), size = self.n_samples, p = weights)
        
        self.samples = samples[inds]
        
        return weights

    def get_beliefs(self):
        # """
        # >>> m = Model(world_model = lambda: SpotlightBackground(sizes = [3,4]))
        # >>> m.samples = np.array([[0,0.1],[1.3,2.5]])
        # >>> m.get_beliefs()
        # array([[ 0.5,  0. ,  0. ,  0. ],
        #        [ 0. ,  0. ,  0. ,  0.5],
        #        [ 0. ,  0. ,  0. ,  0. ]])
        # """
        return self.samples#self.world_model.get_beliefs(self.samples)
        
    def get_uncertainty(self):
        """
        >>> m = Model()
        >>> u1 = m.get_uncertainty()
        >>> x = [m.observe([100,250],0.0) for i in range(10)]
        >>> u2 = m.get_uncertainty()
        >>> x = [m.observe([100,250],1.0) for i in range(10)]        
        >>> u3 = m.get_uncertainty()
        >>> u3 < u1
        True
        >>> u3 < u2
        True
        """
        
        return stats.bounding_oval(self.samples) 

    def get_normal_fit(self):
        
        return stats.get_normal_fit(self.samples)
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
