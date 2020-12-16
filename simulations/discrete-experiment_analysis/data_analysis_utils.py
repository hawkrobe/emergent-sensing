
import os,sys
sys.path.append('../simulations/')
sys.path.append('../player_model/')
sys.path.append("../utils/")

import game_utils

import config

import numpy as np
import pandas as pd

sim_dir = '../../couzin_replication/metadata/v2/'

max_distance = np.sqrt(485**2 + 280**2)


def get_clicks(goals):

    goals = np.array(goals)
    changes = np.zeros(len(goals), dtype = bool)
    diffs = np.sum(np.abs(goals[1:,] - goals[:-1,]), 1)
    changes[1:] = diffs > 0
    
    return changes

def get_slows(velocities):
    
    velocities = np.array(velocities)
    changes = np.zeros(len(velocities), dtype = bool)
    diffs = velocities[1:] - velocities[:-1]
    changes[1:] = diffs > 0
    
    return changes

def get_stops(velocities):
    
    velocities = np.array(velocities)
    changes = np.zeros(len(velocities), dtype = bool)
    diffs = (velocities[1:] == 0) & (velocities[:-1] > 0)
    changes[1:] = diffs
    
    return changes

def get_change_hit_vec(player_data, center_datas, bg_match, inds, hard_stops_only):

    vels = np.array(player_data['velocity'])
    
    goals = np.transpose(np.array([np.array(player_data['goal_x']),
                                   np.array(player_data['goal_y'])]))
    
    clicks = get_clicks(goals)
    if hard_stops_only:
        stops = get_stops(vels)
    else:
        stops = get_slows(vels)        

    change_inds = inds & (clicks | stops)
    
    hits = np.array([False]*len(change_inds))
    
    if sum(inds & clicks) > 0:    
        dists = get_goal_target_distances(player_data[inds & clicks], center_datas[bg_match][inds & clicks])
        hits[inds & clicks] = dists < config.DISCRETE_BG_RADIUS
        
    if sum(inds & stops) > 0:    
        dists = get_pos_target_distances(player_data, center_datas, bg_match, inds & stops)
        hits[inds & stops] = dists < config.DISCRETE_BG_RADIUS
    
    if sum(change_inds) > 0:
        return hits[change_inds]
    else:
        return [0]
    
def get_any_change_stat(player_data, center_datas, bg_match, inds):
    return np.nanmean(get_change_hit_vec(player_data, center_datas, bg_match, inds, False))

def get_click_stop_stat(player_data, center_datas, bg_match, inds):
    return np.nanmean(get_change_hit_vec(player_data, center_datas, bg_match, inds, True))


def get_click_target_stat(player_data, center_datas, bg_match, inds):
    
    goals = np.transpose(np.array([np.array(player_data['goal_x']),
                                   np.array(player_data['goal_y'])]))
    
    clicks = get_clicks(goals)

    if sum(inds & clicks) > 0:
        dists = {}
        for m in center_datas:
            dists[m] = get_goal_target_distances(player_data[inds & clicks], center_datas[m][inds & clicks])

        #compare = 'mismatch' if bg_match == 'matched' else 'matched'
        
        #return np.mean(dists[bg_match] < dists[compare])
        return np.nanmean(dists[bg_match] < config.DISCRETE_BG_RADIUS)
    else:
        return 0
    
def get_goal_target_distances(player_data, center_data):
    
    assert len(set(player_data['pid'])) == 1
    
    goals = np.transpose(np.array([np.array(player_data['goal_x']),
                                   np.array(player_data['goal_y'])]))
    
    targets = np.array(center_data)
    
    assert len(targets) == len(goals)
    
    return np.sqrt(np.sum((goals - targets)**2, 1))

def get_total_goal_target_distances(player_data, center_datas, bg_match, inds):
    return np.nanmean(get_goal_target_distances(player_data.loc[inds], center_datas[bg_match][inds]))

def get_goal_target_hits(player_data, center_datas, bg_match, inds):
    
    return np.mean(get_goal_target_distances(player_data[inds], center_datas[bg_match][inds]) < config.DISCRETE_BG_RADIUS)

def get_goal_any_hits(player_data, center_datas, bg_match, inds):

    target_hits = get_goal_target_distances(player_data[inds], center_datas[bg_match][inds]) < config.DISCRETE_BG_RADIUS
    pos_hits = get_pos_target_distances(player_data, center_datas, bg_match, inds) < config.DISCRETE_BG_RADIUS
    
    return np.mean(target_hits | pos_hits)


def get_scores(player_data, center_datas, bg_match, inds):

    #if player_data.loc[inds,'in_close'].iloc[0] == 1:
    #    assert sum(player_data.loc[inds,'bg_val'] == 0) == sum(player_data.loc[inds,'on_wall'] == 1)
    
    return np.mean(player_data.loc[inds,'bg_val'])

def get_speeds(player_data, center_datas, bg_match, inds):
    
    return np.mean(player_data.loc[inds & (player_data['bg_val'] == 0),'velocity'])


def get_pos_target_distances(player_data, center_data, bg_match, inds):
        
    goals = np.transpose(np.array([np.array(player_data.loc[inds]['x_pos']),
                                   np.array(player_data.loc[inds]['y_pos'])]))
    
    targets = np.array(center_data[bg_match][inds])
    
    assert len(targets) == len(goals)
    
    return np.sqrt(np.sum((goals - targets)**2, 1))

def get_total_pos_target_distances(player_data, center_data, bg_match, inds):

    dists = get_pos_target_distances(player_data, center_data, bg_match, inds)

    return np.nanmean(dists)

def get_total_pos_target_hits(player_data, center_data, bg_match, inds):

    dists = get_pos_target_distances(player_data, center_data, bg_match, inds)

    return np.mean(dists < config.DISCRETE_BG_RADIUS)


def get_game_data(data_dir, game, inactive):
    
    if game[-4:] != '.csv':
        return None
    
    player_data = pd.read_csv(data_dir + game)
    
    if len(player_data) == 0:
        print('no data found in ' + data_dir + game)
        return None
                
    if player_data['pid'].iloc[0] in inactive:
        print('skipping', game, 'from inactivity')
        return None
    
    return player_data

def get_data(in_dir, games):

    game_dfs = []
    game_names = []

    for game_id in games:

        data_dir = in_dir + game_id + '/games/'
        inactive = game_utils.get_inactive(game_id)
        
        for game in os.listdir(data_dir):
            
            player_data = get_game_data(data_dir, game, inactive)
            
            if player_data is not None:
                print('got game with ' + str(len(player_data)) + ' rows')
                game_dfs += [player_data]
                game_names += [game]
    
    return game_dfs, game_names

def get_centers(sub):

    bg_cond = sub.iloc[0]['bg_cond']
    close_half = sub.iloc[0]['close_cond']
    
    assert len(set(sub['sim_num'])) == 1
    sim_num = sub.iloc[0]['sim_num']
    
    base = sim_dir + 'v2-' + bg_cond + '-close_' + close_half + '-asocial-smart-0-' + str(sim_num)
    
    center_datas = {}
    for bgm in ['matched', 'mismatch']:
        center_datas[bgm] = pd.read_csv(base + '-social-' + bgm + '_bg.csv')
    
    return center_datas


def get_game_stats(player_data, function, return_df = False):

    df = []
    
    pid = player_data.iloc[0]['pid']        
    bg_cond = player_data.iloc[0]['bg_cond']
    close_half = player_data.iloc[0]['close_cond']

    assert len(set(player_data['pid'])) == 1
    assert len(set(player_data['bg_cond'])) == 1
    assert len(set(player_data['close_cond'])) == 1        

    for close_subset in ['close','far']:
        for bg_match in ['matched', 'mismatch']:


            sub = player_data.loc[player_data['round_type'] == 'social']

            center_datas = get_centers(sub)

            val = get_stat(sub, center_datas, function, 'social', close_subset, bg_match)

            score = get_stat(sub, center_datas, get_scores, 'social', close_subset, bg_match)            


            sub = player_data.loc[player_data['round_type'] == 'nonsocial']

            center_datas = get_centers(sub)
            
            compare_val = get_stat(sub, center_datas, function, 'nonsocial', close_subset, bg_match)

            compare_score = get_stat(sub, center_datas, get_scores, 'nonsocial', close_subset, bg_match)            


            df += [[pid,
                    bg_cond,
                    bg_match,
                    close_subset,
                    score,
                    compare_score,
                    score - compare_score,
                    val,
                    compare_val,
                    val - compare_val]]

    if return_df:
        df = pd.DataFrame(df)
        df.columns = ['PID',
                      'Bg', 
                      'Bg Match', 
                      'Nearest Goal',
                      'Social Score',
                      'Asocial Score',
                      'Score Index',
                      'Goal Hits',
                      'Asocial Goal Hits',
                      'Social Index']
    
    return df

def get_stats(game_dfs, function):

    df = []

    for player_data in game_dfs:
        df += get_game_stats(player_data, function)
    
    df = pd.DataFrame(df)
    df.columns = ['PID',
                  'Bg', 
                  'Bg Match', 
                  'Nearest Goal',
                  'Social Score',
                  'Asocial Score',
                  'Score Index',
                  'Goal Hits',
                  'Asocial Goal Hits',
                  'Social Index']

    return df

def get_stat(player_data, center_datas, function, round_type, close_subset, bg_match):

    data_sub = player_data.loc[player_data['round_type'] == round_type]

    inds = np.array([False] * len(data_sub))
    start = min(data_sub.loc[data_sub['in_' + close_subset] == 1].tick)
    end = max(data_sub.loc[data_sub['in_' + close_subset] == 1].tick)
    inds[start:(end+1)] = True
    
    val = function(data_sub, center_datas, bg_match, inds)

    sub = data_sub.loc[inds]
    test_inds = get_pos_target_distances(data_sub, center_datas, bg_match, inds) < config.DISCRETE_BG_RADIUS
    assert sum((sub.loc[test_inds, 'bg_val'] < 1) & (sub.loc[test_inds, 'on_wall'] == 0)) == 0    
    
    return val

                                    

