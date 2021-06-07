
from multiprocessing import Pool

import sys
import os
import shutil

sys.path.append('../scripts/')

from image_utils import *

import exp_config

reps = exp_config.plot_reps

info, in_dir = exp_config.get_micro_config(reps)

tmp_out_dir = os.path.expanduser('~') + '/tmp-fish/'
final_out_dir = '../../../fish-movies/'

def func(exp_ind):
    
    experiment = info['experiments'][exp_ind]
    print experiment

    moves_file = in_dir + experiment + '-social-simulation.csv'
    this_out_dir = tmp_out_dir + experiment + '/'
    
    make_images(moves_file, this_out_dir + '/images/')
    
    os.system('sh ../scripts/to_video.sh ' + this_out_dir)
    
    shutil.move(this_out_dir + 'video.mp4', final_out_dir + experiment + '-social.mp4')
    
    moves_file = in_dir + experiment + '-asocial-simulation.csv'
    this_out_dir = tmp_out_dir + experiment + '/'
    
    make_images(moves_file, this_out_dir + '/images/')
    
    os.system('sh ../scripts/to_video.sh ' + this_out_dir)
    
    shutil.move(this_out_dir + 'video.mp4', final_out_dir + experiment + '-asocial.mp4')


p = Pool(exp_config.num_procs)
p.map(func, range(len(info['experiments'])))
#map(func, range(len(info['experiments'])))

