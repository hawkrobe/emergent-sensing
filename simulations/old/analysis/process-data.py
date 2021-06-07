
import sys,os

from multiprocessing import Pool

sys.path.append("../utils/")
import game_utils 

import pandas as pd
import numpy as np
import process_utils

raw = False
waits = False
all_players = False

subset = '1en01'

base = sys.argv[1]

if raw:
    in_dir = '../../out/'
else:
    in_dir = '../../' + base + '/'
out_dir = '../../' + base + '-processed-' + subset
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
    
    bg_file = data_file.split('_')[-2]

    if bg_file.split('-')[1] != subset:
        return

    print data_file

    in_file = data_dir + data_file
    data = pd.io.parsers.read_csv(in_file)
    if len(data) == 0:
        return
    data = data[['pid','tick','active','x_pos','y_pos','velocity','angle','bg_val','total_points']].copy()
    success, df = process_utils.process_data(data, inactive)
    if success:
        df.to_csv(out_dir + data_file, header = True, index = False)

pars = []
if raw:
    games = utils.get_games(in_dir, 'experiment')
    for game_group in games:
        if not all_players:
            inactive = utils.get_inactive(game_group)
        else:
            inactive = {}
        if waits:
            data_dir = in_dir + game_group + '/waiting_games/'
        else:
            data_dir = in_dir + game_group + '/games/'
        for data_file in os.listdir(data_dir):
            pars += [(data_dir, data_file, inactive)]
else:
    for data_file in os.listdir(in_dir):
        pars += [(in_dir, data_file, {})]

p = Pool(8)
p.map(run, pars)
