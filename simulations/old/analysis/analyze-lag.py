import pandas as pd
import numpy as np
import os, sys
import matplotlib.pyplot as plt
import pylab

sys.path.append("../utils/")
from get_inactive import *


game_id = 'data'
outlier_perc = 0.1
plot = False

game_dir = '../../out/' + game_id + '/games/'
latency_dir = '../../out/' + game_id + '/latencies/'

inactive = get_inactive(game_id, False)

stats = {}
counts = {}

for game in os.listdir(game_dir):
    if game[-4:] != '.csv':
        continue    
    game_data = pd.io.parsers.read_csv(game_dir + game)
    lag = pd.io.parsers.read_csv(latency_dir + game)
    players = set(game_data['pid'])
    n = len(players)
    for p in players:
        player_data = game_data[game_data['pid'] == p]
        player_lag = lag[lag['pid'] == p]
        if p not in inactive:
            sub = player_lag[(player_lag['tick'] >= 0)*(player_lag['tick'] <= 2880)]
            if len(sub) > 0:
                lags = list(sub['latency'])
                stats[n] = stats[n] + [lags] if n in stats else [lags]
                count = [np.mean(sub['latency'] > 125)]
                counts[n] = counts[n] + count if n in counts else count
                print p, game, count

print
print 'mean lags'
for n in sorted(counts.keys()):
    print n, np.mean(counts[n]), np.std(counts[n])  

print
print 'mean lags without outlier players'
for n in sorted(counts.keys()):
    counts[n] = np.array(counts[n])
    print n, np.mean(counts[n][counts[n] < outlier_perc]), np.std(counts[n][counts[n] < outlier_perc])

print
print '% outliers'
for n in  sorted(counts.keys()):
    print n, np.mean(counts[n] >= outlier_perc), len(counts[n])

if plot:
    bins = np.linspace(0, 200, 100)
    for n in stats:
        i = 0
        for lags in stats[n]:
            plt.hist(lags, bins, label=str(n) + ' Players')
            pylab.xlim([0,200])
            plt.xlabel('Latency')
            plt.ylabel('Frequency')
            plt.legend(loc='upper right')
            plt.savefig('../../plots/latencies-'+str(n)+'-'+str(i)+'.png')
            plt.clf()
            i += 1

    bins = np.linspace(0, 200, 100)
    for n in stats:
        i = 0
        all_lags = []
        for lags in stats[n]:
            all_lags += lags
        plt.hist(all_lags, bins, label=str(n) + ' Players')
        pylab.xlim([0,200])
        plt.xlabel('Latency')
        plt.ylabel('Frequency')
        plt.legend(loc='upper right')
        plt.savefig('../../plots/all-latencies-'+str(n)+'.png')
        plt.clf()
        i += 1

