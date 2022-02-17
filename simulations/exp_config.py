
import os
import numpy as np
import itertools

simulation_reps = 50
emergent_dir = './output/predictions-emergent/'
strategies = ['naive_copy', 'smart', 'asocial', 'move_to_closest', 'move_to_center']
num_procs = 8

def get_emergent_config(reps):
    """
    Experiment 1 simulations
    """
    try:
        os.makedirs(emergent_dir)
    except:
        pass

    info = {'experiments' : [], 'bots' : [], 'strategies' : [], 'prob_explore' : []}
    for strategy in strategies :
        for group_size in [1,2,3,4,6,8,16,32]: # 16,32,64,128
            for prob_explore in ([None] if strategy in ['asocial', 'smart'] else [0,.25,.5,.75,1]) :
                composition = np.array([strategy == 'asocial', strategy == 'naive_copy',
                                        strategy == 'move_to_center', strategy == 'move_to_closest',
                                        strategy == 'smart']) * group_size
                bots = ([{'strategy' : 'asocial', 'prob_explore' : prob_explore}] * composition[0] +
                        [{'strategy' : 'naive_copy', 'prob_explore' : prob_explore}] * composition[1] +
                        [{'strategy' : 'move_to_center', 'prob_explore' : prob_explore}] * composition[2] +
                        [{'strategy' : 'move_to_closest', 'prob_explore' : prob_explore}] * composition[3] +
                        [{'strategy' : 'smart', 'prob_explore' : prob_explore}] * composition[4])
                info['experiments'] += ['-'.join(
                    [str(len(bots)), '+'.join([str(i) for i in composition]), str(rep), str(prob_explore)]
                ) for rep in range(reps)]
                info['prob_explore'] += [prob_explore for rep in range(reps)]
                info['bots'] += [bots for rep in range(reps)]
                info['strategies'] += [composition for rep in range(reps)]

    # for n_asocial in range(7) :
    #     for n_naive in range(7 - n_asocial) :
    #         for rep in range(reps):
    #             n_center = 0
    #             n_closest = 0
    #             n_smart = 6 - n_asocial - n_naive
    #             composition = (n_asocial, n_naive, n_center, n_closest, n_smart)
    #             bots = ([{'strategy' : 'asocial', 'prob_explore' : 0.5}] * n_asocial +
    #                     [{'strategy' : 'naive_copy', 'prob_explore' : 0.5}] * n_naive +
    #                     [{'strategy' : 'move_to_center', 'prob_explore' : 0.5}] * n_center +
    #                     [{'strategy' : 'move_to_closest', 'prob_explore' : 0.5}] * n_closest +
    #                     [{'strategy' : 'smart', 'prob_explore' : 0.5}] * n_smart)
    #             nbots = len(bots)
    #             print(composition)
    #             info['experiments'] += ['-'.join(
    #                 [str(nbots), ''.join([str(i) for i in composition]), str(rep)]
    #             )]
    #             info['bots'] += [bots]
    #             info['strategies'] += [composition]


    return info, emergent_dir
