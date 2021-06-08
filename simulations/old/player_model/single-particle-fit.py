
import numpy as np
import pandas as pd
import goal_inference_with_data
import rational_model

import sys

par_1 = float(sys.argv[1])
par_2 = float(sys.argv[2])

in_dir = '../../modeling/'    

game = '0-1en01_simulation.csv'
player = 0

df = pd.read_csv(in_dir + game)

players = list(set(df['pid']))
my_pid = players[player]

model = goal_inference_with_data.Model(lambda: rational_model.RationalModel((par_1,par_2)), n_samples = 200)

ticks = list(set(df['tick']))

for tick in range(max(ticks)+1):
    
    sub = df[df['tick'] == tick]

    others = []

    for pid in players:

        if pid == my_pid:
            continue

        others += [{'position':np.array([float(sub.loc[sub['pid'] == pid, 'x_pos']),
                                         float(sub.loc[sub['pid'] == pid, 'y_pos'])]),
                    'angle':float(sub.loc[sub['pid'] == pid, 'angle']),
                    'speed':float(sub.loc[sub['pid'] == pid, 'velocity'])}]
        
    model.observe(np.array([float(sub.loc[sub['pid'] == my_pid,'x_pos']),
                            float(sub.loc[sub['pid'] == my_pid,'y_pos'])]),
                  float(sub.loc[sub['pid'] == my_pid,'angle']),
                  float(sub.loc[sub['pid'] == my_pid,'velocity']),
                  float(sub.loc[sub['pid'] == my_pid,'bg_val']), others, tick)

    if (tick % 10) == 0:
        print tick, model.marginal_like
    
print model.marginal_like


# import numpy as np
# import pandas as pd
# import goal_inference_with_data
# import rational_model

# import sys

# player = int(sys.argv[1])
# #par_1 = float(sys.argv[2])

# #in_dir = '../../modeling/'    
# #game = '0-1en01_simulation.csv'

# in_dir = '../../processed/'
# #game = '2015-01-30-14-5-9-36_1_0-1en01_37758667487.csv'
# game = '2015-01-29-20-50-8-310_1_1-1en01_12584840878.csv'

# df = pd.read_csv(in_dir + game)

# players = list(set(df['pid']))
# my_pid = players[player]

# model = goal_inference_with_data.Model(lambda: rational_model.RationalModel(None), n_samples = 100)

# ticks = list(set(df['tick']))

# for tick in range(max(ticks)+1):
    
#     sub = df[df['tick'] == tick]

#     others = []

#     for pid in players:

#         if pid == my_pid:
#             continue

#         others += [{'position':np.array([float(sub.loc[sub['pid'] == pid, 'x_pos']),
#                                          float(sub.loc[sub['pid'] == pid, 'y_pos'])]),
#                     'angle':float(sub.loc[sub['pid'] == pid, 'angle']),
#                     'speed':float(sub.loc[sub['pid'] == pid, 'velocity'])}]
        
#     model.observe(np.array([float(sub.loc[sub['pid'] == my_pid,'x_pos']),
#                             float(sub.loc[sub['pid'] == my_pid,'y_pos'])]),
#                   float(sub.loc[sub['pid'] == my_pid,'angle']),
#                   float(sub.loc[sub['pid'] == my_pid,'velocity']),
#                   float(sub.loc[sub['pid'] == my_pid,'bg_val']), others, tick)

#     if (tick % 10) == 0:
#         #print tick, max(model.likelihoods)
#         print tick, model.marginal_like, np.mean(model.pars)

# #print max(model.likelihoods)
# print model.marginal_like
