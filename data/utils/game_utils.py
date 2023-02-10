import pandas as pd
import numpy as np
import os, sys, re

def get_games(data_dir, label):
    dirs = []
    for f in os.listdir(data_dir):
        if re.match(label, f):
            dirs += [f]
    return dirs

def get_inactive(data_dir, game_id):
    
    hidden_line = 'Player .* will be disconnected for being hidden.'
    inactive_line = 'Player .* will be disconnected for inactivity.'
    lag_line = 'Player .* will be disconnected because of latency.'
    
    log = open(data_dir  + '/log')
    
    inactive = {}
    for line in log:
        if re.match(hidden_line, line):
            inactive[line.strip().split(' ')[1]] = True
        if re.match(inactive_line, line):
            inactive[line.strip().split(' ')[1]] = True
        if re.match(lag_line, line):
            inactive[line.strip().split(' ')[1]] = True

    log.close()
    
    return inactive


def get_data(in_dir, games):

    pids = []
    assigned_n_players = []
    bn_players = []    
    hn_players = []
    fn_players = []    
    bonuses = []
    first_half_bonuses = []
    second_half_bonuses = []        
    wait_times = []
    game_names = []
    noises = []
    difficulties = []
    max_lats = []
    mean_lats = []

    inactive_count = 0
    ignore_count = 0
    for game_id in games:

        data_dir = in_dir +  '/games/'
        latency_dir = in_dir +  '/latencies/'
        waiting_dir = in_dir +  '/waiting_games/'
        print(game_id)
        inactive = get_inactive(in_dir, game_id)
        
        wait_locs = {}
        for game in os.listdir(waiting_dir):
            if game[-4:] != '.csv':
                continue
            game_tag = game.split('_')[3]
            wait_locs[game_tag] = game
        

        for game in os.listdir(data_dir):
            if game[-4:] != '.csv':
                continue
            assigned_n = int(game.split('_')[1])
            noise = game.split('_')[2]
            difficulty = game.split('_')[2][2:]
            game_tag = game.split('_')[3]
            data = pd.io.parsers.read_csv(data_dir + game)
            latencies = pd.io.parsers.read_csv(latency_dir + game)
            waiting_data = pd.io.parsers.read_csv(waiting_dir + wait_locs[game_tag])
            players = list(set(data['pid']))
            begin_players = []            
            active_players = []
            final_players = []
            for p in players:

                if p in inactive:
                    inactive_count += 1
                    continue
                
                sub = data[data['pid'] == p]
                
                if sum(1-np.isnan(sub['x_pos'])) > 0:#2879:#2880/2:
                    begin_players += [p]
                
                if sum(1-np.isnan(sub['x_pos'])) >= 1200:#2879:#2880/2:
                    active_players += [p]
                else:
                    ignore_count += 1
                
                if sum(1-np.isnan(sub['x_pos'])) >= 2400:#2880/2:
                    final_players += [p]

                    
            bn = len(begin_players)            
            hn = len(active_players)
            fn = len(final_players)
            for p in active_players:
                sub = data[data['pid'] == p]
                lat = latencies[latencies['pid'] == p]
                waiting_sub = waiting_data[waiting_data['pid'] == p]
                waiting_bonus = list(sub['total_points'])[0]
                total_bonus = list(sub['total_points'])[-1]
                #bonus = (total_bonus - waiting_bonus)/len(sub) * 2880 / 1.25
                bonus = np.mean(sub['bg_val'])                
                first_half_bonus = np.mean(sub['bg_val'][:1200])
                second_half_bonus = np.mean(sub['bg_val'][1200:])                
                max_latency = max(lat['latency'])
                mean_latency = np.mean(lat['latency'])

                pids += [p]
                assigned_n_players += [assigned_n]
                bn_players += [bn]                
                hn_players += [hn]
                fn_players += [fn]                
                bonuses += [bonus]
                first_half_bonuses += [first_half_bonus]
                second_half_bonuses += [second_half_bonus]                                
                game_names += [game[:-4]]
                noises += [noise]
                difficulties += [difficulty]
                wait_times += [len(waiting_sub)]
                max_lats += [max_latency]
                mean_lats += [mean_latency]

    print(inactive_count, 'participants were dropped for inactivity')
    print(ignore_count, 'participants were ignored for disconnecting early')
    
    df = pd.DataFrame(dict(pid = pids,
                           assigned_n_players = assigned_n_players,
                           bn_players = bn_players,                           
                           hn_players = hn_players,
                           fn_players = fn_players,                           
                           score = bonuses,
                           first_half_score = first_half_bonuses,
                           second_half_score = second_half_bonuses,                                                      
                           wait = wait_times,
                           game = game_names,
                           noise = noises,
                           difficulty = difficulties,
                           max_lat = max_lats,
                           mean_lat = mean_lats))
                
    return df

def get_group_data(in_dir, games):

    n_players = []
    bonuses = []
    game_names = []
    noises = []
    difficulties = []

    for game_id in games:

        data_dir = in_dir + game_id + '/games/'

        inactive = get_inactive(game_id)
        
        for game in os.listdir(data_dir):
            if game[-4:] != '.csv':
                continue
            noise = game.split('_')[2]
            difficulty = game.split('_')[2][2:]
            game_tag = game.split('_')[3]
            data = pd.io.parsers.read_csv(data_dir + game)

            players = list(set(data['pid']))
            active_players = []
            for p in players:
                if p in inactive:
                    continue
                sub = data[data['pid'] == p]
                if sum(1-np.isnan(sub['x_pos'])) > 2880/2:
                    active_players += [p]

            group_bonus = 0
            n = len(active_players)
            for p in active_players:
                sub = data[data['pid'] == p]
                waiting_bonus = list(sub['total_points'])[0]
                total_bonus = list(sub['total_points'])[-1]
                bonus = (total_bonus - waiting_bonus)/len(sub) * 2880 / 1.25
                group_bonus += bonus/float(n)

            if len(active_players) > 0:
                n_players += [n]
                bonuses += [group_bonus]
                game_names += [game[:-4]]
                noises += [noise]
                difficulties += [difficulty]
    
    df = pd.DataFrame(dict(n_players = n_players,
                           score = bonuses,
                           game = game_names,
                           noise = noises,
                           difficulty = difficulties))
                
    return df

def spinning(data):
    """
    >>> d = [{'speed':1,'angle':0},{'speed':1,'angle':20},{'speed':1,'angle':40},{'speed':1,'angle':60}]
    >>> spinning(d)
    True
    >>> d = [{'speed':5,'angle':0},{'speed':1,'angle':20},{'speed':1,'angle':40},{'speed':1,'angle':60}]
    >>> spinning(d)
    False
    >>> d = [{'speed':1,'angle':0},{'speed':1,'angle':20},{'speed':1,'angle':0},{'speed':1,'angle':60}]
    >>> spinning(d)
    False
    >>> d = [{'speed':1,'angle':340},{'speed':1,'angle':0},{'speed':1,'angle':20},{'speed':1,'angle':40}]
    >>> spinning(d)
    True
    >>> d = [{'speed':1,'angle':40},{'speed':1,'angle':20},{'speed':1,'angle':0},{'speed':1,'angle':340}]
    >>> spinning(d)
    True
    """

    if sum([data[i]['speed'] > 3 for i in range(len(data))]) > 0:
        return False
    
    angles = np.array([data[i]['angle'] for i in range(len(data))])
    diffs = angles[1:] - angles[:-1]
    clockwise = diffs % 360 < 180
    counter = diffs % 360 > 180
    nonzeros = abs(diffs) > 0
    num1 = sum(clockwise * nonzeros)
    num2 = sum(counter * nonzeros)
    if num1 == (len(data) - 1) or num2 == (len(data) - 1):
        return True
    
    return False
