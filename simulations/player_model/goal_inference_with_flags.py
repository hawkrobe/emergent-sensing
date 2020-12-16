
import numpy as np
import utils
import scipy.stats
from scipy.misc import logsumexp

import sys
sys.path.append("../utils/")
import stats

class Model():

    def __init__(self, sizes = [484,280], n_samples = 1000):

        self.sizes = sizes
        self.n_samples = n_samples
        self.samples = self.prior_sample(n_samples)
        self.last_obs = None
        self.last_angle = None
    
    def prior_sample(self, n = 1):
        """
        >>> m = Model()
        >>> x = m.prior_sample(10000)
        >>> np.min(x[:,0])
        0
        >>> np.max(x[:,0])
        483
        >>> np.min(x[:,1])
        0
        >>> np.max(x[:,1])
        279
        >>> assert np.mean(x[:,2]) < 0.6 and assert np.mean(x[:,2]) > 0.4
        >>> assert np.mean(x[:,3]) < 0.6 and assert np.mean(x[:,3]) > 0.4
        """
        return np.column_stack([np.random.choice(self.sizes[0],n),
                                np.random.choice(self.sizes[1],n),
                                np.random.choice([True, False], size = n),
                                np.random.choice([True, False], size = n)])
    
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
            prob_resample = 1 - np.exp(self.likelihood(loc, obs, [goal])[0])
        if np.random.random() < prob_resample:
            return self.samples[np.random.choice(len(self.samples))].copy()
        else:
            return goal
            
    def observe(self, pos, angle):
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
        
        if self.last_obs is None:
            self.last_pos = pos
            self.last_angle = angle
            return None

        obs - last_obs
        
        samples = self.transition(self.samples)
        
        weights = self.likelihood(loc, obs, samples)
            
        weights = np.array(weights)
        norm = logsumexp(weights)
        weights -= norm
        weights = np.exp(weights)
        
        samples = np.array(samples)
        
        inds = np.random.choice(len(samples), size = self.n_samples, p = weights)
        self.samples = samples[inds]

        self.last_obs = obs
        
        return weights

    # prove mixed exact/sampled particle filter is valid by showing a
    # sample from p(x)p(y|x) = p(y|x) sum_z p(x | z) p(z) can be
    # achieved by enumerating z, then sampling an x within each z and
    # weighting based on the likelihood
    def transition(self, samples):
        """
        >>> m = Model(sizes = [4,5])
        >>> x = m.transition([[1,2,False,False]])[:-1]
        >>> x[:,0:2]
        array([[0, 2],
               [1, 1],
               [2, 2],
               [1, 3],
               [1, 2]])
        >>> x = m.transition([[1,2,False,False],[3,4,False,False]])
        >>> x[0:5,0:2]
        array([[0, 2],
               [1, 1],
               [2, 2],
               [1, 3],
               [1, 2]])
        >>> x[6:11,0:2]
        array([[2, 4],
               [3, 3],
               [4, 4],
               [3, 5],
               [3, 4]])
        >>> y = [[1,2,False,False],[3,4,False,False]]
        >>> p = sum([np.sum(abs(m.transition(y)[5,0] - m.transition(y)[11,0])) > 0 for i in range(1000)])
        >>> assert p < 800 and p > 700
        >>> p = sum([np.sum(abs(m.transition(y)[5,1] - m.transition(y)[11,1])) > 0 for i in range(1000)])
        >>> assert p < 850 and p > 750
        >>> assert np.sum(abs(x[:,2] - np.array([False]*len(x)))) > 0 # will fail with low probability 
        >>> assert np.sum(abs(x[:,3] - np.array([False]*len(x)))) > 0 # will fail with low probability 
        """
        n_moves = 6
        n,m = np.array(samples).shape
        x = np.reshape(np.tile( np.array(samples), n_moves), (n_moves * n, m))
        inds = np.array(range(len(x)))
        x[(np.array(inds) % n_moves) == 0,0] -= 1
        x[(np.array(inds) % n_moves) == 1,1] -= 1
        x[(np.array(inds) % n_moves) == 2,0] += 1
        x[(np.array(inds) % n_moves) == 3,1] += 1
        x[(np.array(inds) % n_moves) == 5,0:2] = self.prior_sample(n)[:,0:2]
        x[:,2] = self.transition_binary(x[:,2])
        x[:,3] = self.transition_binary(x[:,3])
        
        return x
    
    def transition_binary(self, x):
        """
        >>> m = Model()
        >>> y = sum(m.transition_binary([0]*1000000))/1000000.0
        >>> assert y < 0.26 and y > 0.24 # will fail with low probability
        >>> y = sum(m.transition_binary([1]*1000000))/1000000.0
        >>> assert y < 0.76 and y > 0.74 # will fail with low probability
        """
        shift = np.random.choice([0,1], size = len(x))
        new = np.random.choice([0,1], size = len(x))
        x = shift * x + (1 - shift) * new
        return x
    
    def likelihood(self, loc, obs, x):
        """
        >>> m = Model()
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
        goals = x[:,0:2]
        has_goal = x[:,2]
        uses_spacebar = x[:,3]
        
        expected = self.score( self.dists(loc, x) )
        return -(obs - expected)**2/float(2*self.noise**2)# scipy.stats.norm.pdf(obs, expected, self.noise)
        #return (1 - self.noise)*scipy.stats.norm.pdf(obs, expected, 0.1) + self.noise

    def dists(self, loc, x):
        """
        >>> m = Model()
        >>> m.dists([0,0], np.array([[0,0]]))
        array([ 0.])
        >>> m.dists([1,3], np.array([[5,6]]))
        array([ 5.])
        >>> m.dists([1,3], np.array([[1,3],[5,6]]))
        array([ 0.,  5.])
        """
        return np.sqrt(np.sum((np.array(loc) - x)**2, 1)) 
        
    def score(self, dist):
        """
        >>> m = Model()
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

    def get_beliefs(self):
        """
        >>> m = Model(sizes = [3,4])
        >>> m.samples = np.array([[0,0.1],[1.3,2.5]])
        >>> m.get_beliefs()
        array([[ 0.5,  0. ,  0. ,  0. ],
               [ 0. ,  0. ,  0. ,  0.5],
               [ 0. ,  0. ,  0. ,  0. ]])
        """
        beliefs = np.zeros(self.sizes)
        for s in self.samples:
            x = min(max(0,round(s[0])),self.sizes[0]-1)
            y = min(max(0,round(s[1])),self.sizes[1]-1)
            beliefs[x,y] += 1
        beliefs = beliefs / np.sum(beliefs)
        return beliefs
        
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
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
