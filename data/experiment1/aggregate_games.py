import os
import re
import pandas as pd

def get_games(data_dir, label):
    dirs = []
    for f in os.listdir(data_dir):
        if re.match(label, f):
            dirs += [f]
    return dirs

data_dirs = get_games('./', 'experiment-')

# aggregate raw game data
games = []
inactive = []
raw_data = []
for data_dir in data_dirs :
    for game in os.listdir(data_dir + '/games'):
        data = pd.read_csv(data_dir + '/games/' + game)
        games += [data_dir + '/games/' + game]
        data['gameid'] = game
        raw_data.append(data.copy())

pd.concat(raw_data).to_csv('./exp1_raw.csv')
