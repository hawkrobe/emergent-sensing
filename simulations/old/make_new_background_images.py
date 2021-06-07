# python make_images.py ../../processed-waits-all/ 2015-01-26-23-19-26-925_5_1-2en01_623635699972 None /Users/peter/Desktop/wait-videos/ augmented

import matplotlib
matplotlib.use('Agg')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pylab
import os
import sys
import matplotlib.patheffects as PathEffects

from image_utils import *

in_dir = sys.argv[1] # '../../processed/'
game = sys.argv[2] # 'game_2_2015-01-18-16-56-240'
out_dir = sys.argv[3] # '/Users/peter/Desktop/videos/'

moves_file = in_dir + game + '.csv'
this_out_dir = out_dir + game + '/images/'

#center_files = ['../../couzin_replication/metadata/background-' + game.split('_')[2] + '.csv']
center_files = None

make_images(moves_file, this_out_dir, center_files = center_files)
