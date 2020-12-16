
import pandas as pd
import numpy as np
import os, sys

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib.font_manager import FontProperties

social_split = False

#from parse import *

sys.path.append("../utils/")
import game_utils
import data_analysis_utils 

import importlib
importlib.reload(data_analysis_utils)

data_dir = '../../out/'
games = []
games += game_utils.get_games(data_dir, 'micro-pilot-exploratory-2017')
games += game_utils.get_games(data_dir, 'micro-pilot-confirmatory-2017')

rme = pd.read_csv(data_dir + '/full-micro-pilot-2017-11-28-RME-results.csv')
rme.index = rme['id']

rme_key = pd.read_csv('./RME Key.csv')

rme_key['Key'] == rme[rme.columns[19:55]]

rme['scores'] = np.mean(np.array([list(rme[rme.columns[19:55]].iloc[i].values == rme_key['Key'].values) for i in range(len(rme))]), 1)

game_dfs, game_names = data_analysis_utils.get_data(data_dir, games)

#data = data_analysis_utils.get_stats(game_dfs, data_analysis_utils.get_scores)
#data = data_analysis_utils.get_stats(game_dfs, data_analysis_utils.get_total_pos_target_hits)
#data = data_analysis_utils.get_stats(game_dfs, data_analysis_utils.get_goal_target_hits)
#data = data_analysis_utils.get_stats(game_dfs, data_analysis_utils.get_click_target_stat)
#data = data_analysis_utils.get_stats(game_dfs, data_analysis_utils.get_goal_any_hits)

data = data_analysis_utils.get_stats(game_dfs, data_analysis_utils.get_any_change_stat)
#data = data_analysis_utils.get_stats(game_dfs, data_analysis_utils.get_click_stop_stat)

if social_split:
    data['Social Strategy'] = data['PID'].replace(rme['Social'])
    data['RME Score'] = data['PID'].replace(rme['scores'])
    data = data.loc[(data['Social Strategy'] == 1) | (data['Social Strategy'] == 0)]

    data['High RME'] = data['RME Score'] > np.median(data['RME Score'])

print('Got ' + str(len(data)) + ' games')


out_dir = '../../../fish-plots/'

try:
    os.makedirs(out_dir)
except:
    pass

sns.set_style("white")
sns.set_context("poster")

deps = ['Social Index', 'Goal Hits', 'Asocial Goal Hits']

for dep in deps:
    if social_split:
        sns_plot = sns.factorplot('Bg Match', dep, hue = 'Nearest Goal', row = 'Bg', col = 'High RME', data = data, kind = 'bar')
        sns_plot.savefig(out_dir + "player-data-" + dep + '-social-split.png')        
    else:
        sns_plot = sns.factorplot('Bg Match', dep, hue = 'Nearest Goal', row = 'Bg', data = data, kind = 'bar')
        sns_plot.savefig(out_dir + "player-data-" + dep + '.png')


spot_player_model_df = []
spot_player_model_rme = []
spot_player_model_pids = []
for pid in set(data.loc[data['Bg'] == 'spot', 'PID']):
    spot_player_model_df += [list(data.loc[data['PID'] == pid, 'Social Index'])]
    spot_player_model_rme += [list(data.loc[data['PID'] == pid, ['RME Score','Social Strategy']].iloc[0])]
    spot_player_model_pids += [pid]

wall_player_model_df = []
wall_player_model_rme = []
wall_player_model_pids = []
for pid in set(data.loc[data['Bg'] == 'wall', 'PID']):
    wall_player_model_df += [list(data.loc[data['PID'] == pid, 'Social Index'])]
    wall_player_model_rme += [list(data.loc[data['PID'] == pid, ['RME Score','Social Strategy']].iloc[0])]
    wall_player_model_pids += [pid]
    
import scipy.cluster.vq as vq    

spot_player_model_df = vq.whiten(spot_player_model_df)
wall_player_model_df = vq.whiten(wall_player_model_df)

# match-close, mismatch-close, match-far, mismatch-far

#init_clusters = [[0,0,2,0],[0,0,2,2],[0,0,0,0],[2,2,2,2]]

clusters = vq.kmeans(spot_player_model_df, 5)[0]
print(clusters)
assignments = vq.vq(spot_player_model_df, clusters)[0]
print(assignments)

clusters = vq.kmeans(wall_player_model_df, 5)[0]
print(clusters)
assignments = vq.vq(wall_player_model_df, clusters)[0]
print(assignments)
