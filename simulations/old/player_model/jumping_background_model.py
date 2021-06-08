
import numpy as np
import utils
import scipy.stats
from scipy.misc import logsumexp

import sys
sys.path.append("../utils/")
import stats

import copy

class JumpingBackgroundDecay():

    def __init__(self, radius = 207.9098, noise = 0.2, width = 0.01, amp = 1.50, jump_freq = 0.125):
        
        self.radius = radius
        self.noise = noise
        self.width = width
        self.amp = amp
        self.jump_freq = jump_freq

    def prior_sample(self, n = 1):
        return stats.random_circle(self.radius, n)
    
    # prove mixed exact/sampled particle filter is valid by showing a
    # sample from p(x)p(y|x) = p(y|x) sum_z p(x | z) p(z) can be
    # achieved by enumerating z, then sampling an x within each z and
    # weighting based on the likelihood
    def transition(self, samples):
        x = []
        for i in range(len(samples)):
            if np.random.random() < self.jump_freq:
                x += [self.prior_sample(n = 1)[0]]
            else:
                x += [copy.deepcopy(samples[i])]
        
        return x
            
    def likelihood(self, loc, obs, x):
        
        collision = utils.check_collision(loc, self.pos_limits, self.shape, update = False)
        if not collision:
            expected = self.score( self.dists(loc, x) )
        else:
            assert obs < 1e-12
            expected = np.array([0.0]*len(x))
        
        return -(obs - expected)**2/float(2*self.noise**2)

    def score(self, dist):
        value = 1 - self.amp * np.exp(-dist*self.width)
        return 1.0 - np.maximum(np.minimum(value, 1.0), 0.0)

    def dists(self, loc, x):
        return np.sqrt(np.sum((np.array(loc) - x)**2, 1))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
