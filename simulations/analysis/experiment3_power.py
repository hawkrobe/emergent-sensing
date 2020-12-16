import pandas as pd
import numpy as np
import os, sys

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib.font_manager import FontProperties

sys.path.append("../utils/")
from game_utils import *

from experiment3_tools import *

data_dir = '../../out/'
games = []
games += get_games(data_dir, 'pilot-2016')
#games += ['tmp']

data = get_data(data_dir, games)

threshold = 0.001
n_groups = [25,50,75,100]
n_iter = 20

hits = dict(zip(n_groups, [0]*len(n_groups)))

for num_games in n_groups:
    for i in range(n_iter):

        boot_data = bootstrap_data(data, num_games)
        
        mdf,gres,rgres = get_results(boot_data, verbose = False)
        
        hit = mdf.pvalues['n_players'] < threshold and gres.pvalues['n_players'] < threshold

        hits[num_games] += hit
