import os
import numpy as np
import itertools

simulation_reps = 10
noise_levels = [0]

micro_dir = './output/predictions-micro/'
emergent_dir = './output/predictions-emergent/'
full_dir = './output/predictions-full-background/'

full_bg_dir = os.path.expanduser("~") + '/light-fields/'

strategies = ['naive_copy', 'smart', 'asocial', 'move_to_closest', 'move_to_center']
num_procs = 8

def get_full_background_config(reps):

    try:
        os.makedirs(full_dir)
    except:
        pass

    info = {}
    info['experiments'] = []
    info['nums_bots'] = []
    info['strategies'] = []
    info['noises'] = []
    for nbots in np.array(range(5)) + 1:
        for s in strategies:
            for bg_num in range(4):
                for noise in ['1en01','2en01']:
                    for rep in range(reps):
                        bg_name = str(bg_num) + '-' + noise
                        info['experiments'] += ['-'.join([bg_name, str(nbots), s, str(rep)])]
                        info['nums_bots'] += [nbots]
                        info['strategies'] += [s]
                        info['noises'] += [bg_name]

    return info, full_dir


def get_noise_string(noise):
    if noise == 0:
        return '0'
    else:
        return '2e' + str(int(np.log2(noise)))
