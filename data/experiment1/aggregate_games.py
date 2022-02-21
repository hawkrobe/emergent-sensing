import sys
import csv

import pandas as pd

sys.path.append("../utils/")
from game_utils import *

data_dirs = []
data_dirs += get_games('./raw_data/', 'experiment-exploratory-2016')
data_dirs += get_games('./raw_data/', 'experiment-confirmatory-2016')

# aggregate raw game data
games = []
inactive = []
raw_data = []
for data_dir in data_dirs :
    for game in os.listdir(data_dir + '/games'):
        data = pd.read_csv(data_dir + '/games/' + game)
        games += [data_dir + '/games/' + game]
        data['gameid'] = game
        inactive += [get_inactive(data_dir, game)]
        raw_data.append(data.copy())

pd.concat(raw_data).to_csv('./raw_data/all_raw_games.csv')

# find inactive games
inactive = {k: v for d in inactive for k, v in d.items()}
print(inactive.keys())
writer = csv.writer(open('./inactive_games.csv','w'))
for pid in list(inactive.keys()):
    writer.writerow([pid])

# # get 'cleaned' games
# dfs = []
# for data_dir in data_dirs :
#     dfs += [get_data(data_dir, games)]
# pd.concat(dfs).to_csv('./all_games_new.csv')
