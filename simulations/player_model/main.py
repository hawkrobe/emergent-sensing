
import pandas as pd

from fit_simple import *
from social_heuristic import *
from rational_model import *
from baseline_model import *
from test_model import *

#in_dir = '../../processed/'
#game = '2015-01-30-14-5-9-36_1_0-1en01_37758667487.csv'; player = 0
#game = '2015-01-29-20-50-8-310_1_1-1en01_12584840878.csv'; player = 0
#game = '2015-01-29-20-50-9-4_5_2-1en01_619311067974.csv'; player = 3
#this_out_dir = 'data-2/'

in_dir = '../../modeling/'
game = '0-1en01_simulation.csv'; player = 0
#this_out_dir = 'simulated/'

#out_dir = '/Users/peter/Desktop/model/' + this_out_dir
#background_dir = '/Users/peter/Desktop/light-fields/' + game.split('_')[-2] + '/'
#out_dir = '/home/pkrafft/model/data/' + this_out_dir
background_dir = '/home/pkrafft/couzin_copy/light-fields/' + game.split('_')[-2] + '/'

df = pd.read_csv(in_dir + game)

players = list(set(df['pid']))
#np.random.shuffle(players)

f = Fit(df, background_dir, player)
#par,err = f.fit_model(SocialHeuristic, [0.0, 0.5, 0.8, 0.9, 1.0])
#par,err = f.fit_model(SocialHeuristic, [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
#par,err = f.fit_model(SocialHeuristic, [0, 10, 20, 40, 80, 160, 320, np.inf])
par,err = f.fit_model(RationalModel, [(1.0,1.0),(0.5,0.5),(0.5,0.25)])

# #f = Fit(df, background_dir, player, out_dir = out_dir)
# #f.fit_model(SocialHeuristic, [par])

Fit(df, background_dir, player).fit_model(lambda x: BaselineModel('straight'), [None])
Fit(df, background_dir, player).fit_model(lambda x: BaselineModel('spin'), [None])
Fit(df, background_dir, player).fit_model(lambda x: BaselineModel('random'), [None])

#f = Fit(df, background_dir, player, test = True)
#f.fit_model(TestModel, [10, 20, 30, 40])
