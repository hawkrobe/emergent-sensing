
import numpy as np
from collections import Counter
import random
from scipy.misc import logsumexp

import smart_particle as inference
import goal_inference

import copy

import utils

class RationalModel():

    def __init__(self, pars, score_field_model, environment, memory = 16, n_samples = 500, watch_others = True, stop_and_click = False):
        
        self.par = pars
        #self.memory = memory
        self.watch_others = watch_others
        
        self.model = inference.Model(lambda: score_field_model(noise = pars), n_samples = n_samples)
        self.environment = environment
        
        self.goal = None
        self.belief = None
        self.goal_models = None
        self.last_score = None
        self.last_pos = None
        
        self.time = -1

        self.stop_and_click = stop_and_click

        #self.likes = None

    def observe(self, pos, bg_val, others, time):

        self.time = time
        self.last_score = bg_val
        self.last_pos = pos


        # if self.likes is None:
        #     self.likes = [[] for i in range(len(others) + 1)]
        
        #self.cache.observe(pos, bg_val, others)
        if self.goal_models is None:
            self.goal_models = [goal_inference.Model(self.environment(None), self.stop_and_click) for i in range(len(others))]

        # g = self.model.samples[np.random.choice(len(self.model.samples))]
        # if len(self.likes[-1]) >= self.memory:
        #     self.likes[-1] = self.likes[-1][1:] + [self.model.likelihood(pos, bg_val, [g])[0]]
        # else:
        #     self.likes[-1] = self.likes[-1] + [self.model.likelihood(pos, bg_val, [g])[0]]
        
        self.model.observe(pos, bg_val)
        
        for i in range(len(others)):
            
            self.goal_models[i].observe(others[i]['position'], others[i]['angle'], others[i]['speed'])
            
        #     g = self.goal_models[i].sample()
        #     if len(self.likes[i]) >= self.memory:
        #         self.likes[i] = self.likes[i][1:] + [self.model.likelihood(pos, bg_val, [g])[0]]
        #     else:
        #         self.likes[i] = self.likes[i] + [self.model.likelihood(pos, bg_val, [g])[0]]
        
        # if self.memory == 0:
        #     weights = np.ones(len(self.likes))/float(len(self.likes))
        # else:
        #     weights = np.array([sum(self.likes[i]) for i in range(len(self.likes))])
        #     norm = logsumexp(weights)
        #     weights = np.exp(weights - norm)
        
        #if (self.goal is None) or (np.random.random() < self.attention):
        # see if your current sample is consistent.  if it's not,
        # sample from each other player.  if none of them are
        # consistent, sample a new draw from your private posterior
        self.old_goal = self.goal
        self.goal = self.model.resample(pos, bg_val, self.old_goal)
        if (self.goal is not self.old_goal):
            #self.old_goal = self.goal
            #self.goal = self.model.resample(pos, bg_val, self.old_goal)
            if self.watch_others and len(others) > 0:
                #ind = np.random.choice(len(weights), p = weights)
                #if ind < (len(weights) - 1):
                ind = np.random.choice(len(others))
                self.goal = self.model.resample(pos, bg_val, self.goal_models[ind].sample())
                # for i in np.random.permutation(range(len(self.goal_models))):
                #     if self.goal is not self.old_goal:
                #         self.old_goal = self.goal_models[i].sample()
                #         self.goal = self.model.resample(pos, bg_val, self.old_goal)
    
    def act(self, p):

        g = self.goal
        p.go_towards(g)
        
        return g
        
        #if p.curr_background >= 1.0:
        #    p.go_towards(p.pos)
        #else:
        #p.go_towards(self.goal)
            #if np.linalg.norm(p.pos - self.goal) < self.threshold:
            #    p.go_slow()
            
