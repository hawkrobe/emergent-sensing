
import pandas as pd
import copy

from utils import *
from environment import *

in_dir = '../../processed/'
#game = '2015-01-30-14-5-9-36_1_0-1en01_37758667487.csv'
#game = '2015-01-29-20-50-8-310_1_1-1en01_12584840878.csv'
game = '2015-01-29-20-50-9-4_5_2-1en01_619311067974.csv'

#in_dir = '../../modeling/'
#game = '0-1en01_simulation.csv'

background_dir = '/Users/peter/Desktop/light-fields/' + game.split('_')[-2] + '/'
#background_dir = '/home/pkrafft/couzin_copy/light-fields/' + game.split('_')[-2] + '/'

df = pd.read_csv(in_dir + game)

players = list(set(df['pid']))

player_index = dict(zip(players,range(len(players))))

pos_limits = World().pos_limits

pos = [[None for i in range(5)] for j in range(len(players))]
bg_vals = [[None for i in range(5)] for j in range(len(players))]
true_totals = [[None for i in range(5)] for j in range(len(players))]
totals = [[None for i in range(5)] for j in range(len(players))]
angles = [[None for i in range(5)] for j in range(len(players))]
speeds = [[None for i in range(5)] for j in range(len(players))]

bg_sum = [0.0 for j in range(len(players))]
init_totals = [0.0 for j in range(len(players))]

times = [None for i in range(5)]

errs = {}
aves = {}

groups = {
    'pos':['from last', 'from this'],
    'bg':['two back pos', 'last pos', 'this pos', 'next pos', 'last time', 'next time'],
    'totals':['from last', 'from this']
}

#
# pos:
#  from last : position[i] = f(position[i-1], angle[i-1], speed[i-1])
#  from this : position[i] = f(position[i-1], angle[i], speed[i])
#
# bg:
#  two back pos : score[i] = g(position[i-2], time[i-2])
#  last pos : score[i] = g(position[i-1], time[i-1])
#  this pos : score[i] = g(position[i], time[i])
#  next pos : score[i] = g(position[i+1], time[i+1])
#  last time : score[i] = g(position[i], time[i-1])
#  next time : score[i] = g(position[i], time[i+1])
#
# totals:
#  from last : total[i] = h(total[i-1], score[0...i-1])
#  from this : total[i] = h(total[i-1], score[0...i])
#
pars = {
    'pos':[1, 2],
    'bg':[(0,0), (1,1), (2,2), (3,3), (2,1), (2,3)],
    'totals':[1, 2]
}

for err_type in groups:

    errs[err_type] = {}
    aves[err_type] = {}
    
    for g in groups[err_type]:

        errs[err_type][g] = 0
        aves[err_type][g] = 0

n = 0
        
for t in range(2880):
    
    sub = df[df['tick'] == t]
    sub_plus = df[df['tick'] == t+1]

    times = times[1:] + [t]
    
    for i in list(sub.index):

        pid = player_index[sub['pid'][i]]
        
        pos[pid] = pos[pid][1:] + [np.array([sub['x_pos'][i], sub['y_pos'][i]])] 
        bg_vals[pid] = bg_vals[pid][1:] + [sub['bg_val'][i]]
        true_totals[pid] = true_totals[pid][1:] + [sub['total_points'][i]]
        angles[pid] = angles[pid][1:] + [sub['angle'][i]]
        speeds[pid] = speeds[pid][1:] + [sub['velocity'][i]]

        bg_sum[pid] += sub['bg_val'][i]

        if t == 0:
            init_totals[pid] = sub['total_points'][i]
        
        if t > 4:

            n += 1
            
            for u in range(5):
                totals[pid][u] = bg_sum[pid] - sum(bg_vals[pid][-(4-u):])
            
            # position errors
            for j,g in enumerate(groups['pos']):
                
                ind = pars['pos'][j]
                err = np.linalg.norm(pos[pid][2] - get_new_pos(pos[pid][1], angles[pid][ind], speeds[pid][ind], pos_limits))
                
                errs['pos'][g] += err
                aves['pos'][g] += err > 0.01

            # background errs
            for j,g in enumerate(groups['bg']):
                
                if bg_vals[pid][2] != 0:
                    
                    inds = pars['bg'][j]
                    err = abs(bg_vals[pid][2] - get_score(pos[pid][inds[0]], times[inds[1]], background_dir, pos_limits))
                    # if err > 0.01 and g == 'last pos':
                    #     print pos[pid][inds[0]-1], pos[pid][inds[0]], pos[pid][inds[0]+1] 
                    #     print bg_vals[pid][1], bg_vals[pid][2], bg_vals[pid][3], get_score(pos[pid][inds[0]], times[inds[1]], background_dir, pos_limits)
                
                    errs['bg'][g] += err
                    aves['bg'][g] += err > 0.01
                
            # totals errs
            for j,g in enumerate(groups['totals']):
                
                ind = pars['totals'][j]
                val = int((totals[pid][ind] / 2880.0 * 1.25) * 100)/100.0
                err = abs((true_totals[pid][2] - init_totals[pid]) -  val)
                
                errs['totals'][g] += err
                aves['totals'][g] += err > 0.01

for err_type in errs:
    print '----'
    print err_type
    for method in errs[err_type]:
        print method, errs[err_type][method]/float(n), aves[err_type][method]/float(n)

print 'bg: last pos, pos: from this, totals: from this'

