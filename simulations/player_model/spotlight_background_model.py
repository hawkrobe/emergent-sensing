
import numpy as np
import utils
import scipy.stats
from scipy.special import logsumexp

import sys
sys.path.append("../utils/")
import stats

class SpotlightBackground():

    def __init__(self, sizes = [484,280], noise = 0.2, width = 0.01, amp = 1.50):

        self.sizes = sizes
        self.noise = noise
        self.width = width
        self.amp = amp

    def prior_sample(self, n = 1):
        """
        >>> m = SpotlightBackground()
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
        >>> m = SpotlightBackground()
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
        >>> m = SpotlightBackground()
        >>> m.likelihood([0,0],0,np.array([[0,0]])) < m.likelihood([0,0],1,np.array([[0,0]]))
        array([ True], dtype=bool)
        >>> m.likelihood([0,0],1,[[0,0]]) >= m.likelihood([100,100],1,[[0,0]]) 
        array([ True], dtype=bool)
        >>> l = m.likelihood([100,100],1,[[0,0],[100,100]])
        >>> l[0] < l[1]
        True
        >>> l1 = m.likelihood([100,90],1,[[100,100]])
        >>> l2 = m.likelihood([100,110],1,[[100,100]])
        >>> abs(l1 - l2) < 1e-12
        array([ True], dtype=bool)
        """
        expected = self.score( self.dists(loc, x) )
        return -(obs - expected)**2/float(2*self.noise**2)# scipy.stats.norm.pdf(obs, expected, self.noise)
        #return (1 - self.noise)*scipy.stats.norm.pdf(obs, expected, 0.1) + self.noise

    def score(self, dist):
        """
        >>> m = SpotlightBackground()
        >>> m.score(0)
        1.0
        >>> m.score(1)
        1.0
        >>> m.score(100)
        0.5518191617571635
        >>> m.score(np.array([100, 1]))
        array([ 0.55181916,  1.        ])
        """
        value = 1 - self.amp * np.exp(-dist*self.width)
        return 1.0 - np.maximum(np.minimum(value, 1.0), 0.0)

    def dists(self, loc, x):
        """
        >>> m = SpotlightBackground()
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
