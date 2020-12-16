
import numpy as np
import sys
sys.path.append("../utils/")
import stats

import utils

class Cacher():

    def __init__(self, world, memory = 4, others_mem = 16):

        self.memory = memory
        self.positions = [None for i in range(self.memory)]
        self.scores = [0 for i in range(self.memory)]
        self.others = [None for i in range(others_mem)]
        self.pos_limits = world.pos_limits
        self.shape = world.shape
        self.min_speed = world.min_speed
    
    def observe(self, loc, obs, others = None):
        """
        >>> from rectangular_world import RectangularWorld
        >>> m = Cacher(RectangularWorld(None), others_mem = 5)
        >>> x = [m.observe(i, i + 1) for i in range(10)]
        >>> m.positions
        [array(6), array(7), array(8), array(9)]
        >>> m.scores
        [7, 8, 9, 10]
        >>> m.others
        [None, None, None, None, None]
        >>> x = [m.observe(i, i + 1, i + 2) for i in range(10)]
        >>> m.others
        [7, 8, 9, 10, 11]
        """
        
        self.positions = self.positions[1:] + [np.copy(loc)]
        self.scores = self.scores[1:] + [obs]
        if others is not None:
            self.others = self.others[1:] + [others]

    def get_normal_fit(self):
        """
        >>> mu = np.array([10,100])
        >>> cov = np.array([[10,-5],[-5,20]])
        >>> samples = np.random.multivariate_normal(mu, cov, size = 10000)
        >>> from rectangular_world import RectangularWorld
        >>> m = Cacher(RectangularWorld(None), memory = len(samples))
        >>> x = [m.observe(s, 0) for s in samples]
        >>> m1,s = m.get_normal_fit()
        >>> assert np.linalg.norm(mu - m1) < 1
        >>> assert np.linalg.norm(cov - s) < 1
        """
        return stats.get_normal_fit(np.array(self.positions, dtype = float))
    
    def high_score(self):
        return np.mean(self.scores[-2:]) > 0.95 or self.scores[-1] == 1.0
    
    def score_increasing(self):
        return np.mean(self.scores[:self.memory/2]) < np.mean(self.scores[-self.memory/2:])

    def spinning_or_not(self):

        spins = []
        
        if self.others[0] is None:
            return spins
        
        for i in range(len(self.others[0])):
            
            if spinning([self.others[j][i] for j in range(len(self.others))]):
                spins += [True]
            else:
                spins += [False]
        
        return spins
    
    def spinning_people(self):

        spins = []
        
        if self.others[0] is None:
            return spins
        
        for i in range(len(self.others[0])):
            
            if spinning([self.others[j][i] for j in range(len(self.others))]):
                spins += [self.others[-1][i]['position'].copy()]
        
        return spins
    
    def walled_people(self):

        walled = []
        
        if self.others[0] is None:
            return walled
        
        for i in range(len(self.others[0])):
            
            if self.walled([self.others[j][i] for j in range(len(self.others))]):
                walled += [self.others[-1][i]['position'].copy()]
        
        return walled

    def stopped_people(self):

        stopped = []
        
        if self.others[0] is None:
            return stopped
        
        for i in range(len(self.others[0])):
            
            if self.stopped([self.others[j][i] for j in range(len(self.others))]):
                stopped += [self.others[-1][i]['position'].copy()]
        
        return stopped
    
    def slow_people(self):

        slows = []
        
        if self.others[0] is None:
            return slows
        
        for i in range(len(self.others[0])):
            
            if going_slow([self.others[j][i] for j in range(len(self.others))]):
                slows += [self.others[-1][i]['position']]
        
        return slows

    def walled(self, data):
        """
        >>> from rectangular_world import RectangularWorld
        >>> m = Cacher(RectangularWorld(None))
        >>> d = [{'speed':1,'angle':0,'position':np.array([1,1])},{'speed':1,'angle':0,'position':np.array([1,1])},{'speed':1,'angle':0,'position':np.array([1,1])}]
        >>> m.walled(d)
        True
        >>> d = [{'speed':5,'angle':0,'position':np.array([1,1])},{'speed':1,'angle':0,'position':np.array([1,1])},{'speed':1,'angle':0,'position':np.array([1,1])}]
        >>> m.walled(d)
        False
        >>> d = [{'speed':1,'angle':10,'position':np.array([1,1])},{'speed':1,'angle':0,'position':np.array([1,1])},{'speed':1,'angle':0,'position':np.array([1,1])}]
        >>> m.walled(d)
        False
        >>> d = [{'speed':1,'angle':0,'position':np.array([20,20])},{'speed':1,'angle':0,'position':np.array([1,1])},{'speed':1,'angle':0,'position':np.array([1,1])}]
        >>> m.walled(d)
        False
        """
        
        for i in range(len(data)):
            if not utils.check_collision(data[i]['position'], self.pos_limits, self.shape, update = False, extended = True):
                return False
            if data[i]['speed'] > 1e-12:
                return False
        
        return True

    def stopped(self, data):
        
        if sum([data[i]['speed'] > 0 for i in range(len(data))]) > 0:
            return False
        else:
            return True
    
def spinning(data):
    """
    >>> d = [{'speed':1,'angle':0},{'speed':1,'angle':20},{'speed':1,'angle':40},{'speed':1,'angle':60}]
    >>> spinning(d)
    True
    >>> d = [{'speed':5,'angle':0},{'speed':1,'angle':20},{'speed':1,'angle':40},{'speed':1,'angle':60}]
    >>> spinning(d)
    False
    >>> d = [{'speed':1,'angle':0},{'speed':1,'angle':20},{'speed':1,'angle':0},{'speed':1,'angle':60}]
    >>> spinning(d)
    False
    >>> d = [{'speed':1,'angle':340},{'speed':1,'angle':0},{'speed':1,'angle':20},{'speed':1,'angle':40}]
    >>> spinning(d)
    True
    >>> d = [{'speed':1,'angle':40},{'speed':1,'angle':20},{'speed':1,'angle':0},{'speed':1,'angle':340}]
    >>> spinning(d)
    True
    """

    if sum([data[i]['speed'] > 3 for i in range(len(data))]) > 0:
        return False
    
    angles = np.array([data[i]['angle'] for i in range(len(data))])
    diffs = angles[1:] - angles[:-1]
    clockwise = diffs % 360 < 180
    counter = diffs % 360 > 180
    nonzeros = abs(diffs) > 0
    num1 = sum(clockwise * nonzeros)
    num2 = sum(counter * nonzeros)
    if num1 == (len(data) - 1) or num2 == (len(data) - 1):
        return True
    
    return False



def going_slow(data):
    """
    >>> d = [{'speed':5,'angle':0},{'speed':1,'angle':20},{'speed':1,'angle':40},{'speed':1,'angle':60}]
    >>> going_slow(d)
    False
    >>> d = [{'speed':1,'angle':0},{'speed':1,'angle':20},{'speed':1,'angle':0},{'speed':1,'angle':60}]
    >>> going_slow(d)
    True
    """

    if sum([data[i]['speed'] > 3 for i in range(len(data))]) > 0:
        return False
    else:
        return True


if __name__ == "__main__":
    import doctest
    doctest.testmod()

    
