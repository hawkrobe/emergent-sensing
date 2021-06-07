import pandas as pd
import numpy as np
from scipy import stats
import os, sys

sys.path.append("../utils/")
from utils import *

data_dir = '../../out/'
games = []
games += get_games(data_dir, 'experiment')

lengths = {}

count = 0
for game_id in games:
    
    data_dir = in_dir + game_id + '/games/'
    
    for game in os.listdir(data_dir):
        if game[-4:] != '.csv':
            continue
        
        noise = game.split('_')[2]
        
        data = pd.io.parsers.read_csv(data_dir + game)
        
        time = len(set(data['tick']))
        
        lengths[noise] = lengths[noise] + [time] if noise in lengths else [time]
        
        count += 1

