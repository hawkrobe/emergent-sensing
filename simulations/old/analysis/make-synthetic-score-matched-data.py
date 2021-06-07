
import pandas as pd
import numpy as np
import os, sys
import copy

in_dir = '../../' + sys.argv[1] + '/'#'../../goal-inference-simulations/'
out_dir = '../../synthetic-score-matched-' + sys.argv[1] + '/'#'../../synthetic-goal-inference-simulations/'

subset = '1en01'

try:
    os.makedirs(out_dir)
except:
    pass

games = {1:{},2:{},3:{},4:{},5:{},6:{}}
score_index = {}

for game in os.listdir(in_dir):
    if game[-4:] != '.csv':
        continue
    
    bg_file = game.split('_')[-2]
    
    if bg_file.split('-')[1] != subset:
        continue    
    
    data = pd.io.parsers.read_csv(in_dir + game)
    players = set(data['pid'].dropna())
    n = len(players)

    if bg_file in games[n]:
        games[n][bg_file][game] = []
    else:
        games[n][bg_file] = {game:[]}
    
    for p in players:
        games[n][bg_file][game] += [data[data['pid'] == p].copy()]

    if n == 1:
        if max(data['tick']) < 1440:
            val = np.mean(data['bg_val'])
        else:
            val = np.mean(data[data['tick']>=1440]['bg_val'])
        if bg_file in score_index:
            assert val not in score_index[bg_file]
            score_index[bg_file][val] = game
        else:
            score_index[bg_file] = {val:game}

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

                sc_ind = copy.deepcopy(score_index)

                scores = []
                for i in range(n):
                    scores += [np.mean(games[n][bg][g][i]['bg_val'])]
                
                for i in np.argsort(-np.array(scores)):
                    
                    ticks = games[n][bg][g][i]['tick']
                    tick = max(ticks)
                    if tick < 1440:
                        val = np.mean(games[n][bg][g][i]['bg_val'])
                    else:
                        val = np.mean(games[n][bg][g][i][ticks >= 1440]['bg_val'])
                    
                    singles = sc_ind[bg].keys()
                    inds = np.argsort(abs(np.array(singles) - val))

                    j = 0
                    found = False
                    
                    while not found:
                        
                        comparison_game = sc_ind[bg][singles[inds[j]]]
                        
                        sim = games[1][bg][comparison_game][0]
                        if max(sim['tick']) >= tick:
                            include = sim.loc[sim['tick'] <= tick].copy()
                            df = df.append(include)
                            del(sc_ind[bg][singles[inds[j]]])
                            found = True
                        
                        j += 1
                    
                df = df.sort(['tick','pid'])
            
            df.to_csv(out_dir + g, index = False, columns = ['pid','tick','active','x_pos','y_pos','velocity','angle','bg_val','total_points'])

