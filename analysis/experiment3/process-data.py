
import sys,os

from multiprocessing import Pool

sys.path.append("../")
import game_utils 

import pandas as pd
import numpy as np
import process_utils

waits = False
all_players = False

in_dir = '../../data/experiment3/out/'
out_dir = '../../processed/'
if waits:
    out_dir += '-waits'
if all_players:
    out_dir += '-all'
out_dir += '/'
try:
    os.makedirs(out_dir)
except:
    pass

def run(pars):

    data_dir, data_file, inactive = pars
    
    if data_file[-4:] != '.csv':
        return
    
    print(data_file)

    in_file = data_dir + data_file
    data = pd.io.parsers.read_csv(in_file)
    if len(data) == 0:
        return
    data = data[['pid','tick','active','x_pos','y_pos','velocity','angle','bg_val','total_points']].copy()
    success, df = process_utils.process_data(data, inactive)
    if success:
        df.to_csv(out_dir + data_file, header = True, index = False)

pars = []

games = game_utils.get_games(in_dir, 'experiment')
for game_group in games:
    if not all_players:
        inactive = game_utils.get_inactive(in_dir, game_group)
    else:
        inactive = {}
    if waits:
        data_dir = in_dir + game_group + '/waiting_games/'
    else:
        data_dir = in_dir + game_group + '/games/'
    for data_file in os.listdir(data_dir):
        pars += [(data_dir, data_file, inactive)]

p = Pool(8)
p.map(run, pars)

#run(pars[245])
