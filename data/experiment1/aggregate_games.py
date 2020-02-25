import sys
import csv

sys.path.append("../utils/")
from game_utils import *

data_dir = './'
games = []
games += get_games(data_dir, 'experiment-exploratory-2016')
games += get_games(data_dir, 'experiment-confirmatory-2016')

raw_data = []
for data_dir in games :
    for game in os.listdir(data_dir + '/games'):
        data = pd.read_csv(data_dir + '/games/' + game)
        data['gameid'] = game
        raw_data.append(data.copy())
pd.concat(raw_data).to_csv('./raw_games/all_raw_games.csv')

# data = get_data(data_dir, games)

# inactive = [get_inactive(data_dir, game) for game in games]
# inactive = {k: v for d in inactive for k, v in d.items()}

# writer = csv.writer(open('./inactive_games.csv','w'))

# for pid in list(inactive.keys()):
#     writer.writerow([pid])

# data.to_csv('./all_games.csv')
