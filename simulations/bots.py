import copy
import sys
sys.path.append('./player_model/')

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
        assert strategy in ['asocial', 'smart',  'naive_copy', 'move_to_center', 'move_to_closest']
        
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
    
        self.turn = np.random.choice(['left','right'])

        self.copy_targeted = self.strategy in ['smart']
        
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
        
    def act(self, p, others):
        """
        determine action for player p 
        """
        self.last_state = copy.copy(self.state)
            
        if ((self.last_bg >= 0.8 and np.random.random() > self.noise)): 
            # All agents exploit at high background 
            g = self.exploit(p)

        elif self.strategy == 'asocial' :
            # asocial bot simply explores until finding good value then exploits
            g = self.explore(p)

        elif self.strategy == 'smart' :
            # smart copy targets exploiting partner if available
            g = self.copy(p, others)

        elif self.strategy ==  'naive_copy' :
            # naive_copy bot randomly chooses copy or explore goal
            if self.inside_movement(p, self.explore_goal) :
                g = self.explore(p)
            elif self.inside_movement(p, self.copy_goal) :
                g = self.copy(p, others)
            else :
                g = (self.copy(p, others) if np.random.random() > self.prob_explore
                     else self.explore(p))

        elif 'move_to' in self.strategy :
            self.explore(p)
            if self.inside_movement(p, self.explore_goal) :
                g = self.explore(p)
            else :
                empty_pos = any([other.last_pos is None for other in others])
                other_pos = [other.last_pos for other in others]
                biased_goal = (self.get_center_goal(others) if self.strategy == 'move_to_center'
                               else other_pos[get_closest(self.last_pos, other_pos)])
                g = interpolate(self.get_explore_goal(), biased_goal, self.prob_explore)
                print('setting midpoint goal')
                self.explore_goal = g
                
        if g is None :
            g = self.explore(p)            

        assert g is not None
        assert sum([x is not None for x in [self.explore_goal, self.exploit_goal, self.copy_goal]]) == 1
        
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
        if self.inside_movement(p, self.explore_goal):
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
        # if you haven't yet reached the agent you're copying,
        # keep copying as long as they're still exploiting
        if self.inside_movement(p, self.copy_goal) :
            if not self.copy_targeted :
                return self.copy_goal

        # otherwise determine whether to copy someone new
        self.copy_goal = None
        candidates = []
        for i in range(len(others)):
            if not self.social_vector[i]:
                continue

            if others[i].last_pos is None:
                continue

            if self.copy_targeted and np.random.random() > self.noise:
                if (others[i].world.edge_goal != self.world.edge_goal) :
                    continue

                if not others[i].state == 'exploiting':
                    continue
            else:
                if others[i].state == 'copying':
                    continue            
            candidates += [i]

        # if there's anyone to copy, pick one of them
        if len(candidates) > 0 and np.random.random() > self.noise:            
            self.state = 'copying'
            self.explore_goal = None
            self.exploit_goal = None
            self.copy_goal = others[np.random.choice(candidates)].last_pos
        return self.copy_goal if self.copy_goal is not None else None

    def inside_movement(self, p, goal):
        """
        returns true when agent p has a goal and has not yet reached it
        """
        if goal is None :
            return False
        else :
            return np.linalg.norm(p.pos - goal) > 2*self.world.min_speed

    def get_explore_goal(self):
        """
        Etermine next location to explore. 
        If using edge goals, move to next corner when you hit the wall.
        Otherwise use random legal position.
        """
        collision = utils.check_collision(self.goal, self.world.pos_limits, self.world.shape,
                                          update = False, extended = True)
        return (get_legal_position(self.goal, self.world.pos_limits, self.world) if collision 
                else self.goal)

    def get_center_goal(self, others):
        new_x = np.mean([other.last_pos[0] for other in others])
        new_y = np.mean([other.last_pos[1] for other in others])
        return np.array([new_x, new_y])

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

def interpolate(v1, v2, w) :
    return w*v1 + (1-w)*v2

def get_closest(pos, cands):
    """
    >>> get_closest([0,0], [[-1,-1],[0,1],[2,0],[2,2]])
    1
    """
    return np.argmin(np.linalg.norm(np.array(pos) - np.array(cands), axis = 1))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
