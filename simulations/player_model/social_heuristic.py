
import numpy as np
from collections import Counter

import smart_particle as inference
import heuristic

import random

import utils

import config

class SocialHeuristic():

    #def __init__(self, threshold, n_samples = 2, social_info = 'all', social_particles = False, infer_score = False, ideal = False, watch_others = True, infer_goals = True):
    def __init__(self, par, score_field_model, environment, n_samples = 1000, social_info = 'spinning', social_particles = False, infer_score = False, ideal = False, watch_others = True):
        
        #self.threshold = threshold
        
        self.social_info = social_info
        self.social_particles = social_particles
        self.ideal = ideal
        self.infer_score = infer_score
        self.watch_others = watch_others
        
        self.model = inference.Model(lambda: score_field_model(noise = par), n_samples = n_samples)
        
        #self.model = inference.Model(n_samples = n_samples, noise = par)

        self.world = environment(None)
        self.cache = heuristic.Cacher(self.world)
        self.turn = np.random.choice(['left','right'])

        self.goal = None
        self.belief = None

        self.last_pos = None
        self.time = -1

    def observe(self, pos, bg_val, others, time = None, ind = None):

        self.time = time

        self.cache.observe(pos, bg_val, others)
        
        if self.social_info == 'spinning':
            self.social = self.cache.spinning_people()
            #self.slow = self.cache.going_slow()
        elif self.social_info == 'stopped':
            self.social = self.cache.stopped_people()
        elif self.social_info == 'walled':
            self.social = self.cache.walled_people()
        else:
            assert self.social_info == 'all'
            self.social = [o['position'].copy() for o in others]

        if self.ideal:
            spins = self.cache.spinning_or_not()
            locs = [pos] + [others[i]['position'] for i in range(len(spins)) if spins[i]]
            locs = [pos] + [others[i]['position'] for i in range(len(others))]
            obs = [bg_val] + [others[i]['bg_val'] for i in range(len(others))]        
            self.model.observe(locs, obs)
        else:
            if self.social_particles:
                if self.last_pos is not None:
                    self.model.observe(self.last_pos, bg_val, self.social)
            else:
                if self.last_pos is not None:                    
                    self.model.observe(self.last_pos, bg_val)
            if self.infer_score:
                for s in self.social:
                    self.model.observe(s, 1.0)

        if self.last_pos is not None:
            self.goal = self.model.resample(self.last_pos, bg_val, self.goal)
        else:
            self.goal = self.model.world_model.prior_sample()[0]
        
        self.last_pos = pos
        self.last_bg = bg_val
                    
        # # see if your current sample is consistent.  if it's not,
        # # sample from each other player.  if none of them are
        # # consistent, sample a new draw from your private posterior
        # self.old_goal = self.goal
        # self.goal = self.model.resample(pos, bg_val, self.old_goal)
        # if (self.goal is not self.old_goal) and self.watch_others:
        #     self.old_goal = self.goal
        #     self.goal = self.model.resample(pos, bg_val, self.old_goal)
        #     for i in np.random.permutation(range(len(self.goal_models))):
        #         if i == ind:
        #             continue
        #         if self.goal is not self.old_goal:
        #             self.old_goal = self.goal_models[i].sample()
        #             self.goal = self.model.resample(pos, bg_val, self.old_goal)
    
    def act(self, p):

        # samples = self.model.samples
        # c = Counter([tuple(np.array(s,dtype=int)) for s in samples])
        # points = c.keys()
        # counts = [c[i] for i in points]
        # maxes = np.array([np.array(points[i]) for i in utils.which_max(counts, ties = 'all')])
        
        #if self.goal is None:
        #    self.goal = p.pos
        
        # if bg_val >= 1.0#self.threshold:
        #     self.goal = pos
        # else:
        #     if len(self.social) > 0:
        #         self.goal = np.mean(self.social, 0) + 20*np.random.random(2) - 10
                
        #     if tuple(np.array(self.goal,dtype=int)) not in points:
        #         self.goal = utils.closest(self.goal, maxes)
    
        # p.go_towards(self.goal)
        
        if self.last_bg >= 1.0: # self.threshold:
            g = self.last_pos
        else:
            if len(self.social) > 0 and self.watch_others:# and (random.random() < 1/8.0):
                g = np.mean(self.social, 0)# + 20*np.random.random(2) - 10
            else:
                if self.world.edge_goal:
                    collision, sides = utils.check_collision(self.last_pos, self.world.pos_limits, self.world.shape, update = False, extended = True, return_side = True)
                    if collision:
                        g = next_corner(sides, self.world.pos_limits, self.turn)
                    else:
                        g = closest_wall(self.last_pos, self.world.pos_limits)
                else:
                    g = self.goal
        
        p.go_towards(g)
        
        return g
        
        #         #p.set_random_goal()
        #         #self.goal = p.goal
                
        #         #self.goal = utils.closest(p.pos, maxes)
        #         #if self.goal is None:
        #         #    self.goal = self.model.resample(p.pos, p.curr_background, self.goal)
        #         self.goal = self.model.resample(p.pos, p.curr_background, self.goal)
        #         p.go_towards(self.goal)
        #         if p.curr_background >= self.threshold:
        #             p.go_slow()
        
        # if p.curr_background >= 1.0:
        #     p.go_towards(p.pos)
        # else:
        #     p.go_towards(self.goal)
        #     #if np.linalg.norm(p.pos - self.goal) < self.threshold:
        #     #    p.go_slow()


        # if p.curr_background >= 1.0:
        #     p.go_towards(p.pos)
        # else:
        #     self.belief = self.model.resample(p.pos, p.curr_background, self.belief)
        #     if len(self.social) > 0:
        #         goal = 0.1 * np.mean(self.social, 0) + 0.9 * self.belief
        #     else:
        #         goal = self.belief
        #     p.go_towards(goal)

def next_corner(sides, pos_limits, turn):

    perturb = np.random.random(size = 2) * config.SIDE_WIDTH/2
    
    if turn == 'right':
        if 'top' in sides and not 'right' in sides:
            goal = np.array([pos_limits['x_max'] - perturb[0], pos_limits['y_max'] - perturb[1]])
        elif 'left' in sides:
            goal = np.array([pos_limits['x_min'] + perturb[0], pos_limits['y_max'] - perturb[1]]) 
        elif 'bottom' in sides:
            goal = np.array([pos_limits['x_min'] + perturb[0], pos_limits['y_min'] + perturb[1]]) 
        elif 'right' in sides:
            goal = np.array([pos_limits['x_max'] - perturb[0], pos_limits['y_min'] + perturb[1]]) 
        else:
            assert False
    if turn == 'left':
        if 'top' in sides and not 'left' in sides:
            goal = np.array([pos_limits['x_min'] + perturb[0], pos_limits['y_max'] - perturb[1]])
        elif 'right' in sides:
            goal = np.array([pos_limits['x_max'] - perturb[0], pos_limits['y_max'] - perturb[1]])
        elif 'bottom' in sides:
            goal = np.array([pos_limits['x_max'] - perturb[0], pos_limits['y_min'] + perturb[1]])
        elif 'left' in sides:
            goal = np.array([pos_limits['x_min'] + perturb[0], pos_limits['y_min'] + perturb[1]])
        else:
            assert False

    return goal

def closest_wall(pos, pos_limits):

    pos = np.copy(pos)
    
    projections = np.array([[pos_limits['x_min'], pos[1]],
                            [pos_limits['x_max'], pos[1]],
                            [pos[0], pos_limits['x_min']],
                            [pos[0], pos_limits['y_max']]])
    
    closest = np.argmin(np.abs(pos - projections))
    
    return projections[closest]

