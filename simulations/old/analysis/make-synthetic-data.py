
import pandas as pd
import numpy as np
import os, sys

in_dir = '../../' + sys.argv[1] + '/'#'../../goal-inference-simulations/'
out_dir = '../../synthetic-' + sys.argv[1] + '/'#'../../synthetic-goal-inference-simulations/'

subset = '1en01'

try:
    os.makedirs(out_dir)
except:
    pass

games = {1:{},2:{},3:{},4:{},5:{},6:{}}

for game in os.listdir(in_dir):
    if game[-4:] != '.csv':
        continue
    
    bg_file = game.split('_')[-2]
    
    if bg_file.split('-')[1] != subset:
        continue    
    
    data = pd.io.parsers.read_csv(in_dir + game)
    players = set(data['pid'])
    n = len(players)

    if bg_file in games[n]:
        games[n][bg_file][game] = []
    else:
        games[n][bg_file] = {game:[]}
    
    for p in players:
        games[n][bg_file][game] += [data[data['pid'] == p].copy()]

count = 0
            
for n in games:
    
    for bg in games[n]:

        for g in games[n][bg]:
            
            count += 1

            assert len(games[n][bg][g]) == n
            
            if n == 1:

                df = games[n][bg][g][0]

            else:

                df = pd.DataFrame()
                inds = np.random.permutation(games[1][bg].keys())
                
                j = 0
                for i in range(n):
                    
                    found = False
                    tick = max(games[n][bg][g][i]['tick'])
                    
                    while not found:
                        
                        sim = games[1][bg][inds[j]][0]
                        if max(sim['tick']) >= tick:
                            include = sim.loc[sim['tick'] <= tick].copy()
                            df = df.append(include)
                            found = True
                        
                        j += 1
                
                df = df.sort(['tick','pid'])
            
            df.to_csv(out_dir + g, index = False, columns = ['pid','tick','active','x_pos','y_pos','velocity','angle','bg_val','total_points'])

