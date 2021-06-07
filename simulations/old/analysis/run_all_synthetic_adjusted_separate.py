
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

# data_names = ['Behavioral Data', 'Goal Inference Model']
# data_dirs = ['new-processed-processed-1en01','goal-inference-simulations-processed-1en01']
# nominal_dirs = ['new-synthetic-processed-1en01','synthetic-goal-inference-simulations-processed-1en01']
# matched_dirs = ['new-synthetic-score-matched-processed-1en01','synthetic-score-matched-goal-inference-simulations-processed-1en01']
# subset = '1en01'

# start = 1440
# groups = ['High Scoring','Low Scoring','']
# behaviors = ['Skilled','']
# score_cutoff = 0.75
# matched = [True, False]

data_names = ['Goal Inference Noise Model']
data_dirs = ['parset-simulations-processed-1en01']
nominal_dirs = ['synthetic-parset-simulations-processed-1en01']
matched_dirs = ['synthetic-score-matched-parset-simulations-processed-1en01']
subset = '1en01'

# data_names = ['Goal Inference Attention Model']
# data_dirs = ['goal-inference-attention-simulations-processed-1en01']
# nominal_dirs = ['synthetic-goal-inference-attention-simulations-processed-1en01']
# matched_dirs = ['synthetic-score-matched-goal-inference-attention-simulations-processed-1en01']
# subset = '1en01'

# data_names = ['Social Heuristic']
# data_dirs = ['social-heuristic-simulations-processed-1en01']
# nominal_dirs = ['synthetic-social-heuristic-simulations-processed-1en01']
# matched_dirs = ['synthetic-score-matched-social-heuristic-simulations-processed-1en01']
# subset = '1en01'

# data_names = ['Unconditional Social Heuristic']
# data_dirs = ['unconditional-social-heuristic-simulations-simulations-processed-1en01']
# nominal_dirs = ['synthetic-unconditional-social-heuristic-simulations-simulations-processed-1en01']
# matched_dirs = ['synthetic-score-matched-unconditional-social-heuristic-simulations-simulations-processed-1en01']
# subset = '1en01'


start = 1440
groups = ['']
behaviors = ['']
score_cutoff = 0.75
matched = [True, False]



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
compares = [False, False, False, True, True, True, True]

# function_names = ['Distance to Mean of Other Positions', 'Average Time Before Facing Away From Group After Low Score', 'Average Time Before Facing Spinning Players']
# functions = [dist_to_mean_others, face_away_when_low, facing_spinning]
# compares = [True, True, True]


def plot_synthetic(args):
    
    data_ind, func_ind, group, behavior, match = args
    
    data_dir = in_dir + data_dirs[data_ind]
    function = functions[func_ind]
    
    if match:
        synthetic_dir = in_dir + matched_dirs[data_ind]
    else:
        synthetic_dir = in_dir + nominal_dirs[data_ind]
    
    games = []
    ns = []
    values = []
    scores = []
    sources = []
    lengths = []
    
    for t,game in enumerate(os.listdir(data_dir)):
                
        if game[-4:] != '.csv':
            continue
        if game.split('_')[-2].split('-')[1] != subset:
            continue    
        
        data = pd.io.parsers.read_csv(data_dir + '/' + game)
        syn_data = pd.io.parsers.read_csv(synthetic_dir + '/' + game)
        
        if compares[func_ind]:
            if match:
                dfs = ['Interacting Groups','Matched Nominal Groups']
            else:
                dfs = ['Interacting Groups','Random Nominal Groups']
        else:
            dfs = ['Interacting Groups']
        
        for df in dfs:

            if df == 'Interacting Groups':
                players = list(set(data[data['tick'] == start]['pid'].dropna()))
            else:
                players = list(set(syn_data[syn_data['tick'] == start]['pid'].dropna()))
            
            n = len(players)
            
            # if n == 6:
            #     n = 5
            
            for i,p in enumerate(players):

                if df == 'Interacting Groups':
                    sub = data[data['pid'] == p]
                else:
                    sub = syn_data[syn_data['pid'] == p]

                ignore = False
                
                if len(sub) < start:
                    ignore = True
                
                sub = sub.iloc[start:].copy()
                
                if behavior == 'Skilled':
                    if np.mean(sub['spinning']) == 0 or np.mean(sub['velocity']>3) == 0:
                        ignore = True
                
                if group == 'High Scoring':
                    if np.mean(sub['bg_val']) < score_cutoff:
                        ignore = True
                if group == 'Low Scoring':
                    if np.mean(sub['bg_val']) >= score_cutoff:
                        ignore = True

                if ignore:
                    values += [np.nan]
                else:
                    val = function(sub)
                    values += [val]
                
                games += [game]
                ns += [n]
                scores += [np.mean(sub['bg_val'])]
                sources += [df]
                lengths += [len(sub)]
            
    data = pd.DataFrame({'Game':games,'Score':scores,'Number of Players':ns,function_names[func_ind]:values,'Source':sources,'Lengths':lengths})
    
    sns.set(font = 'serif', context = 'paper', style = 'white')
    sns.despine()

    try:
        g = sns.factorplot('Number of Players', function_names[func_ind], markers = ['o', 's'], linestyles = ['-','--'], data = data, kind='point', dodge = 0.15, order = sorted(set(data['Number of Players'])), hue = 'Source', legend = False)
    except:
        import pdb; pdb.set_trace()
        
    title = data_names[data_ind] + ', Noise Level: ' + subset    
    filename = subset + '-' + function_names[func_ind].replace(" ", "")
    if group != '' or behavior != '':
        title += '\n' + group + ' ' + behavior + ' Players'
        if group != '':
            filename += '-' + group.replace(" ", "")
        if behavior != '':
            filename += '-' + behavior.replace(" ", "")
    
    if compares[func_ind]:
        filename += '-Matched' if match else ''
    filename +=  '-' + data_names[data_ind].replace(" ", "")

    #plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.125), ncol = 2)
    plt.legend(loc='lower center', ncol = 2)
    plt.subplots_adjust(top=0.85)
    g.fig.suptitle(title, size = 10)
    
    fig = plt.gcf()
    
    #fig.set_size_inches(5, 5)
    try:
        fig.savefig(out_dir + filename + '.pdf')
    except:
        import pdb; pdb.set_trace()
    
    plt.close(fig) 


pars = []

for i in range(len(data_dirs)):

    for j in range(len(functions)):

        for g in groups:

            for b in behaviors:

                if compares[j]:
                
                    for m in matched:

                        pars += [(i, j, g, b, m)]

                else:
                    pars += [(i, j, g, b, False)]

print(len(pars))
                    
p = Pool(8)
p.map(plot_synthetic, pars)
