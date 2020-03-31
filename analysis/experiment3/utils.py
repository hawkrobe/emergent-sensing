
from scipy.special import logsumexp
import numpy as np
import copy

import config

def which_min(x, ties = 'random'):
    """
    >>> which_min([2,1,2])
    array([1])
    >>> sorted(set([j[0] for j in [which_min([1,2,1]) for i in range(100)]]))
    [0, 2]
    """
    x = np.array(x)
    y = np.argwhere(np.nanmin(x) == x)
    if ties == 'random':
        return y[np.random.choice(len(y))]
    elif ties == 'all':
        return y

def which_max(x, ties = 'random'):
    """
    >>> which_max([[1,2,1],[1,1,1]])
    array([0, 1])
    >>> which_max([[1,1,1],[1,2,1]])
    array([1, 1])
    >>> sorted(set([(j[0],j[1]) for j in [which_max([[2,1,2],[1,2,1]]) for i in range(100)]]))
    [(0, 0), (0, 2), (1, 1)]
    >>> which_max([[2,1,2],[1,2,1]], ties = 'all')
    array([[0, 0],
           [0, 2],
           [1, 1]])
    """
    x = np.array(x)
    y = np.argwhere(np.nanmax(x) == x)
    if ties == 'random':
        return y[np.random.choice(len(y))]
    elif ties == 'all':
        return y

def closest(pos, x):
    """
    >>> closest(np.array([0,0]), np.array([[0, 0]]))
    array([0, 0])
    >>> closest(np.array([0,0]), np.array([[0, 0],[0, 2],[1, 1]]))
    array([0, 0])
    >>> closest(np.array([0,0]), np.array([[0, 2],[1, 1]]))
    array([1, 1])
    >>> sorted(set([(j[0],j[1]) for j in [closest(np.array([0,0]), np.array([[1, 0],[0, 1]])) for i in range(100)]]))
    [(0, 1), (1, 0)]
    """    
    return x[which_min(np.sum((pos - x)**2,1))][0]

def get_new_pos(pos, angle, speed, pos_limits, shape):
    """
    >>> from rectangular_world import RectangularWorld
    >>> from environment import *
    >>> w = World(RectangularWorld, debug = True)
    >>> pos = np.array([5,4])
    >>> angle = 90
    >>> speed = 1
    >>> get_new_pos(pos, angle, speed, w.world_model.pos_limits, 'rectangle')
    array([ 6.,  4.])
    >>> pos = np.array([1,1])
    >>> get_new_pos(pos, angle, speed, w.world_model.pos_limits, 'rectangle')
    array([ 2.5,  2.5])
    """
    r = speed
    theta = (angle - 90) * np.pi / 180.0
    new_dir = np.array([r * np.cos(theta), r * np.sin(theta)])
    new_pos = (pos + new_dir).copy()
    check_collision(new_pos, pos_limits, shape)
    return new_pos

def get_score(pos, time, bg_dir, pos_limits, line_width = 1401):
    """
    >>> from rectangular_world import RectangularWorld
    >>> from environment import *
    >>> w = World(RectangularWorld, debug = True)
    >>> get_score(np.array([2.1,2.9]), 0, '../test/', {'x_min':0,'x_max':10,'y_min':0,'y_max':10}, 25)
    0.86
    """
    
    with open(bg_dir + 't' + str(time) + '.csv') as f:

        x,y = np.round(pos)
        
        f.seek(line_width * x + y * 5)
        val = f.read(4)

    if check_collision(pos, pos_limits, 'rectangle', update = False):
        return 0.0
    else:
        return 1 - float(val)

def calculate_score(pos, center, radius, pos_limits, shape):
    """
    >>> calculate_score(np.array([10,10]), np.array([10,10]), 20, {'radius':40}, 'circle')
    1.0
    >>> calculate_score(np.array([20,20]), np.array([10,10]), 1, {'radius':40}, 'circle')
    0.2
    >>> calculate_score(np.array([10,10]), np.array([10,10]), 1, {'radius':1}, 'circle')
    0.0
    """

    if center is not None and np.linalg.norm(pos - center) < radius:
        val = 1.0
    else:
        val = config.LOW_SCORE
    
    return val

    
    # if center is not None and np.linalg.norm(pos - center) < radius:
    #     val = 1.0
    # else:
    #     val = config.LOW_SCORE
    
    # if check_collision(pos, pos_limits, shape, update = False, extended = True):
    #     return 0.0
    # else:
    #     return val

def wall_score(pos, center, radius, pos_limits, shape):
    """
    >>> wall_score(np.array([10,10]), np.array([10,10]), 20, {'radius':40}, 'circle')
    0.0
    >>> wall_score(np.array([20,20]), np.array([10,10]), 1, {'radius':40}, 'circle')
    0.0
    >>> wall_score(np.array([10,10]), np.array([10,10]), 1, {'radius':1}, 'circle')
    1.0
    """
    
    # collision = check_collision(pos, pos_limits, shape, update = False, extended = True)
    
    # if center is not None and np.linalg.norm(pos - center) < radius and collision:
    #     val = 1.0
    # elif collision:
    #     val = config.LOW_SCORE
    # else:
    #     val = 0.0
    
    if center is not None and np.linalg.norm(pos - center) < radius:
        val = 1.0
    else:
        val = config.LOW_SCORE
    
    return val
        
def check_collision(pos, pos_limits, shape, update = True, keep_towards = False, extended = False, return_side = False):
    """
    >>> from rectangular_world import RectangularWorld
    >>> from environment import *
    >>> w = World(RectangularWorld, debug = True)
    >>> p = w.players[0]
    >>> pos = [-1,1]
    >>> check_collision(pos, w.world_model.pos_limits, 'rectangle')
    True
    >>> pos
    [2.5, 2.5]
    >>> pos = [1000,1000]
    >>> check_collision(pos, w.world_model.pos_limits, 'rectangle')
    True
    >>> pos
    [482.5, 277.5]
    >>> pos = [1000,1000]
    >>> check_collision(pos, w.world_model.pos_limits, 'rectangle', update = False)
    True
    >>> pos
    [1000, 1000]
    >>> pos = [50,50]
    >>> check_collision(pos, w.world_model.pos_limits, 'rectangle', update = False)
    False
    >>> pos = np.array([50.0,-50.0])
    >>> check_collision(pos, {'radius':10}, 'circle', update = True)
    True
    >>> pos
    array([ 7.07106781, -7.07106781])
    >>> pos = np.array([50.0,-50.0])
    >>> check_collision(pos, {'radius':100}, 'circle', update = True)
    False
    >>> pos
    array([ 50., -50.])
    >>> pos = [-1,1]
    >>> check_collision(pos, w.world_model.pos_limits, 'rectangle', keep_towards = True)
    (True, [-7.5, -7.5])
    >>> pos
    [2.5, 2.5]
    >>> pos = [100,1]
    >>> check_collision(pos, w.world_model.pos_limits, 'rectangle', keep_towards = True)
    (True, [100, -7.5])
    >>> pos = [1,100]
    >>> check_collision(pos, w.world_model.pos_limits, 'rectangle', keep_towards = True)
    (True, [-7.5, 100])
    >>> pos = [1000, 100]
    >>> check_collision(pos, w.world_model.pos_limits, 'rectangle', keep_towards = True)
    (True, [492.5, 100])
    >>> pos = [100, 1000]
    >>> check_collision(pos, w.world_model.pos_limits, 'rectangle', keep_towards = True)
    (True, [100, 287.5])
    >>> pos = [1, 1000]
    >>> check_collision(pos, w.world_model.pos_limits, 'rectangle', keep_towards = True)
    (True, [-7.5, 287.5])
    >>> pos = [1000, 1]
    >>> check_collision(pos, w.world_model.pos_limits, 'rectangle', keep_towards = True)
    (True, [492.5, -7.5])
    >>> pos = [1000, 1000]
    >>> check_collision(pos, w.world_model.pos_limits, 'rectangle', keep_towards = True)
    (True, [492.5, 287.5])
    """
    
    collision = False
    if keep_towards:
        target_pos = copy.deepcopy(pos)
    
    if extended:
        extension = config.SIDE_WIDTH
    else:
        extension = 1e-12

    side = []

    if shape == 'rectangle':
        if pos[0] <= pos_limits["x_min"] + extension:
            collision = True
            side += ['left']
            if update:
                if extended:
                    pos[0] = pos_limits["x_min"] + extension/2.0
                else:
                    pos[0] = pos_limits["x_min"]
            if keep_towards:
                target_pos[0] = pos_limits["x_min"] - 10

        if pos[0] >= pos_limits["x_max"] - extension:
            collision = True
            side += ['right']
            if update:
                if extended:
                    pos[0] = pos_limits["x_max"] - extension/2.0
                else:
                    pos[0] = pos_limits["x_max"]
            if keep_towards:
                target_pos[0] = pos_limits["x_max"] + 10

        if pos[1] <= pos_limits["y_min"] + extension:
            collision = True
            side += ['bottom']
            if update:      
                if extended:          
                    pos[1] = pos_limits["y_min"] + extension/2.0
                else:
                    pos[1] = pos_limits["y_min"]
            if keep_towards:
                target_pos[1] = pos_limits["y_min"] - 10

        if pos[1] >= pos_limits["y_max"] - extension:
            collision = True
            side += ['top']
            if update:
                if extended:
                    pos[1] = pos_limits["y_max"] - extension/2.0
                else:
                    pos[1] = pos_limits["y_max"]
            if keep_towards:
                target_pos[1] = pos_limits["y_max"] + 10
    
    elif shape == 'circle':
        if np.linalg.norm(pos) > pos_limits["radius"]:
            collision = True
            if update or keep_towards:
                theta = np.arctan2(pos[1], pos[0])
                new_pos = pos_limits["radius"]*np.array([np.cos(theta), np.sin(theta)])
                if update:
                    pos[0] = new_pos[0]
                    pos[1] = new_pos[1]
                if keep_towards:
                    target_pos = copy.deepcopy(new_pos)
                    target_pos *= 2
    
    else:
        assert False

    if keep_towards:
        return collision, target_pos
    else:
        if return_side:
            return collision, side
        else:
            return collision

def get_move_towards(pos, angle, x, min_speed, max_speed, turn_pref, pos_limits, shape, max_angle = 40.0, goal_dist = None, stop_and_click = False):

    collision, target_pos = check_collision(x, pos_limits, shape, update = False, keep_towards = True)
    if collision:
        x = target_pos

    if stop_and_click:
        max_angle = 180
    
    # determine player movement decisions by how far player can move
    # by constantly turning at max angle
    diag = 1 / np.cos(np.radians( (180.0 - max_angle)/2.0 ))
    
    dist = np.linalg.norm(x - pos)
    if dist < min_speed * diag:
        if stop_and_click:
            move = {'speed':'stop','angle':0}
        else:
            move = {'speed':'slow','angle':(max_angle if turn_pref == 'left' else -max_angle)}
    else:
        theta = (angle - 90.0) * np.pi / 180.0
        towards = (x - pos)/dist
        angle = np.degrees(np.arctan2(towards[1],towards[0]) - theta) % 360
        if angle > 180.0:
            angle = -(360.0 - angle)
        if abs(angle) > max_angle:
            angle = np.sign(angle) * max_angle
        if dist < max_speed * diag:
            move = {'speed':'slow', 'angle':angle}
        else:
            move = {'speed':'fast', 'angle':angle}
    
    if (goal_dist is not None) and (dist < goal_dist):
        move['speed'] = 'slow'
    
    return move

def angle_between(last_angle, this_angle):
    """
    >>> angle_between(50.0, 50.0)
    0.0
    >>> angle_between(60.0, 50.0)
    -10.0
    >>> angle_between(50.0, 60.0)
    10.0
    >>> angle_between(350.0, 5.0)
    15.0
    >>> angle_between(5.0, 350.0)
    -15.0
    """

    turn_angle = (this_angle - last_angle) % 360
    turn_angle = turn_angle - 360 if turn_angle > 180 else turn_angle

    return turn_angle

if __name__ == "__main__":
    import doctest
    doctest.testmod()
