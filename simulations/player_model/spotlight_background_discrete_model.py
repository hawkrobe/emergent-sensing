
import numpy as np
import utils
import scipy.stats
from scipy.special import logsumexp

import sys
sys.path.append("../utils/")
import stats

import config

class SpotlightBackgroundDiscrete():

    def __init__(self, edge_goal, sizes = [484,280], width = config.DISCRETE_BG_RADIUS, prop = 0.2):

        self.sizes = sizes
        self.width = width
        self.prop = prop

        self.pos_limits = config.POS_LIMITS
        self.shape = 'rectangle'
        self.edge_goal = edge_goal

    def prior_sample(self, n = 1):
        """
        >>> m = SpotlightBackgroundDiscrete()
        >>> np.min(m.prior_sample(10000)[:,0])
        0
        >>> np.max(m.prior_sample(10000)[:,0])
        483
        >>> np.min(m.prior_sample(10000)[:,1])
        0
        >>> np.max(m.prior_sample(10000)[:,1])
        279
        """
        return np.column_stack([np.random.choice(self.sizes[0],n), np.random.choice(self.sizes[1],n)])
        
    # prove mixed exact/sampled particle filter is valid by showing a
    # sample from p(x)p(y|x) = p(y|x) sum_z p(x | z) p(z) can be
    # achieved by enumerating z, then sampling an x within each z and
    # weighting based on the likelihood
    def transition(self, samples):
        """
        >>> m = SpotlightBackgroundDiscrete()
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

    def likelihood(self, loc, obs, x):
        """
        >>> m = SpotlightBackgroundDiscrete()
        >>> m.likelihood(np.array([100,100]), 1.0, np.array([[100,100]]))
        array([ 0.])
        >>> m.likelihood(np.array([100,100]), 1.0, np.array([[100,100],[150,100]]))
        array([ 0., -1.])
        >>> m.likelihood(np.array([100,100]), 0.2, np.array([[100,100],[150,100]]))
        array([       -inf, -0.45867515])
        """

        # TODO: remove edge collision weirdness
        assert obs > 0
        
        expected = self.score( self.dists(loc, x) )
        
        #if obs == 0 or (self.edge_goal != collision):
        #    return np.array([0.0]*len(x))
        
        top = abs(obs - 1.0) < 1e-12

        val = top*expected + (1 - top)*(1 - expected)
        
        return np.log(val)
        
    def score(self, dist):
        """
        >>> m = SpotlightBackgroundDiscrete()
        >>> m.score(0)
        1.0
        >>> m.score(10)
        1.0
        >>> m.score(40)
        1.0
        >>> m.score(41) < 1.0
        True
        >>> abs(m.score(50) - np.exp(-1)) < 1e12
        True
        >>> m.score(np.array([0,10,41,50]))
        array([ 1.        ,  1.        ,  0.90483742,  0.36787944])
        """
        
        sure_width = self.width * (1 - self.prop)
        
        within = dist < sure_width
        
        return within + (1 - within) * np.exp(-(dist - sure_width)/(self.width - sure_width))
    
    def dists(self, loc, x):
        """
        >>> m = SpotlightBackgroundDiscrete()
        >>> m.dists([0,0], np.array([[0,0]]))
        array([ 0.])
        >>> m.dists([1,3], np.array([[5,6]]))
        array([ 5.])
        >>> m.dists([1,3], np.array([[1,3],[5,6]]))
        array([ 0.,  5.])
        """
        return np.sqrt(np.sum((np.array(loc) - x)**2, 1))

    def get_beliefs(self, samples):
        beliefs = np.zeros(self.sizes)
        for s in samples:
            x = min(max(0,round(s[0])),self.sizes[0]-1)
            y = min(max(0,round(s[1])),self.sizes[1]-1)
            beliefs[x,y] += 1
        beliefs = beliefs / np.sum(beliefs)
        return beliefs

if __name__ == "__main__":
    import doctest
    doctest.testmod()
