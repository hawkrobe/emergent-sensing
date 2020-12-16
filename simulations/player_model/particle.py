
import numpy as np
import utils
import scipy.stats

class Model():

    def __init__(self, sizes = [484,280], noise = 0.2, width = 0.01, amp = 1.50, n_samples = 2):

        self.sizes = sizes
        self.noise = noise
        self.width = width
        self.amp = amp
        self.n_samples = n_samples
        self.samples = np.array([self.prior_sample() for i in range(n_samples)])
        self.weights = [None for i in range(n_samples)]

    def prior_sample(self):
        """
        >>> m = Model()
        >>> np.min([m.prior_sample()[0] for i in range(10000)])
        0
        >>> np.max([m.prior_sample()[0] for i in range(10000)])
        483
        >>> np.min([m.prior_sample()[1] for i in range(10000)])
        0
        >>> np.max([m.prior_sample()[1] for i in range(10000)])
        279
        """
        return np.array([np.random.choice(self.sizes[0]),np.random.choice(self.sizes[1])])

    def observe(self, loc, obs, others = None):
        """
        >>> m = Model(n_samples = 500)
        >>> x = [m.observe([100,250],1.0) for i in range(10)]
        >>> np.linalg.norm(np.mean(m.samples,0) - np.array([100,250])) < 25
        True
        """
        
        for i in range(self.n_samples):
            self.samples[i] = self.transition(self.samples[i])

        if others is not None and len(others) > 0:
            self.samples = np.vstack([self.samples,others])
        
        for i in range(self.n_samples):
            self.weights[i] = self.likelihood(loc, obs, self.samples[i])
        
        self.weights /= sum(self.weights)

        self.samples = self.samples[np.random.choice(self.n_samples, size = self.n_samples, p = self.weights)]
                
    
    def transition(self, x):
        y = np.copy(x)
        direction = np.random.choice(['left','right','up','down','stay','jump'])
        if direction == 'left':
            y[0] -= 1
        if direction == 'right':
            y[0] += 1
        if direction == 'up':
            y[1] -= 1
        if direction == 'down':
            y[1] += 1
        if direction == 'jump':
            y = self.prior_sample()
        return y
            
    def likelihood(self, loc, obs, x):
        """
        >>> m = Model()
        >>> m.likelihood([0,0],0,[0,0]) < m.likelihood([0,0],1,[0,0])
        True
        >>> m.likelihood([0,0],1,[0,0]) >= m.likelihood([100,100],1,[0,0]) 
        True
        """
        expected = self.score(np.linalg.norm(np.array(loc) - x))
        return (1 - self.noise)*scipy.stats.norm.pdf(obs, expected, 0.1) + self.noise
    
    def score(self, dist):
        """
        >>> m = Model()
        >>> m.score(0)
        1.0
        >>> m.score(1)
        1.0
        >>> m.score(100)
        0.5518191617571635
        """
        value = 1.0 - self.amp * np.exp(-dist*self.width)
        return 1.0 - np.maximum(np.minimum(value, 1.0), 0.0)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
