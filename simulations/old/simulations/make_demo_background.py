
import sys
sys.path.append('../player_model/')

import pandas as pd
import numpy as np

from environment import *
from centroid_manager import *

import copy

import config
import exp_config

from rectangular_world import RectangularWorld

def create_demo_background(environment_model, out_dir, file_prefix):
    
    world = World(environment_model, noise_location = None,
                  stop_and_click = config.STOP_AND_CLICK)
    
    c = Centroids(environment_model, world, None)

    gaps = [17,20,38,41]
    
    for tick in range(0, world.game_length):

        in_it = False
        for i in range(len(gaps)//2):
            if tick >= gaps[2*i]*8 and tick < gaps[2*i+1]*8:
                in_it = True
        
        if world.world_model.edge_goal and in_it:
            c.advance(None, add = False)
        else:
            c.advance(None)
            
    write_centers(world.world_model.centers, out_dir + file_prefix + '_bg.csv')
    
def write_centers(centers, center_file):    
    centers = np.array([[np.nan,np.nan] if x is None else x for x in centers])
    df = pd.DataFrame(centers)
    df.columns = ['x_pos','y_pos']
    df.to_csv(center_file, index = False)


def get_environments():

    environments = {}

    environments['spot'] = lambda x: RectangularWorld(x,
                                                     config.GAME_LENGTH,
                                                     False,
                                                     config.DISCRETE_BG_RADIUS)
    environments['wall'] = lambda x: RectangularWorld(x,
                                                      config.GAME_LENGTH,
                                                      False,
                                                      config.DISCRETE_BG_RADIUS,
                                                      edge_goal = True)

    return environments

    
if __name__ == "__main__":

    reps = exp_config.simulation_reps

    info, out_dir = exp_config.get_micro_config(exp_config.simulation_reps)
    
    environments = get_environments()
    
    for i in range(reps):

        print(i)
        
        file_prefix = 'wall-demo' + str(i)
        
        create_demo_background(environments['wall'], out_dir, file_prefix)
        
        file_prefix = 'spot-demo' + str(i)

        create_demo_background(environments['spot'], out_dir, file_prefix)
        
