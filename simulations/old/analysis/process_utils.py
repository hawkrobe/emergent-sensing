
import pandas as pd
import numpy as np

import sys
sys.path.append("../player_model/")
sys.path.append("../utils/")

import stats

import environment as env
import smart_particle as inference

slow_dist = 17/8.0
fast_dist = 57/8.0

lookback = 4
stay_lookback = 8*3
spin_lookback = 8
copy_threshold = lookback
move_threshold = lookback

stay_dist = slow_dist*(stay_lookback-1)/1.5
nearby_dist = 40
facing_angle = np.radians(45)# 2*np.pi / 6

# angle is specified w.r.t. top, needs to be translated to the coordinate system
def get_angle(angle):
    """
    >>> get_angle(270)
    3.141592653589793
    """
    
    return ( (angle - 90) % 360 ) * np.pi/180.0

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

def is_turning_towards(p_last_angle, p_angle, p_loc, others_loc):
    """
    >>> is_turning_towards(np.radians(45), np.radians(45), np.array([1,1]), np.array([2,2]))
    False
    >>> is_turning_towards(np.radians(45), np.radians(50), np.array([1,1]), np.array([2,2]))
    False
    >>> is_turning_towards(np.radians(50), np.radians(45), np.array([1,1]), np.array([2,2]))
    True
    >>> is_turning_towards(np.radians(40), np.radians(45), np.array([1,1]), np.array([2,2]))
    True
    """
    
    last_dir = np.array([np.cos(float(p_last_angle)), np.sin(float(p_last_angle))])
    this_dir = np.array([np.cos(float(p_angle)), np.sin(float(p_angle))])
    norm = np.linalg.norm(others_loc - p_loc)
    if norm > 1e-12:
        towards = (others_loc - p_loc)/norm
        angle_between = np.arccos(np.dot(this_dir,towards))
        alt_between = np.arccos(np.dot(last_dir,towards))
        if angle_between < alt_between:
            return True
    
    return False

def angle_between(p_angle, p_loc, others_loc):
    """
    >>> np.degrees(angle_between(np.radians(40), np.array([1,1]), np.array([2,2])))
    5.0000000000000648
    >>> np.degrees(angle_between(np.radians(45), np.array([1,1]), np.array([2,2])))
    8.5377364625159387e-07
    >>> np.degrees(angle_between(np.radians(50), np.array([1,1]), np.array([2,2])))
    4.999999999999992
    >>> np.degrees(angle_between(np.radians(50), np.array([1,1]), np.array([1,1])))
    0.0
    """
    
    this_dir = np.array([np.cos(float(p_angle)), np.sin(float(p_angle))])
    norm = np.linalg.norm(others_loc - p_loc)
    if norm > 1e-12:
        towards = (others_loc - p_loc)/norm
        angle_between = np.arccos(np.dot(this_dir,towards))
    else:
        angle_between = 0        
    
    return angle_between


def nearby(player_data, p, t):
    """
    >>> player_data = {}
    >>> player_data['a'] = pd.DataFrame({'tick':[5],'x_pos':[1],'y_pos':[1],'angle':[135],'velocity':2.5}, [5])
    >>> player_data['c'] = pd.DataFrame({'tick':[5],'x_pos':[1],'y_pos':[1],'angle':[135],'velocity':5}, [5])
    >>> player_data['b'] = pd.DataFrame({'tick':[5],'x_pos':[1],'y_pos':[1],'angle':[135],'velocity':2.5}, [5])
    >>> player_data['d'] = pd.DataFrame({'tick':[5],'x_pos':[100],'y_pos':[100],'angle':[135],'velocity':2.5}, [5])
    >>> nearby(player_data, 'a', 5)
    {'b': True}
    """
    
    if not (t in player_data[p]['tick']):
        return {}
    
    if player_data[p].loc[t,'velocity'] > 3:
        return {}
    
    p_loc = player_data[p].loc[t,['x_pos','y_pos']]
    
    close_to = {}
    for q in player_data:
        if p == q or not (t in player_data[q]['tick']):
            continue
        if player_data[q].loc[t,'velocity'] > 3:
            continue
        q_loc = player_data[q].loc[t,['x_pos','y_pos']]
        norm = np.linalg.norm(q_loc - p_loc)
        if norm < nearby_dist:
            close_to[q] = True
    
    return close_to

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

def going_straight(player_data, p, t):
    """
    >>> player_data = {}
    >>> player_data['a'] = pd.DataFrame({'tick':range(8),'angle':[0,0,0,0,0,0,0,0],'velocity':[1,1,1,1,1,1,1,1]}, range(8))
    >>> going_straight(player_data, 'a', 7)
    True
    >>> player_data['a'] = pd.DataFrame({'tick':range(8),'angle':[0,1,2,3,4,5,6,7],'velocity':[1,1,1,1,1,1,1,1]}, range(8))
    >>> going_straight(player_data, 'a', 7)
    False
    """
    
    if t < lookback - 1 or not (t in player_data[p]['tick']):
        return False
    
    angles = np.array(player_data[p].loc[t-lookback+1:t,'angle'])
    diffs = angles[1:] - angles[:-1]
    nonzeros = abs(diffs) > 0

    if sum(nonzeros) == 0:
        return True
    
    return False

def staying_put(player_data, p, t):
    """
    >>> player_data = {}
    >>> player_data['a'] = pd.DataFrame({'tick':range(24),'x_pos':[0]*24,'y_pos':[0]*24,'velocity':[1]*24}, range(24))
    >>> staying_put(player_data, 'a', 23)
    True
    >>> player_data['a'] = pd.DataFrame({'tick':range(24),'x_pos':[0]*24,'y_pos':[0]*24,'velocity':[1]*23 + [10]}, range(24))
    >>> staying_put(player_data, 'a', 23)
    False
    >>> player_data['a'] = pd.DataFrame({'tick':range(24),'x_pos':[0]*23+[100],'y_pos':[0]*23+[100],'velocity':[1]*24}, range(24))
    >>> staying_put(player_data, 'a', 23)
    False
    """
    
    if (t-stay_lookback+1) not in player_data[p]['tick']:
        return False
    if not (t in player_data[p]['tick']):
        return False

    if sum(player_data[p].loc[t-stay_lookback+1:t,'velocity'] > 3) > 0:
        return False
    
    positions = np.array(player_data[p].loc[t-stay_lookback+1:t,['x_pos','y_pos']])
    directions = positions[1:] - positions[0:-1]
    
    m = np.linalg.norm(sum(directions))
    if m < stay_dist:
        return True

    return False

def moving_fast(player_data, p, t):
    """
    >>> player_data = {}
    >>> player_data['a'] = pd.DataFrame({'tick':[5],'velocity':[10]}, [5])
    >>> moving_fast(player_data, 'a', 5)
    True
    >>> player_data['a'] = pd.DataFrame({'tick':[5],'velocity':[0]}, [5])
    >>> moving_fast(player_data, 'a', 5)
    False
    """
    
    if not (t in player_data[p]['tick']):
        return False
    
    if player_data[p].loc[t,'velocity'] > 3:
        return True

    return False

def turning(player_data, p, t):
    """
    >>> player_data = {}
    >>> player_data['a'] = pd.DataFrame({'tick':[4,5],'angle':[10,10]}, [4,5])
    >>> turning(player_data, 'a', 5)
    False
    >>> turning(player_data, 'a', 6)
    False
    >>> player_data['a'] = pd.DataFrame({'tick':[4,5],'angle':[10,11]}, [4,5])
    >>> turning(player_data, 'a', 5)
    True
    """
    
    if not (t in player_data[p]['tick']) or not ((t-1) in player_data[p]['tick']):
        return False
    
    if abs(player_data[p].loc[t,'angle'] - player_data[p].loc[t-1,'angle']) > 1e-8:
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
    ['pid', 'tick', 'x_pos', 'nearby-a', 'facing-a', 'copying-a', 'nearby-c', 'facing-c', 'copying-c', 'spinning', 'staying', 'going_straight', 'moving_fast', 'nearby', 'nearby_spinning', 'have_been_nearby', 'since_nearby', 'copying', 'state', 'other_exploiting', 'other_spinning', 'copying_exploiting', 'score_increased', 'score_decreased', 'uncertainty_increased', 'score_decreased_from_one', 'turning', 'turning_towards_others', 'turning_towards_spinning', 'turning_towards_beliefs', 'facing', 'facing_spinning', 'copying_reward', 'uncertainty', 'others_cov', 'ave_dist_others', 'spinning_cov', 'dist_to_mean_others', 'dist_to_mean_spinning', 'dist_to_mean_beliefs', 'angle_to_mean_others', 'angle_to_mean_spinning', 'angle_to_mean_beliefs']
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
            columns += ['nearby-' + str(q),
                       'facing-' + str(q),
                       'copying-' + str(q)]
        columns += ['spinning','staying','going_straight','moving_fast','nearby','nearby_spinning','have_been_nearby','since_nearby','copying','state','other_exploiting','other_spinning','copying_exploiting','score_increased','score_decreased','uncertainty_increased','score_decreased_from_one','turning','turning_towards_others','turning_towards_spinning','turning_towards_beliefs','facing','facing_spinning']
        for c in columns:
            player_data[p][c] = False
        player_data[p]['since_nearby'] = np.nan
        player_data[p]['state'] = 'none'
        player_data[p]['copying_reward'] = np.nan
        player_data[p]['uncertainty'] = np.nan
        player_data[p]['others_cov'] = np.nan
        player_data[p]['ave_dist_others'] = np.nan
        player_data[p]['spinning_cov'] = np.nan
        player_data[p]['dist_to_mean_others'] = np.nan
        player_data[p]['dist_to_mean_spinning'] = np.nan
        player_data[p]['dist_to_mean_beliefs'] = np.nan
        player_data[p]['angle_to_mean_others'] = np.nan
        player_data[p]['angle_to_mean_spinning'] = np.nan
        player_data[p]['angle_to_mean_beliefs'] = np.nan
        
    
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
    
    player_data[p].loc[t,'moving_fast'] = moving_fast(player_data, p, t)
    player_data[p].loc[t,'turning'] = turning(player_data, p, t)
    
    if spinning(player_data, p, t):
        player_data[p].loc[(t-spin_lookback+1):t,'spinning'] = True
        update_others_from_spin(player_data, p, t)
    
    player_data[p].loc[t,'staying'] = staying_put(player_data, p, t)
    if player_data[p].loc[t,'staying']:
        player_data[p].loc[(t-stay_lookback+1):t,'staying'] = True

def set_changes(player_data, p, t):
    """
    >>> player_data = {}
    >>> player_data['a'] = pd.DataFrame({'tick':range(16),'bg_val':[1,1,1,1] + [0.9]*12,'uncertainty':[1]*16}, range(16))
    >>> set_changes(player_data, 'a', 15)
    >>> player_data['a'].loc[14:15]
        bg_val  tick  uncertainty score_decreased_from_one
    14     0.9    14            1                      NaN
    15     0.9    15            1                     True
    >>> player_data['a'] = pd.DataFrame({'tick':range(16),'bg_val':[1,1,1,0] + [1]*8 + [0.9]*4,'uncertainty':-np.array(range(16))}, range(16))
    >>> set_changes(player_data, 'a', 15)
    >>> player_data['a'].loc[14:15]
        bg_val  tick  uncertainty score_decreased
    14     0.9    14          -14             NaN
    15     0.9    15          -15            True
    >>> player_data['a'] = pd.DataFrame({'tick':range(16),'bg_val':[1,1,1,1] + [0.8]*8 + [0.9]*4,'uncertainty':range(16)}, range(16))
    >>> set_changes(player_data, 'a', 15)
    >>> player_data['a'].loc[14:15,player_data['a'].columns[2:]]
        uncertainty score_increased uncertainty_increased score_decreased_from_one
    14           14             NaN                   NaN                      NaN
    15           15            True                  True                     True
    """


    if t not in player_data[p]['tick']:
        return

    if (t - 2*lookback + 1) not in player_data[p]['tick']:
        return
    
    if np.mean(player_data[p].loc[(t - lookback + 1):t,'bg_val']) > np.mean(player_data[p].loc[(t - 2*lookback + 1):(t - lookback),'bg_val']):
        player_data[p].loc[t,'score_increased'] = True
    
    if np.mean(player_data[p].loc[(t - lookback + 1):t,'bg_val']) < np.mean(player_data[p].loc[(t - 2*lookback + 1):(t - lookback),'bg_val']):        
        player_data[p].loc[t,'score_decreased'] = True
    
    if np.mean(player_data[p].loc[(t - lookback + 1):t,'uncertainty']) > np.mean(player_data[p].loc[(t - 2*lookback + 1):(t - lookback),'uncertainty']):
        player_data[p].loc[t,'uncertainty_increased'] = True
    
    if (t - 4*lookback + 1) not in player_data[p]['tick']:
        return
    
    if (sum(player_data[p].loc[(t - 4*lookback + 1):(t - 3*lookback),'bg_val'] > 0.999) == lookback) and (player_data[p].loc[t,'bg_val'] < 0.999):
        player_data[p].loc[t,'score_decreased_from_one'] = True
    
def set_others(player_data, p, t):
    """
    >>> player_data = {}
    >>> player_data['a'] = pd.DataFrame({'tick':[1,2],'x_pos':[0,0],'y_pos':[0,0],'velocity':[0,0],'angle':[0,0],'spinning':False,'other_spinning':[False,True]}, [1,2])
    >>> player_data['b'] = pd.DataFrame({'tick':[1,2],'x_pos':[0,1],'y_pos':[0,0],'velocity':[0,0],'angle':[0,0],'spinning':False}, [1,2])
    >>> set_others(player_data, 'a', 2)
    >>> player_data['a'].iloc[:,7:]
       dist_to_mean_others  angle_to_mean_others turning_towards_others
    1                  NaN                   NaN                    NaN
    2                    1              1.570796                  False
    >>> player_data['a'] = pd.DataFrame({'tick':[1,2],'x_pos':[0,0],'y_pos':[0,0],'velocity':[0,0],'angle':[0,0],'spinning':False,'other_spinning':[False,True]}, [1,2])
    >>> player_data['b'] = pd.DataFrame({'tick':[1,2],'x_pos':[0,1],'y_pos':[0,0],'velocity':[0,0],'angle':[0,0],'spinning':[False,True]}, [1,2])    
    >>> set_others(player_data, 'a', 2)
    >>> player_data['a'].iloc[1,7:]
    dist_to_mean_others                1
    angle_to_mean_others        1.570796
    turning_towards_others         False
    dist_to_mean_spinning              1
    angle_to_mean_spinning      1.570796
    turning_towards_spinning       False
    Name: 2, dtype: object
    >>> player_data['a'] = pd.DataFrame({'tick':[1,2],'x_pos':[0,0],'y_pos':[0,0],'velocity':[0,0],'angle':[0,10],'spinning':False,'other_spinning':[False,True]}, [1,2])
    >>> player_data['b'] = pd.DataFrame({'tick':[1,2],'x_pos':[0,1],'y_pos':[0,0],'velocity':[0,0],'angle':[0,0],'spinning':[False,True]}, [1,2]) 
    >>> player_data['c'] = pd.DataFrame({'tick':[1,2],'x_pos':[0,1],'y_pos':[0,0],'velocity':[0,0],'angle':[0,0],'spinning':[False,True]}, [1,2])
    >>> player_data['d'] = pd.DataFrame({'tick':[1,2],'x_pos':[0,1],'y_pos':[0,0],'velocity':[0,0],'angle':[0,0],'spinning':[False,True]}, [1,2])
    >>> player_data['e'] = pd.DataFrame({'tick':[1,2],'x_pos':[0,9],'y_pos':[0,0],'velocity':[0,0],'angle':[0,0],'spinning':[False,False]}, [1,2])
    >>> set_others(player_data, 'a', 2)
    >>> player_data['a'].iloc[1,7:]
    others_cov                         0
    ave_dist_others                    4
    dist_to_mean_others                3
    angle_to_mean_others        1.396263
    turning_towards_others          True
    spinning_cov                       0
    dist_to_mean_spinning              1
    angle_to_mean_spinning      1.396263
    turning_towards_spinning        True
    Name: 2, dtype: object
    """

    if t not in player_data[p]['tick']:
        return
    
    others = []
    for q in player_data:
        if p == q or not (t in player_data[q]['tick']):
            continue
        others += [np.array(player_data[q].loc[t,['x_pos','y_pos']],dtype=float)]
    
    if len(others) > 2:
        player_data[p].loc[t,'others_cov'] = stats.bounding_oval(others)
    
    if len(others) > 1:
        player_data[p].loc[t,'ave_dist_others'] = stats.ave_dist(others)
    
    if len(others) > 0:
        mean_others = np.mean(others, 0)
        set_relative_features(player_data, p, t, mean_others, 'others')

    
    others = []
    for q in player_data:
        if p == q or not (t in player_data[q]['tick']):
            continue
        if player_data[q].loc[t,'spinning']:
            others += [np.array(player_data[q].loc[t,['x_pos','y_pos']],dtype=float)]
    
    if len(others) > 2:
        player_data[p].loc[t,'spinning_cov'] = stats.bounding_oval(others)
    
    if len(others) > 0:
        assert player_data[p].loc[t,'other_spinning']
        mean_others = np.mean(others, 0)
        set_relative_features(player_data, p, t, mean_others, 'spinning')
        
def set_copying(player_data, p, t):
    """
    >>> player_data = {}
    >>> player_data['a'] = pd.DataFrame({'tick':range(8),'x_pos':range(8),'y_pos':range(8),'velocity':[10]*8,'angle':[135]*8,'moving_fast':[True]*8,'facing-c':[True]*8}, range(8))
    >>> player_data['c'] = pd.DataFrame({'tick':range(8),'x_pos':[1000]*8,'y_pos':[1000]*8,'velocity':[0]*8,'angle':[135]*8}, range(8))
    >>> set_copying(player_data, 'a', 7)
    >>> player_data['a'].iloc[2:8][['going_straight','copying-c','copying']]
      going_straight copying-c copying
    2            NaN       NaN     NaN
    3            NaN       NaN     NaN
    4           True      True    True
    5           True      True    True
    6           True      True    True
    7           True      True    True
    >>> player_data['a'] = pd.DataFrame({'tick':range(8),'x_pos':range(8),'y_pos':range(8),'velocity':[1]*8,'angle':[135]*8,'moving_fast':[True]*8,'facing-c':[True]*8}, range(8))
    >>> player_data['c'] = pd.DataFrame({'tick':range(8),'x_pos':[0]*8,'y_pos':[0]*8,'velocity':[0]*8,'angle':[135]*8}, range(8))
    >>> player_data['a'] = pd.DataFrame({'tick':range(8),'x_pos':range(8),'y_pos':range(8),'velocity':[1]*8,'angle':[135]*8,'moving_fast':[True]*8,'facing-c':[True]*8}, range(8))
    >>> set_copying(player_data, 'a', 7)
    >>> player_data['a'].iloc[2:8]
       angle facing-c moving_fast  tick  velocity  x_pos  y_pos going_straight
    2    135     True        True     2         1      2      2            NaN
    3    135     True        True     3         1      3      3            NaN
    4    135     True        True     4         1      4      4           True
    5    135     True        True     5         1      5      5           True
    6    135     True        True     6         1      6      6           True
    7    135     True        True     7         1      7      7           True
    >>> player_data['a'] = pd.DataFrame({'tick':range(8),'x_pos':range(8),'y_pos':range(8),'velocity':[1]*8,'angle':[135]*8,'moving_fast':[True]*8,'facing-c':[True]*8}, range(8))
    >>> set_copying(player_data, 'a', 2)
    >>> player_data['a'].iloc[2:8]
       angle facing-c moving_fast  tick  velocity  x_pos  y_pos
    2    135     True        True     2         1      2      2
    3    135     True        True     3         1      3      3
    4    135     True        True     4         1      4      4
    5    135     True        True     5         1      5      5
    6    135     True        True     6         1      6      6
    7    135     True        True     7         1      7      7
    """
    
    if t not in player_data[p]['tick']:
        return
    
    straight = going_straight(player_data, p, t)
    if straight:
        player_data[p].loc[(t-lookback+1):t,'going_straight'] = True

    facing = going_towards(player_data, p, t)
    if t >= lookback - 1:
        was_moving = player_data[p].loc[(t-lookback+1):t,'moving_fast']
    
    for q in facing:
        
        player_data[p].loc[t,'facing-' + str(q)] = True
        player_data[p].loc[t,'facing'] = True
        
        if t >= lookback - 1:
            
            was_facing = player_data[p].loc[(t-lookback+1):t,'facing-' + str(q)]
        
            if sum(was_facing & was_moving) >= copy_threshold and straight:
                
                player_data[p].loc[(t-lookback+1):t,'copying-' + str(q)] = True
                player_data[p].loc[(t-lookback+1):t,'copying'] = True

def set_close_to(player_data, p, t):
    """
    >>> player_data = {}
    >>> player_data['a'] = pd.DataFrame({'tick':[5,6],'x_pos':[1,100],'y_pos':[1,100],'velocity':0}, [5,6])
    >>> player_data['c'] = pd.DataFrame({'tick':[5,6],'x_pos':[1,1],'y_pos':[1,1],'velocity':5,'spinning':False}, [5,6])
    >>> player_data['b'] = pd.DataFrame({'tick':[5,6],'x_pos':[1,1],'y_pos':[1,1],'velocity':2.5,'spinning':False}, [5,6])
    >>> player_data['d'] = pd.DataFrame({'tick':[5,6],'x_pos':[1,1],'y_pos':[1,1],'velocity':2.5,'spinning':False}, [5,6])
    >>> set_close_to(player_data, 'a', 5)
    >>> player_data['a'][player_data['a'].columns[4:12]]
      nearby-b nearby have_been_nearby  since_nearby nearby-d
    5     True   True             True             0     True
    6      NaN    NaN             True           NaN      NaN
    >>> set_close_to(player_data, 'a', 6)
    >>> player_data['a'][player_data['a'].columns[4:12]]
      nearby-b nearby have_been_nearby  since_nearby nearby-d
    5     True   True             True             0     True
    6      NaN    NaN             True             1      NaN
    """    
    close_to = nearby(player_data, p, t)
    
    for q in close_to:
        player_data[p].loc[t,'nearby-' + str(q)] = True
        player_data[p].loc[t,'nearby'] = True
        player_data[p].loc[t:,'have_been_nearby'] = True
        player_data[p].loc[t,'since_nearby'] = 0
    
    if len(close_to) == 0 and t > 0 and (t in player_data[p]['tick']):
        player_data[p].loc[t,'since_nearby'] = player_data[p].loc[t-1,'since_nearby'] + 1

def get_and_set_state(player_data, p, t):

    if t not in player_data[p]['tick']:
        return None
    
    if player_data[p].loc[t,'spinning']:
        state = 'exploiting'
    elif player_data[p].loc[t,'copying']:
        state = 'copying'
    elif player_data[p].loc[t,'staying']:
        state = 'exploiting'
    else:
        state = 'exploring'
    
    player_data[p].loc[t,'state'] = state
    
    return state

def update_others_from_exploit(player_data, p, t):
    """
    >>> player_data = {}
    >>> player_data['a'] = pd.DataFrame({'tick':[5]}, [5])
    >>> player_data['b'] = pd.DataFrame({'tick':[5],'copying-a':True}, [5])
    >>> player_data['c'] = pd.DataFrame({'tick':[5],'copying-a':False}, [5])
    >>> update_others_from_exploit(player_data, 'a', 5)
    >>> player_data['a']
       tick
    5     5
    >>> player_data['b']
      copying-a  tick other_exploiting copying_exploiting
    5      True     5             True               True
    >>> player_data['c']
      copying-a  tick other_exploiting
    5     False     5             True
    """
    
    for q in player_data:
        
        if q == p or not (t in player_data[q]['tick']):
            continue
        
        player_data[q].loc[t,'other_exploiting'] = True
        
        if player_data[q].loc[t,'copying-' + str(p)]:
            
            player_data[q].loc[t,'copying_exploiting'] = True

def update_others_from_spin(player_data, p, t):
    """
    >>> player_data = {}
    >>> player_data['a'] = pd.DataFrame({'tick':[5]}, [5])
    >>> player_data['b'] = pd.DataFrame({'tick':[5],'nearby-a':False,'facing-a':True}, [5])
    >>> player_data['c'] = pd.DataFrame({'tick':[3,4,5],'nearby-a':[True,False,True],'facing-a':False}, [3,4,5])
    >>> update_others_from_spin(player_data, 'a', 5)
    >>> player_data['a']
       tick
    5     5
    >>> player_data['b']
      facing-a nearby-a  tick other_spinning facing_spinning
    5     True    False     5           True            True
    >>> player_data['c']
      facing-a nearby-a  tick other_spinning nearby_spinning
    3    False     True     3           True            True
    4    False    False     4           True             NaN
    5    False     True     5           True            True
    """
    
    for q in player_data:
        
        if q == p:
            continue
        
        for u in range((t-spin_lookback+1),t+1):
            if u in player_data[q]['tick']:
                player_data[q].loc[u,'other_spinning'] = True                
            if u in player_data[q]['tick'] and player_data[q].loc[u]['nearby-' + str(p)]:
                player_data[q].loc[u,'nearby_spinning'] = True
            if u in player_data[q]['tick'] and player_data[q].loc[u]['facing-' + str(p)]:
                player_data[q].loc[u,'facing_spinning'] = True
            
def update_copy_rewards(player_data, p, t):
    """
    >>> player_data = {}
    >>> player_data['a'] = pd.DataFrame({'tick':[5], 'bg_val':1}, [5])
    >>> player_data['b'] = pd.DataFrame({'tick':[5],'copying-a':True,'copying-c':True,'copying-d':False}, [5])
    >>> player_data['c'] = pd.DataFrame({'tick':[5],'bg_val':0}, [5])
    >>> player_data['d'] = pd.DataFrame({'tick':[5],'bg_val':0}, [5])
    >>> update_copy_rewards(player_data, 'b', 5)
    >>> player_data['b']
      copying-a copying-c copying-d  tick  copying_reward
    5      True      True     False     5             0.5
    """
    
    count = 0
    
    player_data[p].loc[t,'copying_reward'] = 0
    
    for q in player_data:
        
        if q == p or not (t in player_data[q]['tick']):
            continue
        
        if player_data[p].loc[t,'copying-' + str(q)]:            
            count += 1
            r = player_data[q].loc[t,'bg_val']
            player_data[p].loc[t,'copying_reward'] += r
    
    player_data[p].loc[t,'copying_reward'] /= float(count)

def set_uncertainty(player_data, models, p, t):
    """
    >>> player_data = {}
    >>> models = {'a':inference.Model()}
    >>> player_data['a'] = pd.DataFrame({'tick':[5,6],'x_pos':[1,100],'y_pos':[1,100],'bg_val':[0,1],'angle':[0,350]}, [5,6])
    >>> set_uncertainty(player_data, models, 'a', 5)
    >>> set_uncertainty(player_data, models, 'a', 6)
    >>> u1 = player_data['a'].loc[5,'uncertainty']
    >>> u2 = player_data['a'].loc[6,'uncertainty']
    >>> u2 < u1
    True
    >>> u1 = player_data['a'].loc[5,'dist_to_mean_beliefs']
    >>> u2 = player_data['a'].loc[6,'dist_to_mean_beliefs']
    >>> u2 < u1
    True
    """
    
    if t not in player_data[p]['tick']:
        return
    
    models[p].observe(np.array([player_data[p].loc[t,'x_pos'],
                             player_data[p].loc[t,'y_pos']]),
                   player_data[p].loc[t,'bg_val'])
    
    player_data[p].loc[t,'uncertainty'] = models[p].get_uncertainty()
    
    mean_beliefs = np.mean(models[p].samples, 0)
    set_relative_features(player_data, p, t, mean_beliefs, 'beliefs')

def set_relative_features(player_data, p, t, target_pos, feature_name):
    """
    >>> player_data = {}
    >>> player_data['a'] = pd.DataFrame({'tick':[5,6],'x_pos':[1,100],'y_pos':[1,100],'angle':[0,350]}, [5,6])
    >>> set_relative_features(player_data, 'a', 6, np.array([110,100]), 'test')
    >>> player_data['a'].iloc[:,4:]
       dist_to_mean_test  angle_to_mean_test turning_towards_test
    5                NaN                 NaN                  NaN
    6                 10            1.745329                False
    >>> player_data['a'] = pd.DataFrame({'tick':[5,6],'x_pos':[1,100],'y_pos':[1,100],'angle':[0,10]}, [5,6])
    >>> set_relative_features(player_data, 'a', 6, np.array([110,100]), 'test')
    >>> player_data['a'].iloc[:,4:]
       dist_to_mean_test  angle_to_mean_test turning_towards_test
    5                NaN                 NaN                  NaN
    6                 10            1.396263                 True
    """
    
    my_pos = np.array(player_data[p].loc[t,['x_pos','y_pos']],dtype=float)
    
    dist_to_mean = np.linalg.norm(target_pos - my_pos)
    
    player_data[p].loc[t,'dist_to_mean_' + feature_name] = dist_to_mean

    this_angle = get_angle(player_data[p].loc[t,['angle']])
    player_data[p].loc[t,'angle_to_mean_' + feature_name] = angle_between(this_angle, my_pos, target_pos)
    
    if (t-1) in player_data[p]['tick']:
        last_angle = get_angle(player_data[p].loc[t-1,['angle']])
        player_data[p].loc[t,'turning_towards_' + feature_name] = is_turning_towards(last_angle, this_angle, my_pos, target_pos)
    
    
def update_characteristics(player_data, models, p, t):

    set_close_to(player_data, p, t)
    set_movement(player_data, p, t)
    set_copying(player_data, p, t)
    set_uncertainty(player_data, models, p, t)
    set_changes(player_data, p, t)

def update_post_pass(player_data, p, t):
    
    state = get_and_set_state(player_data, p, t)

    set_others(player_data, p, t)
    
    if state == 'exploiting':
        update_others_from_exploit(player_data, p, t)
    if state == 'copying':
        update_copy_rewards(player_data, p, t)
    
def process_data(data, inactive, verbose = True):
    """
    >>> np.random.seed(1)
    >>> success, df = process_data(pd.DataFrame({'tick':range(24)+range(24)+range(24)+range(23)+range(23)+range(23),'pid':[1]*24+[2]*24+[3]*24+[4]*23+[5]*23+[6]*23,'x_pos':range(24)+[100]*24+range(24)+range(23)+[100]*23+[100]*23,'y_pos':range(24)+[100]*24+range(24)+range(23)+[100]*23+[100]*23,'velocity':[10]*24+[1]*24+[1]*24+[1]*23+[1]*23+[1]*23,'angle':[135]*24+range(24)+[135]*24+[135]*23+range(23)+range(23),'bg_val':[0]*24+[1]*24+[0]*24+[0]*23+[1]*23+[1]*23}),{}, verbose = False)
    >>> len(df)
    141
    >>> df.iloc[60]
    angle                                135
    bg_val                                 0
    pid                                    1
    tick                                  10
    velocity                              10
    x_pos                                 10
    y_pos                                 10
    nearby-1                           False
    facing-1                           False
    copying-1                          False
    nearby-2                           False
    facing-2                            True
    copying-2                           True
    nearby-3                           False
    facing-3                           False
    copying-3                          False
    nearby-4                           False
    facing-4                           False
    copying-4                          False
    nearby-5                           False
    facing-5                            True
    copying-5                           True
    nearby-6                           False
    facing-6                            True
    copying-6                           True
    spinning                           False
    staying                            False
    going_straight                      True
    moving_fast                         True
    nearby                             False
    nearby_spinning                    False
    have_been_nearby                   False
    since_nearby                         NaN
    copying                             True
    state                            copying
    other_exploiting                    True
    other_spinning                      True
    copying_exploiting                  True
    score_increased                    False
    score_decreased                    False
    uncertainty_increased               True
    score_decreased_from_one           False
    turning                            False
    turning_towards_others             False
    turning_towards_spinning           False
    turning_towards_beliefs            False
    facing                              True
    facing_spinning                     True
    copying_reward                         1
    uncertainty                     8484.406
    others_cov                             0
    ave_dist_others                 76.36753
    spinning_cov                           0
    dist_to_mean_others             76.36753
    dist_to_mean_spinning           127.2792
    dist_to_mean_beliefs            353.2469
    angle_to_mean_others        1.490116e-08
    angle_to_mean_spinning      1.490116e-08
    angle_to_mean_beliefs          0.3436884
    Name: 10, Length: 59, dtype: object
    >>> df.iloc[61]
    angle                               10
    bg_val                               1
    pid                                  2
    tick                                10
    velocity                             1
    x_pos                              100
    y_pos                              100
    nearby-1                         False
    facing-1                         False
    copying-1                        False
    nearby-2                         False
    facing-2                         False
    copying-2                        False
    nearby-3                         False
    facing-3                         False
    copying-3                        False
    nearby-4                         False
    facing-4                         False
    copying-4                        False
    nearby-5                          True
    facing-5                         False
    copying-5                        False
    nearby-6                          True
    facing-6                         False
    copying-6                        False
    spinning                          True
    staying                           True
    going_straight                   False
    moving_fast                      False
    nearby                            True
    nearby_spinning                   True
    have_been_nearby                  True
    since_nearby                         0
    copying                          False
    state                       exploiting
    other_exploiting                  True
    other_spinning                    True
    copying_exploiting               False
    score_increased                  False
    score_decreased                  False
    uncertainty_increased            False
    score_decreased_from_one         False
    turning                           True
    turning_towards_others           False
    turning_towards_spinning         False
    turning_towards_beliefs          False
    facing                           False
    facing_spinning                  False
    copying_reward                     NaN
    uncertainty                   658.3822
    others_cov                           0
    ave_dist_others               76.36753
    spinning_cov                       NaN
    dist_to_mean_others           76.36753
    dist_to_mean_spinning                0
    dist_to_mean_beliefs          2.428225
    angle_to_mean_others         0.9599311
    angle_to_mean_spinning               0
    angle_to_mean_beliefs        0.8797644
    Name: 10, Length: 59, dtype: object
    >>> df.iloc[62]
    angle                                135
    bg_val                                 0
    pid                                    3
    tick                                  10
    velocity                               1
    x_pos                                 10
    y_pos                                 10
    nearby-1                           False
    facing-1                           False
    copying-1                          False
    nearby-2                           False
    facing-2                            True
    copying-2                          False
    nearby-3                           False
    facing-3                           False
    copying-3                          False
    nearby-4                            True
    facing-4                           False
    copying-4                          False
    nearby-5                           False
    facing-5                            True
    copying-5                          False
    nearby-6                           False
    facing-6                            True
    copying-6                          False
    spinning                           False
    staying                             True
    going_straight                      True
    moving_fast                        False
    nearby                              True
    nearby_spinning                    False
    have_been_nearby                    True
    since_nearby                           0
    copying                            False
    state                         exploiting
    other_exploiting                    True
    other_spinning                      True
    copying_exploiting                 False
    score_increased                    False
    score_decreased                    False
    uncertainty_increased              False
    score_decreased_from_one           False
    turning                            False
    turning_towards_others             False
    turning_towards_spinning           False
    turning_towards_beliefs            False
    facing                              True
    facing_spinning                     True
    copying_reward                       NaN
    uncertainty                     8573.016
    others_cov                             0
    ave_dist_others                 76.36753
    spinning_cov                           0
    dist_to_mean_others             76.36753
    dist_to_mean_spinning           127.2792
    dist_to_mean_beliefs            347.9206
    angle_to_mean_others        1.490116e-08
    angle_to_mean_spinning      1.490116e-08
    angle_to_mean_beliefs          0.3277598
    Name: 10, Length: 59, dtype: object
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
            
    for t in ticks:

        if t % 100 == 0 and verbose:
            print 'next', t
        
        for p in player_data:

            update_post_pass(player_data, p, t)
                    
    df = pd.concat([player_data[p] for p in player_data])
    df = df.sort(['tick','pid'])
    
    return True, df

if __name__ == "__main__":
    import doctest
    doctest.testmod()
