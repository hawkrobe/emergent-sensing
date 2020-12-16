
import os
import numpy as np
import pandas as pd

import config

from rectangular_world import RectangularWorld

n_players = 5

out_dir = '../../experiments/'
try:
    os.makedirs(out_dir)
except:
    pass

world = RectangularWorld(None, config.GAME_LENGTH)
length = int(world.game_length)

def make_experiment(experiment, positions, goal_pos, bot_goal_pos):    
    player_bg_file = out_dir + experiment + '_player_bg.csv'
    bot_bg_file = out_dir + experiment + '_bot_bg.csv'
    init_pos_file = out_dir + experiment + '_init.csv'
    pd.DataFrame(positions, columns = ['x_pos','y_pos']).to_csv(init_pos_file, index = False)
    pd.DataFrame(goal_pos, columns = ['x_pos','y_pos']).to_csv(player_bg_file, index = False)
    pd.DataFrame(bot_goal_pos, columns = ['x_pos','y_pos']).to_csv(bot_bg_file, index = False)

positions = {}

positions['spot'] = [[100,50],
                     np.array([400,200]) + np.random.normal(size = 2)*5,
                     np.array([400,200]) + np.random.normal(size = 2)*5,
                     np.array([80,200]) + np.random.normal(size = 2)*5,
                     np.array([80,200]) + np.random.normal(size = 2)*5]

positions['wall'] = [[100,0],
                     np.array([400,280]),
                     np.array([410,280]),
                     np.array([80,200]) + np.random.normal(size = 2)*5,
                     np.array([80,200]) + np.random.normal(size = 2)*5]

goal = {'far':{}, 'close':{}}

goal['far']['spot'] = np.array([np.array([400,200]) for i in range(length)])
goal['close']['spot'] = np.array([np.array([100,50]) for i in range(length)])
goal['far']['wall'] = np.array([np.array([405,280]) for i in range(length)])
goal['close']['wall'] = np.array([np.array([100,0]) for i in range(length)])

for bg in ['spot', 'wall']:

    for bot_bg in ['spot', 'wall']:

        for loc in ['far', 'close']:

            experiment = bg + '-' + bot_bg + '-' + loc
            pos = [positions[bg][0]]
            pos += positions[bot_bg][1:]
            make_experiment(experiment, np.array(pos), goal[loc][bg], goal['far'][bot_bg])

# ##

# experiment = 'start-apart-come-together'

# positions = np.array([[100,50],
#                       np.array([400,200]) + np.random.normal(size = 2)*5,
#                       np.array([400,200]) + np.random.normal(size = 2)*5,
#                       np.array([80,200]) + np.random.normal(size = 2)*5,
#                       np.array([80,200]) + np.random.normal(size = 2)*5])

# goal_pos = np.array([np.array([400,200]) for i in range(length)])
# bot_goal_pos = np.array([np.array([400,200]) for i in range(length)])

# make_experiment(experiment, positions, goal_pos, bot_goal_pos)

# ##

# experiment = 'start-apart-stay-apart'

# positions = np.array([[100,50],
#                       np.array([400,200]) + np.random.normal(size = 2)*5,
#                       np.array([400,200]) + np.random.normal(size = 2)*5,
#                       np.array([80,200]) + np.random.normal(size = 2)*5,
#                       np.array([80,200]) + np.random.normal(size = 2)*5])

# goal_pos = np.array([np.array([100,50]) for i in range(length)])
# bot_goal_pos = np.array([np.array([400,200]) for i in range(length)])

# make_experiment(experiment, positions, goal_pos, bot_goal_pos)

# ##

# experiment = 'start-apart-come-together-alt'

# positions = np.array([[100,0],
#                       np.array([400,280]),
#                       np.array([410,280]),
#                       np.array([80,200]) + np.random.normal(size = 2)*5,
#                       np.array([80,200]) + np.random.normal(size = 2)*5])

# goal_pos = np.array([np.array([405,280]) for i in range(length)])
# bot_goal_pos = np.array([np.array([405,280]) for i in range(length)])

# make_experiment(experiment, positions, goal_pos, bot_goal_pos)

# ##

# experiment = 'start-apart-stay-apart-alt'

# positions = np.array([[100,0],
#                       np.array([400,280]),
#                       np.array([410,280]),
#                       np.array([80,200]) + np.random.normal(size = 2)*5,
#                       np.array([80,200]) + np.random.normal(size = 2)*5])

# goal_pos = np.array([np.array([100,0]) for i in range(length)])
# bot_goal_pos = np.array([np.array([405,280]) for i in range(length)])

# make_experiment(experiment, positions, goal_pos, bot_goal_pos)

# ##

# experiment = 'start-apart-come-together-mismatch'

# positions = np.array([[100,50],
#                       np.array([400,200]) + np.random.normal(size = 2)*5,
#                       np.array([400,200]) + np.random.normal(size = 2)*5,
#                       np.array([80,200]) + np.random.normal(size = 2)*5,
#                       np.array([80,200]) + np.random.normal(size = 2)*5])

# goal_pos = np.array([np.array([400,200]) for i in range(length)])
# bot_goal_pos = np.array([np.array([405,280]) for i in range(length)])

# make_experiment(experiment, positions, goal_pos, bot_goal_pos)

# ##

# experiment = 'start-apart-stay-apart-mismatch'

# positions = np.array([[100,50],
#                       np.array([400,200]) + np.random.normal(size = 2)*5,
#                       np.array([400,200]) + np.random.normal(size = 2)*5,
#                       np.array([80,200]) + np.random.normal(size = 2)*5,
#                       np.array([80,200]) + np.random.normal(size = 2)*5])

# goal_pos = np.array([np.array([100,50]) for i in range(length)])
# bot_goal_pos = np.array([np.array([405,280]) for i in range(length)])

# make_experiment(experiment, positions, goal_pos, bot_goal_pos)

# ##

# experiment = 'start-apart-come-together-alt-mismatch'

# positions = np.array([[100,0],
#                       np.array([400,280]),
#                       np.array([410,280]),
#                       np.array([80,200]) + np.random.normal(size = 2)*5,
#                       np.array([80,200]) + np.random.normal(size = 2)*5])

# goal_pos = np.array([np.array([405,280]) for i in range(length)])
# bot_goal_pos = np.array([np.array([400,200]) for i in range(length)])

# make_experiment(experiment, positions, goal_pos, bot_goal_pos)

# ##

# experiment = 'start-apart-stay-apart-alt-mismatch'

# positions = np.array([[100,0],
#                       np.array([400,280]),
#                       np.array([410,280]),
#                       np.array([80,200]) + np.random.normal(size = 2)*5,
#                       np.array([80,200]) + np.random.normal(size = 2)*5])

# goal_pos = np.array([np.array([100,0]) for i in range(length)])
# bot_goal_pos = np.array([np.array([400,200]) for i in range(length)])

# make_experiment(experiment, positions, goal_pos, bot_goal_pos)

# experiment = 'start-together-come-apart'

# positions = np.array([[400,200],
#                       np.array([400,200]) + np.random.normal(size = 2)*5,
#                       np.array([400,200]) + np.random.normal(size = 2)*5,
#                       np.array([80,200]) + np.random.normal(size = 2)*5,
#                       np.array([80,200]) + np.random.normal(size = 2)*5])

# goal_pos = np.array([np.array([100,50]) for i in range(length)])
# bot_goal_pos = np.array([np.array([400,200]) for i in range(length)])

# make_experiment(experiment, positions, goal_pos, bot_goal_pos)

