import pandas as pd
import numpy as np
from scipy import stats
import os, sys
import matplotlib.pyplot as plt

sys.path.append("../utils/")
from utils import *

in_dir = '../../out/'
out_dir = '../../out/simulated/games/'
try:
    os.makedirs(out_dir)
except:
    pass

noise = '1-2en01'
num_players = 5

hits = get_games(in_dir, 'experiment')
np.random.shuffle(hits)

game_group = []
count = 0

print 'getting data...'
for hit_id in hits:

    if count == num_players:
        break
    
    inactive = get_inactive(hit_id)
    
    data_dir = in_dir + hit_id + '/games/'
    games = os.listdir(data_dir)
    np.random.shuffle(games)
    
    for game in games:
        if game[-4:] != '.csv':
            continue
        if count == num_players:
            break
        this_noise = game.split('_')[2]
        data = pd.io.parsers.read_csv(data_dir + game)
        players = list(set(data['pid']))
        p = players[0]
        n = len(players)
        if n != 1 or p in inactive or this_noise != noise or sum(np.isnan(data['x_pos'])) > 0:
            continue
        else:
            game_group += [(data, p)]
            count += 1

print 'making new data frame...'
df = pd.DataFrame()

for t in range(2880):
    
    for data,p in game_group:
                
        sub = data[data['tick'] == t]
        if len(sub[sub['pid'] == p]) == 0:
            continue
        df = df.append(sub[sub['pid'] == p])

game_id = np.random.randint(sys.maxint)
df.to_csv(out_dir + str(game_id) + '.csv', header = True, index = False)
