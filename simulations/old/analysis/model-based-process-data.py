
import sys,os
sys.path.append("../utils/")
import game_utils 

import pandas as pd
import numpy as np

import model_based_process_utils as process

import pickle

raw = False
waits = False
all_players = False

subset = '1en01'

base = sys.argv[1] #'new-processed'
if raw:
    in_dir = '../../out/'
else:
    in_dir = '../../' + base + '/'
out_dir = '../../' + base + '-model-processed-' + subset
if waits:
    out_dir += '-waits'
if all_players:
    out_dir += '-all'
out_dir += '/'
try:
    os.makedirs(out_dir)
except:
    pass

def run(data_dir, data_file, inactive):

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
    success, df = process.Processor(data, inactive).process_data()
    if success:
        pickle.dump(df, open(out_dir + data_file[:-4] + '.out', 'w'))

if raw:
    games = game_utils.get_games(in_dir, 'experiment')
    for game_group in games:
        if not all_players:
            inactive = game_utils.get_inactive(game_group)
        else:
            inactive = {}
        if waits:
            data_dir = in_dir + game_group + '/waiting_games/'
        else:
            data_dir = in_dir + game_group + '/games/'
        for data_file in os.listdir(data_dir):
            run(data_dir, data_file, inactive)            
else:
    for data_file in os.listdir(in_dir):
        run(in_dir, data_file, {})
