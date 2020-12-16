
import os
import numpy as np

DEBUG = True

if DEBUG:
    simulation_reps = 2
    noise_levels = [0]
else:
    simulation_reps = 25
    noise_levels = [0, 1/8.0 * 1/8.0, 1/8.0 * 1/4.0, 1/8.0 * 1/2.0, 1/8.0]

plot_reps = 2
num_players = 5

micro_dir = '../../predictions-micro/'
emergent_dir = '../../predictions-emergent/'
full_dir = '../../predictions-full-background/'

full_bg_dir = os.path.expanduser("~") + '/light-fields/'

groups = ['smart']
#groups = ['smart', 'naive', 'asocial', 'eager', 'lazy']

num_procs = 8

def get_micro_config(reps):

    try:
        os.makedirs(micro_dir)
    except:
        pass

    partner_types = ['asocial']
    
    info = {}
    info['experiments'] = []
    info['background_types'] = []
    info['locs'] = []
    info['partners'] = []
    info['groups'] = []
    info['noises'] = []
    info['seed'] = []
    for bg in ['spot', 'wall']:
        for loc in ['close_first', 'close_second']:
            for partner in partner_types:
                for g in groups:
                    for noise in noise_levels:
                        for rep in range(reps):
                            info['experiments'] += ['-'.join(['v2', bg, loc, partner, g, get_noise_string(noise), str(rep)])]
                            info['background_types'] += [bg]
                            info['locs'] += [loc]
                            info['partners'] += [partner]
                            info['groups'] += [g]
                            info['noises'] += [noise]
                            info['seed'] += [np.random.randint(4294967295)]
    
    return info, micro_dir

def get_emergent_config(reps):

    try:
        os.makedirs(emergent_dir)
    except:
        pass

    info = {}
    info['experiments'] = []
    info['background_types'] = []
    info['nums_bots'] = []
    info['groups'] = []
    info['noises'] = []
    for bg in ['spot']:#, 'wall']:
        for nbots in np.array(range(5)) + 1:
            for g in groups:
                for noise in noise_levels:
                    for rep in range(reps):
                        info['experiments'] += ['-'.join([bg, str(nbots), g, get_noise_string(noise), str(rep)])]
                        info['background_types'] += [bg]
                        info['nums_bots'] += [nbots]
                        info['groups'] += [g]
                        info['noises'] += [noise]
                        
    return info, emergent_dir

def get_full_background_config(reps):

    try:
        os.makedirs(full_dir)
    except:
        pass

    info = {}
    info['experiments'] = []
    info['nums_bots'] = []
    info['groups'] = []
    info['noises'] = []
    for nbots in np.array(range(5)) + 1:
        for g in groups:
            for bg_num in range(4):
                for noise in ['1en01','2en01']:
                    for rep in range(reps):
                        bg_name = str(bg_num) + '-' + noise
                        info['experiments'] += ['-'.join([bg_name, str(nbots), g, str(rep)])]
                        info['nums_bots'] += [nbots]
                        info['groups'] += [g]
                        info['noises'] += [bg_name]
                        
    return info, full_dir


def get_noise_string(noise):
    
    if noise == 0:
        return '0'
    else:
        return '2e' + str(int(np.log2(noise)))
