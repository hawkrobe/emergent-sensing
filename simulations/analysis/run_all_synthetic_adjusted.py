
import pandas as pd
import numpy as np
import scipy 
import os, sys

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import pylab
import matplotlib as mpl
import seaborn as sns

import analysis_utils

from multiprocessing import Pool

sys.path.append('../utils/')
from game_utils import *

in_dir = '../../'
out_dir = '../../plots/'
#out_dir = '../../figures/'

#data_names = ['Behavioral Data','Nominal Groups']
#data_dirs = ['new-processed-processed-1en01','new-synthetic-processed-1en01']
#subset = '1en01'
#append = 'data'

# data_names = ['Behavioral Data','Social Heuristic','Unconditional Social Heuristic']
# data_dirs = ['new-processed-processed-1en01','social-heuristic-simulations-processed-1en01','unconditional-social-heuristic-simulations-simulations-processed-1en01']
# subset = '1en01'
# append = 'model'

data_names = ['Behavioral Data','Social Heuristic','Non-Social Model']
data_dirs = ['new-processed-processed-1en01','social-heuristic-simulations-processed-1en01','synthetic-social-heuristic-simulations-processed-1en01']
subset = '1en01'
append = 'model'


start = 1440

def score(sub):
    return np.mean(sub['bg_val'])

def speed(sub):
    return sum(sub['velocity'] > 3) > 0

def spinning(sub):
    return sum(sub['spinning']) > 0

def dist_to_mean_others(sub):
    return np.mean(sub['dist_to_mean_others'])

def face_towards_after_away(sub):
    ignore_state = lambda sub, i: sub.iloc[i]['spinning']
    this_state = lambda sub, i: sub.iloc[i]['ave_dist_others'] < sub.iloc[i]['dist_to_mean_others']
    next_state = lambda sub, i: sub.iloc[i]['facing']
    return analysis_utils.get_value(sub, ignore_state, this_state, next_state)

def face_away_when_low(sub):
    start_index = 1
    initial_condition = lambda sub, i: (sub.iloc[i]['ave_dist_others'] > sub.iloc[i]['dist_to_mean_others']) and sub.iloc[i]['bg_val'] < 1.0
    while_condition = lambda sub, i: sub.iloc[i]['bg_val'] < 1.0
    final_condition = lambda sub, i: (sub.iloc[i]['ave_dist_others'] < sub.iloc[i]['dist_to_mean_others'])
    return analysis_utils.get_while_value(sub, initial_condition, while_condition, final_condition, start_index)

def facing_spinning(sub):
    start_index = 1
    initial_condition = lambda sub, i: ~sub.iloc[i-1]['spinning'] and ~sub.iloc[i-1]['other_spinning'] and ~sub.iloc[i]['spinning'] and sub.iloc[i]['other_spinning']
    while_condition = lambda sub, i: ~sub.iloc[i-1]['facing_spinning']
    final_condition = lambda sub, i: sub.iloc[i]['facing_spinning']
    return analysis_utils.get_while_value(sub, initial_condition, while_condition, final_condition, start_index)

function_names = ['Score','Speed','Spinning','Distance to Mean of Other Positions','Average Time Before Facing Distant Group', 'Average Time Before Facing Away From Group After Low Score', 'Average Time Before Facing Spinning Players']
functions = [score, speed, spinning, dist_to_mean_others, face_towards_after_away, face_away_when_low, facing_spinning]

def plot_synthetic(args):
    
    func_ind = args
    function = functions[func_ind]
    
    games = []
    ns = []
    values = []
    scores = []
    sources = []
    lengths = []

    for data_ind in range(len(data_dirs)):
        
        data_dir = in_dir + data_dirs[data_ind]
        
        for t,game in enumerate(os.listdir(data_dir)):

            if game[-4:] != '.csv':
                continue
            if game.split('_')[-2].split('-')[1] != subset:
                continue    

            data = pd.io.parsers.read_csv(data_dir + '/' + game)

            
            players = list(set(data[data['tick'] == start]['pid'].dropna()))

            n = len(players)

            # if n == 6:
            #     n = 5

            for i,p in enumerate(players):

                sub = data[data['pid'] == p]

                ignore = False

                if len(sub) < start:
                    ignore = True

                sub = sub.iloc[start:].copy()

                # if behavior == 'Skilled':
                #     if np.mean(sub['spinning']) == 0 or np.mean(sub['velocity']>3) == 0:
                #         ignore = True

                if ignore:
                    values += [np.nan]
                else:
                    val = function(sub)
                    values += [val]

                games += [game]
                ns += [n]
                scores += [np.mean(sub['bg_val'])]
                sources += [data_names[data_ind]]
                lengths += [len(sub)]
            
    data = pd.DataFrame({'Game':games,'Score':scores,'Number of Players':ns,function_names[func_ind]:values,'Source':sources,'Lengths':lengths})
    
    sns.set(font = 'serif', context = 'paper', style = 'white')
    sns.despine()

    try:
        g = sns.factorplot('Number of Players', function_names[func_ind], data = data, kind='point', dodge = 0.15, order = sorted(set(data['Number of Players'])), hue = 'Source')
    except:
        import pdb; pdb.set_trace()
        
    filename = subset + '-' + function_names[func_ind].replace(" ", "") + '-' + append

    #plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.125), ncol = 2)
    #plt.legend(loc='lower center', ncol = 2)
    #plt.subplots_adjust(top=0.85)
    
    fig = plt.gcf()
    
    #fig.set_size_inches(5, 5)
    try:
        fig.savefig(out_dir + filename + '.pdf')
    except:
        import pdb; pdb.set_trace()
    
    plt.close(fig) 


pars = []

for i in range(len(functions)):
    pars += [i]

print(len(pars))
                    
p = Pool(8)
p.map(plot_synthetic, pars)
