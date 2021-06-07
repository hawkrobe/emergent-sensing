
import sys
sys.path.append('../player_model/')
import simulation_utils
import config
from rectangular_world import RectangularWorld
import numpy as np
import pandas as pd

game_length = 5.0
super_slow = False

def run(i):

    environment = get_environment()
    
    center = simulation_utils.random_walk_centers(environment, super_slow)
    
    write_centers(center, '../../backgrounds/background-' + str(i)+ '.csv')

def get_environment():

    return lambda x: RectangularWorld(x,
                                      game_length,
                                      False,
                                      config.DISCRETE_BG_RADIUS,
                                      edge_goal = False)

def write_centers(centers, center_file):    
    centers = np.array([[np.nan,np.nan] if x is None else x for x in centers])
    df = pd.DataFrame(centers)
    df.columns = ['x_pos','y_pos']
    df.to_csv(center_file, index = False)

for i in range(5):
    run(i)
