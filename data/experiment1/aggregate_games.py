import sys
import csv

import pandas as pd

sys.path.append("../utils/")
from game_utils import *

data_dirs = []
data_dirs += get_games('./', 'experiment-')

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

pd.concat(raw_data).to_csv('./exp1_raw.csv')

# find inactive games
inactive = {k: v for d in inactive for k, v in d.items()}
writer = csv.writer(open('./inactive_games.csv','w'))
for pid in list(inactive.keys()):
    writer.writerow([pid])
