import copy
import sys
sys.path.append('../player_model/')

import utils
import config
import random

import numpy as np
import smart_particle as inference
from spotlight_background_discrete_model import SpotlightBackgroundDiscrete

class BasicBot():    
    def __init__(self, environment, social_vector, strategy, my_index,
                 noise = 0, prob_explore = 0.5, random_explore = False, log_file = None):
        self.strategy = strategy                
        assert strategy in ['asocial', 'smart', 'smart_but_lazy', 'naive_copy', 'move_to_center']
        
        self.noise = noise
        self.random_explore = random_explore
        self.prob_explore = prob_explore
        self.world = environment(None)
        self.last_pos = None
        self.total_score = 0
        self.time = -1
        
        self.state = 'exploring'
        self.last_state = 'exploring'
        self.explore_goal = None
        self.copy_goal = None
        self.exploit_goal = None
        
        self.my_index = my_index        
        social_vector[my_index] = False
        self.social_vector = [False]*len(social_vector) if strategy == 'asocial' else social_vector 

        if not self.random_explore:
            self.model = inference.Model(lambda: SpotlightBackgroundDiscrete(self.world.edge_goal),
                                         n_samples = 500)
            self.goal = self.model.resample(None, None, None)
        else :
            self.goal = self.world.get_random_position()
    
        self.force_goal = None
        self.inside_force = False
        self.turn = np.random.choice(['left','right'])

        self.copy_targeted = self.strategy in ['smart', 'smart_but_lazy']
        self.copy_close = self.strategy == 'smart_but_lazy'
        
    def observe(self, pos, bg_val, time):
        """
        determine current background value 
        """
        if self.last_pos is not None:
            if self.random_explore:
                self.goal = self.world.get_random_position()
            else:
                self.model.observe(self.last_pos, bg_val)
                self.goal = self.model.resample(self.last_pos, bg_val, self.goal)

        self.last_pos = pos
        self.last_bg = bg_val
        self.time = time
        self.total_score += bg_val
        
    def act(self, p, others, force_exploit = False, exploit_pos = None):
        """
        determine action for player p 
        """
        self.last_state = copy.copy(self.state)
        
        if self.inside_force or force_exploit:
            # In Exp. 2, we force bot to exploit
            g = self.force_exploit(p, exploit_pos)
            
        elif ((self.last_bg >= 0.8 and np.random.random() > self.noise)): 
            # All agents exploit at high background 
            self.force_goal = None
            g = self.exploit(p)

        elif self.strategy == 'asocial' :
            # asocial bot simply explores until finding good value then exploits
            g = self.explore(p)

        elif self.strategy == 'smart' :
            # smart copy targets exploiting partner if available
            g = self.copy(p, others)

        elif self.strategy ==  'naive_copy' :
            # naive_copy bot randomly chooses copy or explore goal
            if self.inside_exploration_action(p):
                g = self.explore(p)
            elif self.inside_copying_action(p, others) :
                g = self.copy(p, others)
            else :
                g = (self.explore(p) if np.random.random() > self.prob_explore
                     else self.copy(p, others))

        elif self.strategy == 'move_to_center' :
            if self.inside_exploration_action(p) :
                g = self.explore(p)
            else :
                empty_pos = any([other.last_pos is None for other in others])
                self.explore(p)
                g = (self.get_explore_goal() if np.random.random() > self.prob_explore or empty_pos
                     else self.get_center_goal(others))
                self.explore_goal = g
        if g is None :
            g = self.explore(p)            

        assert g is not None
        assert sum([x is not None for x in [self.explore_goal, self.exploit_goal, self.copy_goal, self.force_goal]]) == 1
        
        p.go_towards(g)
        slow = self.state == 'exploiting' and p.speed > 0
        if slow:
            p.go_slow()
                
        return g, slow

    def explore(self, p):
        """
        sets an exploration goal if agent does not already have one
        """
        self.exploit_goal = None
        self.copy_goal = None
        if self.inside_exploration_action(p):
            return self.explore_goal
        else :
            self.state = 'exploring'
            self.explore_goal = self.get_explore_goal()
            return self.explore_goal
    
    def exploit(self, p):        
        self.explore_goal = None
        self.copy_goal = None
        self.exploit_goal = self.last_pos
        self.turn = np.random.choice(['left','right'])        
        self.state = 'exploiting'
        return self.exploit_goal
    
    def copy(self, p, others):
        # if currently copying, keep copying that same person as long as they're still exploiting
        if self.copy_goal is not None :
            copy_target = others[self.copy_goal]
            if (np.linalg.norm(p.pos - copy_target.last_pos) > 4*self.world.min_speed
                and (copy_target.state == 'exploiting' or not self.copy_targeted)):
                return copy_target.last_pos

        # otherwise determine whether to copy someone new
        self.copy_goal = None
        candidates = []
        for i in range(len(others)):
            if not self.social_vector[i]:
                continue

            if others[i].last_pos is None:
                continue

            if self.copy_targeted and np.random.random() > self.noise:
                if (others[i].world.edge_goal != self.world.edge_goal) and not self.copy_close:
                    continue

                if not others[i].state == 'exploiting':
                    continue
            else:
                if others[i].state == 'copying':
                    continue            
            candidates += [i]

        # if there's anyone to copy, pick one
        if len(candidates) > 0 and np.random.random() > self.noise:            
            self.state = 'copying'
            self.force_goal = None
            self.explore_goal = None
            self.exploit_goal = None
            self.copy_goal = (candidates[get_closest(p.pos, [others[i].last_pos for i in candidates])]
                              if self.copy_close else np.random.choice(candidates))
        return others[self.copy_goal].last_pos if self.copy_goal is not None else None

    def inside_exploration_action(self, p):
        """
        returns true when agent p has an exploration goal and has not yet reached it
        """
        return (self.explore_goal is not None and
                np.linalg.norm(p.pos - self.explore_goal) > 4*self.world.min_speed)

    def inside_copying_action(self, p, others):
        """
        returns true when agent p has an exploration goal and has not yet reached it
        """
        return (self.copy_goal is not None and
                np.linalg.norm(p.pos - others[self.copy_goal].last_pos) > 4*self.world.min_speed)

    def get_explore_goal(self):
        """
        Etermine next location to explore. 
        If using edge goals, move to next corner when you hit the wall.
        Otherwise use random legal position.
        """
        if self.world.edge_goal and np.random.random() > self.noise:
            collision, sides = utils.check_collision(self.last_pos, self.world.pos_limits, self.world.shape,
                                                     update = False, extended = True, return_side = True)
            return (next_corner(sides, self.world.pos_limits, self.turn) if collision
                    else closest_wall(self.last_pos, self.world.pos_limits))
        else:
            collision = utils.check_collision(self.goal, self.world.pos_limits, self.world.shape,
                                              update = False, extended = True)
            return (get_legal_position(self.goal, self.world.pos_limits, self.world) if collision 
                    else self.goal)

    def get_center_goal(self, others):
        new_x = np.mean([other.last_pos[0] for other in others])
        new_y = np.mean([other.last_pos[1] for other in others])
        return np.array([new_x, new_y])

    def force_exploit(self, p, center):        
        if self.inside_force:
            if np.linalg.norm(p.pos - self.force_goal) < 2*self.world.min_speed:                
                self.inside_force = False
            return self.force_goal
        else :        
            self.force_goal = center
            self.inside_force = True        
            self.exploit_goal = None
            self.explore_goal = None
            self.copy_goal = None
            self.state = 'exploring'
            return self.force_goal

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
    determine nearest point lying on wall boundary
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
