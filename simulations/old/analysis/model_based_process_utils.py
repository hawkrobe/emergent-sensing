
import pandas as pd
import numpy as np

from scipy.misc import logsumexp

import sys
sys.path.append("../player_model/")
sys.path.append("../utils/")

import stats

import environment as env
import smart_particle as inference
import goal_inference
import heuristic as cache

class Processor():

    def __init__(self, data, inactive):
        
        self.inference_model = inference.Model()

        active_players = get_active_players(data, inactive)
        self.player_data = dict([(p, data.loc[data['pid'] == p,:].copy()) for p in active_players])
        for p in self.player_data:
            self.player_data[p].index = self.player_data[p].tick
        
        self.ticks = sorted(set(data['tick']))
        
        self.goal_models = {}
        self.caches = {}

        for p in self.player_data:
            
            self.goal_models[p] = goal_inference.Model(n_samples = 100)
            self.caches[p] = cache.Model(memory = 16)

    def set_goals(self, p, t):
    
        if t not in self.player_data[p]['tick']:
            return

        self.goal_models[p].observe(np.array([self.player_data[p].loc[t,'x_pos'],
                                              self.player_data[p].loc[t,'y_pos']]),
                                    self.player_data[p].loc[t,'angle'],
                                    self.player_data[p].loc[t,'velocity'])

        mean, cov = self.goal_models[p].get_normal_fit()
        self.processed_data[p][t]['goal_mean'] = mean
        self.processed_data[p][t]['goal_cov'] = cov

    def set_pos_dist(self, p, t):

        if t not in self.player_data[p]['tick']:
            return

        self.caches[p].observe(np.array([self.player_data[p].loc[t,'x_pos'],
                                         self.player_data[p].loc[t,'y_pos']]),
                               self.player_data[p].loc[t,'bg_val'])
        
        if t - self.caches[p].memory not in self.player_data[p]['tick']:
            return
        
        mean, cov = self.caches[p].get_normal_fit()
        self.processed_data[p][t]['pos_mean'] = mean
        self.processed_data[p][t]['pos_cov'] = cov
        
    def set_weights(self, p, t):

        if t not in self.player_data[p]['tick']:
            return

        if t - self.caches[p].memory not in self.player_data[p]['tick']:
            return
        
        for q in self.player_data:

            if p == q:
                continue

            if t not in self.player_data[q]['tick']:
                continue
            
            self.fit_weighted_dist(p, t, np.array(self.caches[q].positions).copy(), 'pos-' + str(q))
            self.fit_weighted_dist(p, t, self.goal_models[q].samples.copy(), 'goal-' + str(q))
            
    def fit_weighted_dist(self, p, t, samples, label):
        
        weights = self.inference_model.likelihood(np.array([self.player_data[p].loc[t,'x_pos'],
                                                            self.player_data[p].loc[t,'y_pos']]),
                                                  self.player_data[p].loc[t,'bg_val'],
                                                  samples)
        
        weights = np.array(weights)
        norm = logsumexp(weights)
        
        self.processed_data[p][t][label + '_prob'] = np.exp(norm) / float(len(weights))
        
        weights -= norm
        weights = np.exp(weights)

        inds = np.random.choice(len(samples), size = 1000, p = weights)
        samples = samples[inds]
        
        mean, cov = stats.get_normal_fit(samples)
        self.processed_data[p][t][label + '_mean'] = mean
        self.processed_data[p][t][label + '_cov'] = cov

    def update_characteristics(self, p, t):

        self.set_pos_dist(p, t)

        # it's important for this to come after new positions are cached
        # and before new goals are set
        self.set_weights(p, t)

        self.set_goals(p, t)

        
    def process_data(self, verbose = True):
        """
        >>> ticks = range(50) + range(49)
        >>> x = [0]*50 + [1]*49
        >>> success, df, m = process_data(pd.DataFrame({'tick':ticks,'pid':x,'x_pos':x,'y_pos':x,'velocity':x,'angle':x,'bg_val':x}),{}, verbose = False)
        >>> len(df)
        99
        """

        if len(self.player_data) == 0:
            return False, None

        self.processed_data = {}
        for p in self.player_data:
            self.processed_data[p] = {}

        for t in self.ticks:
            
            if t % 100 == 0 and verbose:
                print 'init', t
            
            for p in self.player_data:
                
                if t not in self.player_data[p]['tick']:
                    continue
                
                self.processed_data[p][t] = {}
                
                self.update_characteristics(p, t)

        return True, self.processed_data

def get_active_players(data, inactive):
    """
    >>> get_active_players(pd.DataFrame({'pid':['a','a','b','c','c','d'],'x_pos':[1,1,np.nan,1,1,1]}), {'d':True})
    ['a', 'c']
    """
    
    active_players = []
    
    for p in set(data['pid']):
        
        if p in inactive:
            continue
        
        if sum(np.isnan(data.loc[data['pid']==p,'x_pos'])) > 0:
            continue
        
        active_players += [p]
    
    return active_players

if __name__ == "__main__":
    import doctest
    doctest.testmod()
