
import sys
import pandas as pd

from fit import *
from rational_model import *

player = int(sys.argv[1])

in_dir = '../../modeling/'    
game = '0-1en01_simulation.csv'

#in_dir = '../../processed/'
#game = '2015-01-30-14-5-9-36_1_0-1en01_37758667487.csv'
#game = '2015-01-29-20-50-8-310_1_1-1en01_12584840878.csv'

df = pd.read_csv(in_dir + game)

players = list(set(df['pid']))
my_pid = players[player]

background_dir = '/home/pkrafft/couzin_copy/light-fields/' + game.split('_')[-2] + '/'

f = Fit(df, background_dir, player)
par = f.fit_model(RationalModel)
