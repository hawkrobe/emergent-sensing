
import pandas as pd
import numpy as np

import sys
sys.path.append("../player_model/")

import environment as env
import smart_particle as inference

slow_dist = 17/8.0
fast_dist = 57/8.0

lookback = 4
spin_lookback = 4

facing_angle = np.radians(45)# 2*np.pi / 6

# angle is specified w.r.t. top, needs to be translated to the coordinate system
def get_angle(angle):
    """
    >>> get_angle(270)
    3.141592653589793
    """
    
    return ( (angle - 90) % 360 ) * np.pi/180.0

def set_copying(player_data, p, t):
    
    if t not in player_data[p]['tick']:
        return
    
    facing = going_towards(player_data, p, t)
    
    for q in facing:
    
        player_data[p].loc[t,'facing-' + str(q)] = True
        player_data[p].loc[t,'facing'] = True

def going_towards(player_data, p, t):
    """
    >>> player_data = {}
    >>> player_data['a'] = pd.DataFrame({'tick':[5],'x_pos':[1],'y_pos':[1],'angle':[135]}, [5])
    >>> player_data['b'] = pd.DataFrame({'tick':[5],'x_pos':[1],'y_pos':[1],'angle':[135]}, [5])
    >>> player_data['c'] = pd.DataFrame({'tick':[5],'x_pos':[2],'y_pos':[2],'angle':[135]}, [5])
    >>> going_towards(player_data, 'a', 5)
    {'c': True}
    """
    
    if not (t in player_data[p]['tick']):
        return {}
    
    p_loc = player_data[p].loc[t,['x_pos','y_pos']]
    p_angle = get_angle(player_data[p].loc[t,'angle'])
    
    facing = {}
    for q in player_data:
        if p == q or not (t in player_data[q]['tick']):
            continue
        q_loc = player_data[q].loc[t,['x_pos','y_pos']]
        if is_facing(p_loc, p_angle, q_loc):
            facing[q] = True
    
    return facing

def is_facing(p_loc, p_angle, q_loc):
    """
    >>> is_facing(np.array([1,1]), np.radians(45), np.array([2,2]))
    True
    >>> is_facing(np.array([1,1]), np.radians(45), np.array([1,1]))
    False
    >>> is_facing(np.array([1,1]), np.radians(225), np.array([2,2]))
    False
    """
    
    p_dir = np.array([np.cos(p_angle), np.sin(p_angle)])
    norm = np.linalg.norm(q_loc - p_loc)
    if norm > 1e-12:
        towards = (q_loc - p_loc)/norm
        angle_between = np.arccos(np.dot(p_dir,towards))
        if angle_between < facing_angle:
            return True
    
    return False

def spinning(player_data, p, t):
    """
    >>> player_data = {}
    >>> player_data['a'] = pd.DataFrame({'tick':range(8),'angle':[0,0,0,0,0,0,0,0],'velocity':[1,1,1,1,1,1,1,1]}, range(8))
    >>> spinning(player_data, 'a', 7)
    False
    >>> player_data['a'] = pd.DataFrame({'tick':range(8),'angle':[0,1,2,3,4,5,6,7],'velocity':[1,1,1,1,1,1,1,1]}, range(8))
    >>> spinning(player_data, 'a', 7)
    True
    >>> player_data['a'] = pd.DataFrame({'tick':range(8),'angle':[0,1,2,1,4,5,6,7],'velocity':[1,1,1,1,1,1,1,1]}, range(8))
    >>> spinning(player_data, 'a', 7)
    False
    >>> player_data['a'] = pd.DataFrame({'tick':range(8),'angle':[7,6,5,4,3,2,1,0],'velocity':[1,1,1,1,1,1,1,1]}, range(8))
    >>> spinning(player_data, 'a', 7)
    True
    >>> player_data['a'] = pd.DataFrame({'tick':range(8),'angle':[7,6,5,4,3,2,1,0],'velocity':[1,1,1,1,1,1,1,10]}, range(8))
    >>> spinning(player_data, 'a', 7)
    False
    """

    if (t-spin_lookback+1) not in player_data[p]['tick']:
        return False
    if not (t in player_data[p]['tick']):
        return False

    if player_data[p].loc[t,'velocity'] < 3:
        
        angles = np.array(player_data[p].loc[t-spin_lookback+1:t,'angle'])
        diffs = angles[1:] - angles[:-1]
        clockwise = diffs % 360 < 180
        counter = diffs % 360 > 180
        nonzeros = abs(diffs) > 0
        num1 = sum(clockwise * nonzeros)
        num2 = sum(counter * nonzeros)
        if num1 == spin_lookback - 1 or num2 == spin_lookback - 1:
            return True
    
    return False

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

def get_player_data(data, inactive):
    """
    >>> d = get_player_data(pd.DataFrame({'pid':['a','a','b','c','c','d'],'x_pos':[1,1,np.nan,1,1,1],'tick':[1,2,1,1,2,1]}), {'d':True})
    >>> len(d)
    2
    >>> list(d['c'].columns)
    ['pid', 'tick', 'x_pos', 'nearby-a', 'facing-a', 'copying-a', 'nearby-c', 'facing-c', 'copying-c', 'spinning', 'staying', 'going_straight', 'moving', 'nearby', 'have_been_nearby', 'since_nearby', 'copying', 'state', 'other_exploiting', 'copying_exploiting', 'copying_reward', 'uncertainty']
    >>> d['c'].iloc[:,0:6]
         pid  tick  x_pos nearby-a facing-a copying-a
    tick                                             
    1      c     1      1    False    False     False
    2      c     2      1    False    False     False
    """
    
    active_players = get_active_players(data, inactive)
        
    player_data = dict([(p, data.loc[data['pid'] == p,:].copy()) for p in active_players]) 

    for p in player_data:
        player_data[p].index = player_data[p].tick
        columns = []
        for q in player_data:
            columns += ['facing-' + str(q)]
        columns += ['spinning','facing']
        for c in columns:
            player_data[p][c] = False
        player_data[p]['uncertainty'] = np.nan
    
    return player_data

def set_movement(player_data, p, t):
    """
    >>> player_data = {}
    >>> player_data['a'] = pd.DataFrame({'tick':range(24),'x_pos':range(24),'y_pos':range(24),'velocity':[1]*24,'angle':range(24),'staying':False,'spinning':False}, range(24))
    >>> set_movement(player_data, 'a', 23)
    >>> sum(player_data['a']['staying'])
    24
    >>> list(player_data['a']['spinning'])
    [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, True, True, True, True, True, True, True]
    >>> player_data['a'] = pd.DataFrame({'tick':range(24),'x_pos':range(24),'y_pos':range(24),'velocity':[10]*24,'angle':range(24),'staying':False,'spinning':False}, range(24))
    >>> set_movement(player_data, 'a', 23)
    >>> sum(player_data['a']['staying'])
    0
    >>> sum(list(player_data['a']['spinning']))
    0
    """
    
    if t not in player_data[p]['tick']:
        return
    
    if spinning(player_data, p, t):
        player_data[p].loc[(t-spin_lookback+1):t,'spinning'] = True

def set_uncertainty(player_data, models, p, t):
    """
    >>> player_data = {}
    >>> models = {'a':inference.Model()}
    >>> player_data['a'] = pd.DataFrame({'tick':[5,6],'x_pos':[1,100],'y_pos':[1,100],'bg_val':[0,1]}, [5,6])
    >>> set_uncertainty(player_data, models, 'a', 5)
    >>> set_uncertainty(player_data, models, 'a', 6)
    >>> u1 = player_data['a'].loc[5,'uncertainty']
    >>> u2 = player_data['a'].loc[6,'uncertainty']
    >>> u2 < u1
    True
    """

    if t not in player_data[p]['tick']:
        return False
    
    models[p].observe(np.array([player_data[p].loc[t,'x_pos'],
                             player_data[p].loc[t,'y_pos']]),
                   player_data[p].loc[t,'bg_val'])
    
    player_data[p].loc[t,'uncertainty'] = models[p].get_uncertainty()
    
def process_data(data, inactive, verbose = True):
    """
    >>> success, df = process_data(pd.DataFrame({'tick':range(24)+range(24)+range(24)+range(24),'pid':[1]*24+[2]*24+[3]*24+[4]*24,'x_pos':range(24)+[100]*24+range(24)+range(24),'y_pos':range(24)+[100]*24+range(24)+range(24),'velocity':[10]*24+[1]*24+[1]*24+[1]*24,'angle':[135]*24+range(24)+[135]*24+[135]*24,'bg_val':[0]*24+[1]*24+[0]*24+[0]*24}),{}, verbose = False)
    >>> df.iloc[10,0:(len(df.columns)-1)]
    angle                     135
    bg_val                      0
    pid                         1
    tick                       10
    velocity                   10
    x_pos                      10
    y_pos                      10
    nearby-1                False
    facing-1                False
    copying-1               False
    nearby-2                False
    facing-2                 True
    copying-2                True
    nearby-3                False
    facing-3                False
    copying-3               False
    nearby-4                False
    facing-4                False
    copying-4               False
    spinning                False
    staying                 False
    going_straight           True
    moving                   True
    nearby                  False
    have_been_nearby        False
    since_nearby              NaN
    copying                  True
    state                 copying
    other_exploiting         True
    copying_exploiting       True
    copying_reward              1
    Name: 10, dtype: object
    >>> df.iloc[34,0:(len(df.columns)-1)]
    angle                         10
    bg_val                         1
    pid                            2
    tick                          10
    velocity                       1
    x_pos                        100
    y_pos                        100
    nearby-1                   False
    facing-1                   False
    copying-1                  False
    nearby-2                   False
    facing-2                   False
    copying-2                  False
    nearby-3                   False
    facing-3                   False
    copying-3                  False
    nearby-4                   False
    facing-4                   False
    copying-4                  False
    spinning                    True
    staying                     True
    going_straight             False
    moving                     False
    nearby                     False
    have_been_nearby           False
    since_nearby                 NaN
    copying                    False
    state                 exploiting
    other_exploiting            True
    copying_exploiting         False
    copying_reward               NaN
    Name: 10, dtype: object
    >>> df.iloc[58,0:(len(df.columns)-1)]
    angle                        135
    bg_val                         0
    pid                            3
    tick                          10
    velocity                       1
    x_pos                         10
    y_pos                         10
    nearby-1                   False
    facing-1                   False
    copying-1                  False
    nearby-2                   False
    facing-2                    True
    copying-2                  False
    nearby-3                   False
    facing-3                   False
    copying-3                  False
    nearby-4                    True
    facing-4                   False
    copying-4                  False
    spinning                   False
    staying                     True
    going_straight              True
    moving                     False
    nearby                      True
    have_been_nearby            True
    since_nearby                   0
    copying                    False
    state                 exploiting
    other_exploiting            True
    copying_exploiting         False
    copying_reward               NaN
    Name: 10, dtype: object
    >>> u = list(df.loc[10,'uncertainty'])
    >>> u[1] < u[0] and u[1] < u[2] and u[1] < u[3] 
    True
    >>> abs(u[0] - u[3])/u[3] < 0.2 and abs(u[0] - u[2])/u[2] < 0.2 and abs(u[2] - u[3])/u[3] < 0.2
    True
    """
    
    player_data = get_player_data(data, inactive)
    if len(player_data) == 0:
        return False, None

    models = dict(zip(player_data.keys(), [inference.Model() for p in player_data]))
    
    ticks = sorted(set(data['tick']))
    
    for t in ticks:

        if t % 100 == 0 and verbose:
            print 'init', t
        
        for p in player_data:

            update_characteristics(player_data, models, p, t)
                    
    df = pd.concat([player_data[p] for p in player_data])
    
    return True, df

def update_characteristics(player_data, models, p, t):

    set_movement(player_data, p, t)
    set_copying(player_data, p, t)
    set_uncertainty(player_data, models, p, t)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
