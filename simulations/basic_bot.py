  
import numpy as np
import copy

import sys
sys.path.append('../player_model/')

import utils
import config

import smart_particle as inference
from spotlight_background_discrete_model import SpotlightBackgroundDiscrete

class BasicBot():
    
    def __init__(self, environment, social_vector, social_rule, my_index, noise = 0, random_explore = False, log_file = None):
                
        assert social_rule in ['smart','naive','eager','asocial','lazy']
        
        self.noise = noise
        self.random_explore = random_explore
        
        self.world = environment(None)
        
        self.last_pos = None
        self.time = -1
        
        self.state = 'exploring'
        self.last_state = 'exploring'

        self.explore_goal = None
        self.copy_goal = None
        self.exploit_goal = None
        
        self.my_index = my_index
        
        social_vector[my_index] = False
        self.social_vector = social_vector

        if not self.random_explore:
            self.model = inference.Model(lambda: SpotlightBackgroundDiscrete(self.world.edge_goal), n_samples = 500)
        
        self.force_goal = None
        self.inside_force = False

        self.turn = np.random.choice(['left','right'])
        
        self.social_rule = social_rule
        
        if social_rule == 'eager':
            self.copy_first = True
            self.social_rule = 'smart'
        else:
            self.copy_first = False
        
        if social_rule == 'lazy':
            self.social_rule = 'smart'
            self.copy_close = True
        else:
            self.copy_close = False
        
        if social_rule == 'asocial':
            self.social_vector = [False]*len(social_vector)
        
        self.inferred_center = None

        if self.random_explore:
            self.goal = self.world.get_random_position()
        else:
            self.goal = self.model.resample(None, None, None)
        
        # self.log_file = log_file
        
        # self.log_file.write(' '.join(map(str, [self.time, self.my_index, 'noise', self.noise, '\n'])))
        # self.log_file.write(' '.join(map(str, [self.time, self.my_index, 'social_rule', self.social_rule, '\n'])))
        # self.log_file.write(' '.join(map(str, [self.time, self.my_index, 'social_vector', self.social_vector, '\n'])))

    def observe(self, pos, bg_val, time):
        
        if self.last_pos is not None:
            if self.random_explore:
                self.goal = self.world.get_random_position()
            else:
                self.model.observe(self.last_pos, bg_val)
                self.goal = self.model.resample(self.last_pos, bg_val, self.goal)

        self.last_pos = pos
        self.last_bg = bg_val
        self.time = time
        
        # self.log_file.write(' '.join(map(str, [self.time, self.my_index, 'observed', pos, bg_val, '\n'])))
        # self.log_file.write(' '.join(map(str, [self.time, self.my_index, 'goal', self.goal, '\n'])))
    
    def act(self, p, others, force_exploit = False, exploit_pos = None):
        
        self.last_state = copy.copy(self.state)

        if self.inside_force:
            
            g = self.force_exploit(p, exploit_pos)
            
        elif (self.last_bg >= 0.8 and np.random.random() > self.noise) and (not self.copy_first or self.socially_consistent_center(p, others)):

            self.force_goal = None
            g = self.exploit(p)
        
        elif force_exploit:

            g = self.force_exploit(p, exploit_pos)
            
        else:

            self.force_goal = None
            self.exploit_goal = None
            self.inferred_center = None

            if self.social_rule == 'naive':
                if not self.inside_exploration_action(p):
                    g = self.copy(p, others)
            else:
                g = self.copy(p, others)
            
            if self.state == 'copying':
                
                self.explore_goal = None
                
            else:
                
                if self.copy_first and (self.last_bg >= 1.0 and np.random.random() > self.noise):
                    
                    g = self.exploit(p)
                
                else:
                    
                    g = self.explore(p)                
                
        assert g is not None
        assert sum([x is not None for x in [self.explore_goal, self.exploit_goal, self.copy_goal, self.force_goal]]) == 1
        
        # self.log_file.write(' '.join(map(str, [self.time, self.my_index, 'state', self.state, '\n'])))
        # self.log_file.write(' '.join(map(str, [self.time, self.my_index, 'final_goal', g, '\n'])))
        
        p.go_towards(g)
        slow = self.state == 'exploiting' and p.speed > 0
        if slow:
            p.go_slow()
                
        return g, slow

    def socially_consistent_center(self, p, others):
        
        for i,o in enumerate(others):
            
            if self.social_vector[i] and o.state == 'exploiting' and np.linalg.norm(p.pos - o.last_pos) < self.world.min_speed:#config.DISCRETE_BG_RADIUS:
                return True
        
        return False

    def inside_exploration_action(self, p):

        if self.explore_goal is not None:
            if np.linalg.norm(p.pos - self.explore_goal) > 2*self.world.min_speed:
                return True
        
        return False

    def explore(self, p):
        
        if self.inside_exploration_action(p):
            return self.explore_goal
        
        self.state = 'exploring'
        self.explore_goal = self.get_explore_goal()

        # self.log_file.write(' '.join(map(str, [self.time, self.my_index, 'explore_goal', self.explore_goal, '\n'])))

        return self.explore_goal

    def force_exploit(self, p, center):
        
        if self.inside_force:

            g = self.force_goal
            
            if np.linalg.norm(p.pos - self.force_goal) < 2*self.world.min_speed:
                
                self.inside_force = False
                
            return g

        self.inside_force = True
        
        self.exploit_goal = None
        self.explore_goal = None
        self.copy_goal = None
        
        self.state = 'exploring'
        return self.get_force_exploit_goal(center)

    def exploit(self, p):
        
        self.explore_goal = None
        self.copy_goal = None

        self.turn = np.random.choice(['left','right'])
        
        self.state = 'exploiting'
        return self.get_exploit_goal(p)
    
    def copy(self, p, others):

        if self.copy_goal is not None:
            if self.social_rule != 'smart' or others[self.copy_goal].state == 'exploiting':
                if np.linalg.norm(p.pos - others[self.copy_goal].last_pos) > self.world.max_speed:
                    return others[self.copy_goal].last_pos
        
        self.copy_goal = None

        candidates = []

        for i in range(len(others)):

            if not self.social_vector[i]:
                continue

            if others[i].last_pos is None:
                continue

            if self.social_rule == 'smart' and np.random.random() > self.noise:

                if (others[i].world.edge_goal != self.world.edge_goal) and not self.copy_close:
                    continue

                if not others[i].state == 'exploiting':
                    continue
            else:
                if others[i].state == 'copying':
                    continue
            
            candidates += [i]

        # self.log_file.write(' '.join(map(str, [self.time, self.my_index, 'copy_candidates', candidates, '\n'])))
        
        if len(candidates) > 0 and np.random.random() > self.noise:
            
            self.state = 'copying'

            if self.copy_close:
                ind = candidates[get_closest(p.pos, [others[i].last_pos for i in candidates])]
            else:
                ind = np.random.choice(candidates)
            
            # self.log_file.write(' '.join(map(str, [self.time, self.my_index, 'copy', ind, '\n'])))

            self.copy_goal = ind #np.copy(others[ind].last_pos)

        else:
            
            self.state = 'exploring'
        
        # self.log_file.write(' '.join(map(str, [self.time, self.my_index, 'copy_goal', self.copy_goal, '\n'])))
        
        if self.copy_goal is not None:
            return others[self.copy_goal].last_pos
        else:
            return None

    def get_force_exploit_goal(self, center):
        
        self.force_goal = center
        
        # self.log_file.write(' '.join(map(str, [self.time, self.my_index, 'exploit_goal', self.exploit_goal, '\n'])))
        
        return self.force_goal

    def get_exploit_goal(self, p):

        self.exploit_goal = self.last_pos

        # self.log_file.write(' '.join(map(str, [self.time, self.my_index, 'exploit_goal', self.exploit_goal, '\n'])))
        
        return self.exploit_goal

    def get_explore_goal(self):
        
        goal_collision = utils.check_collision(self.goal, self.world.pos_limits, self.world.shape, update = False, extended = True)

        if self.world.edge_goal and np.random.random() > self.noise:
            collision, sides = utils.check_collision(self.last_pos, self.world.pos_limits, self.world.shape, update = False, extended = True, return_side = True)
            if collision:
                g = next_corner(sides, self.world.pos_limits, self.turn)
            else:
                g = closest_wall(self.last_pos, self.world.pos_limits)
        else:
            if goal_collision:
                g = get_legal_position(self.goal, self.world.pos_limits, self.world)
            else:
                g = self.goal
        
        return g
    
def next_corner(sides, pos_limits, turn):
    
    perturb = np.random.random(size = 2) * config.SIDE_WIDTH
    
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

def closest_wall(pos, pos_limits, index = False):
    """
    >>> pos_limits = {'x_min':0,'x_max':200,'y_min':0,'y_max':100}
    >>> closest_wall(np.array([10,50]), pos_limits)
    array([ 0, 50])
    >>> closest_wall(np.array([20,90]), pos_limits)
    array([ 20, 100])
    >>> closest_wall(np.array([190,80]), pos_limits)
    array([200,  80])
    >>> closest_wall(np.array([190,5]), pos_limits)
    array([190,   0])
    """
    
    pos = np.copy(pos)
    
    projections = np.array([[pos_limits['x_min'], pos[1]],
                            [pos_limits['x_max'], pos[1]],
                            [pos[0], pos_limits['y_min']],
                            [pos[0], pos_limits['y_max']]])
    
    closest = np.argmin(np.sum(np.abs(pos - projections), axis = 1))
    
    if index:
        return closest
    else:
        return projections[closest]

def get_legal_position(pos, pos_limits, world):
    
    pos = np.copy(pos)
    
    if world.edge_goal:
        offset = config.SIDE_WIDTH - world.max_speed
    else:
        offset = config.SIDE_WIDTH + world.max_speed
    
    if pos[0] <= pos_limits["x_min"] + config.SIDE_WIDTH:
        pos[0] = pos_limits["x_min"] + offset

    if pos[0] >= pos_limits["x_max"] - config.SIDE_WIDTH:
        pos[0] = pos_limits["x_max"] - offset
    
    if pos[1] <= pos_limits["y_min"] + config.SIDE_WIDTH:
        pos[1] = pos_limits["y_min"] + offset
    
    if pos[1] >= pos_limits["y_max"] - config.SIDE_WIDTH:
        pos[1] = pos_limits["y_max"] - offset

    return pos


# http://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python/13849249#13849249
def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

    >>> angle_between((1, 0, 0), (0, 1, 0))
    1.5707963267948966
    >>> angle_between((1, 0, 0), (1, 0, 0))
    0.0
    >>> angle_between((1, 0, 0), (-1, 0, 0))
    3.1415926535897931
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def get_closest(pos, cands):
    """
    >>> get_closest([0,0], [[-1,-1],[0,1],[2,0],[2,2]])
    1
    """
    return np.argmin(np.linalg.norm(np.array(pos) - np.array(cands), axis = 1))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
