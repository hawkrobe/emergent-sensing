
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

    def observe(self, pos, bg_val, others, time):

        self.time = time
        self.last_score = bg_val
        self.last_pos = pos
        if self.goal_models is None:
            self.goal_models = [goal_inference.Model(self.environment(None), self.stop_and_click) for i in range(len(others))]

        self.model.observe(pos, bg_val)
        
        for i in range(len(others)):
            self.goal_models[i].observe(others[i]['position'], others[i]['angle'], others[i]['speed'])

        self.old_goal = self.goal
        self.goal = self.model.resample(pos, bg_val, self.old_goal)
        if self.goal is not self.old_goal:
            if self.watch_others and len(others) > 0:
                ind = np.random.choice(len(others))
                self.goal = self.model.resample(pos, bg_val, self.goal_models[ind].sample())

    def act(self, p):

        g = self.goal
        p.go_towards(g)
        return g
