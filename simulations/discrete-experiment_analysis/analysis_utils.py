
import sys
sys.path.append('../simulations/')
sys.path.append('../player_model/')

import config
import exp_config

import numpy as np
import pandas as pd

max_distance = np.sqrt(485**2 + 280**2)

def get_goal_target_distance(player_data, center_data, close_condition = None, close_subset = None):
    
    player_ind = player_data['pid'] == 0

    player_data = player_data.loc[player_ind]
    
    tick_ind = get_tick_ind(player_data, center_data, close_condition, close_subset)
    
    goals = np.transpose(np.array([player_data.loc[tick_ind,'goal_x'],
                                   player_data.loc[tick_ind,'goal_y']]))
    
    targets = np.array(center_data.loc[tick_ind])

    assert len(targets) == len(goals)
    
    # if close_condition is None:
    #     assert len(targets) == 480 and len(goals) == 480
    # else:
    #     assert len(targets) == 240 and len(goals) == 240
    
    #return 1 - np.nanmean(np.sqrt(np.sum((goals - targets)**2, 1))) / max_distance
    return np.mean(np.sqrt(np.sum((goals - targets)**2, 1)) < config.DISCRETE_BG_RADIUS)

def get_tick_ind(player_data, center_data, close_condition, close_subset):

    def is_in_it(tick, second):

        if second:
            player_spot = [40,43,44,47,48,50]            
        else:
            player_spot = [10,13,14,17,18,20]
        
        in_it = False
        for i in range(len(player_spot)//2):
            if tick >= player_spot[2*i]*8 and tick < player_spot[2*i+1]*8:
                in_it = True
                    
        return in_it


    if close_condition is None:
        tick_ind = [True]*len(player_data)
    else:
        tick_ind = [False]*len(player_data)        
        for tick in range(len(player_data)):
            if close_subset == 'close':
                tick_ind[tick] = is_in_it(tick, close_condition == 'close_second')
            else:
                tick_ind[tick] = is_in_it(tick, not (close_condition == 'close_second'))
            
    # if close_condition is None:
    #     tick_ind = [True]*len(player_data)
    # else:
    #     if close_subset == 'close':
    #         if close_condition == 'close_first':
    #             tick_ind = player_data['tick'] < 240
    #         else:
    #             assert close_condition == 'close_second'
    #             tick_ind = player_data['tick'] >= 240
    #     else:
    #         assert close_subset == 'far'
    #         if close_condition == 'close_first':
    #             tick_ind = player_data['tick'] >= 240
    #         else:
    #             assert close_condition == 'close_second'
    #             tick_ind = player_data['tick'] < 240
    
    return np.array(tick_ind)

def get_data():
    
    df = []

    
    for bg in ['spot', 'wall']:
        for bg_match in ['matched', 'mismatch']:
            for close_subset in ['close','far']:
                for close in ['close_first', 'close_second']:
                    for bots in ['visible','invisible']:
                        for m in exp_config.groups:
                            for noise in [exp_config.get_noise_string(n) for n in exp_config.noise_levels]:
                                for i in range(exp_config.simulation_reps):
                                    
                                    if bots == 'visible':
                                        tmp_m = m
                                    else:
                                        tmp_m = 'asocial'
                                    
                                    base = '-'.join(['v2', bg, close, 'asocial', tmp_m, noise, str(i)])
                                    
                                    player_data = pd.read_csv(exp_config.micro_dir + base + '-social-simulation.csv')
                                    
                                    center_data = pd.read_csv(exp_config.micro_dir + base + '-social-' + bg_match + '_bg.csv')
                                    
                                    val = get_goal_target_distance(player_data, center_data, close, close_subset)
                                    
                                    base = '-'.join(['v2', bg, close, 'asocial', tmp_m, noise, str(i)])
                                    
                                    player_data = pd.read_csv(exp_config.micro_dir + base + '-asocial-simulation.csv')
                                    
                                    tmp = pd.read_csv(exp_config.micro_dir + base + '-asocial-' + bg_match + '_bg.csv')
                                    
                                    #assert (center_data == tmp).all()
                                    
                                    center_data = tmp
                                    
                                    compare_val = get_goal_target_distance(player_data, center_data, close, close_subset)

                                    assert not np.isnan(compare_val)
                                    
                                    df += [[bg, bg_match, close_subset, bots, m, noise, i, val, compare_val, val - compare_val]]

    df = pd.DataFrame(df)
    df.columns = ['Bg', 
                  'Bg Match', 
                  'Nearest Goal', 
                  'Bot Condition', 
                  'Model', 
                  'Model Noise',
                  'Repetition',
                  'Goal Hits',
                  'Asocial Goal Hits',
                  'Social Index']

    return df

def get_emergent_data(group = True):
    
    df = []
    
    for bg in ['spot']:
        for nbots in np.array(range(5)) + 1:
            for m in exp_config.groups:
                for noise in [exp_config.get_noise_string(n) for n in exp_config.noise_levels]:
                    for i in range(exp_config.simulation_reps):
                                    
                        base = '-'.join([bg,str(nbots),m,noise,str(i)])
                                    
                        player_data = pd.read_csv(exp_config.emergent_dir + base + '-simulation.csv')
                        
                        if group:
                            val = np.nanmean(player_data['bg_val'])
                            df += [[bg, nbots, m, noise, i, val]]
                        else:
                            for pid in set(player_data['pid']):
                                sub = player_data.loc[player_data['pid'] == pid]
                                val = np.nanmean(sub['bg_val'])
                                df += [[bg, nbots, m, noise, i, base, pid, val]]
                            

    df = pd.DataFrame(df)
    if group:
        df.columns = ['Background', 
                      'Number of Players', 
                      'Model', 
                      'Model Noise',
                      'Repetition', 
                      'Average Score']
    else:
        df.columns = ['Background', 
                      'Number of Players', 
                      'Model', 
                      'Model Noise',
                      'Repetition', 
                      'Group',
                      'Player',
                      'Score']        

    return df

