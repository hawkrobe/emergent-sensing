
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

micro_dir = './output/predictions-micro/'
emergent_dir = './output/predictions-emergent/'
full_dir = './output/predictions-full-background/'

full_bg_dir = os.path.expanduser("~") + '/light-fields/'

strategies = ['asocial']
#strategies = ['smart', 'naive', 'asocial', 'eager', 'lazy']

num_procs = 8

def get_emergent_config(reps):
    """
    Experiment 1 simulations
    """
    try:
        os.makedirs(emergent_dir)
    except:
        pass

    info = {}
    info['experiments'] = []
    info['background_types'] = []
    info['nums_bots'] = []
    info['strategies'] = []
    for bg in ['spot']:
        for nbots in np.array(range(5)) + 1:
            for s in strategies:
                for rep in range(reps):
                    info['experiments'] += ['-'.join([bg, str(nbots), s, str(rep)])]
                    info['background_types'] += [bg]
                    info['nums_bots'] += [nbots]
                    info['strategies'] += [s]
                        
    return info, emergent_dir

def get_micro_config(reps):
    """
    Experiment 2 simulations
    """
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
    info['strategies'] = []
    info['noises'] = []
    info['seed'] = []
    for bg in ['spot', 'wall']:
        for loc in ['close_first', 'close_second']:
            for partner in partner_types:
                for s in strategies:
                    for noise in noise_levels:
                        for rep in range(reps):
                            info['experiments'] += ['-'.join(['v2', bg, loc, partner, s, get_noise_string(noise), str(rep)])]
                            info['background_types'] += [bg]
                            info['locs'] += [loc]
                            info['partners'] += [partner]
                            info['strategies'] += [s]
                            info['noises'] += [noise]
                            info['seed'] += [np.random.randint(4294967295)]
    
    return info, micro_dir

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
