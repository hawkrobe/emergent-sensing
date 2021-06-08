import cProfile

import pandas as pd

from fit_simple import *
from social_heuristic import *
from baseline_model import *
from test_model import *

# first run python single-simulate.py

in_dir = '../../modeling/'
game = '0-1en01_simulation.csv'
this_out_dir = 'simulated/'

out_dir = '/Users/peter/Desktop/model/' + this_out_dir
background_dir = '/Users/peter/Desktop/light-fields/' + game.split('_')[-2] + '/'

df = pd.read_csv(in_dir + game)

players = list(set(df['pid']))
np.random.shuffle(players)

player = 0

def run():

    f = Fit(df, background_dir, player)
    f.fit_model(SocialHeuristic, [0.5, 0.8, 0.9, 1.0, 2])
    
    #f = Fit(df, background_dir, player, test = True)
    #f.fit_model(TestModel, [10, 20, 30, 40])

cProfile.run('run()')
