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
games += get_games(data_dir, 'experiment-confirmatory-2016')
#games += ['tmp']

data = get_data(data_dir, games)

get_results(data)

