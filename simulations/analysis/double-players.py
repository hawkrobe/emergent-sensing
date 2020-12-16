import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import pylab

game_dir = '../../out/pilot-2015-01-22/games/'

all_players = {}

for game in os.listdir(game_dir):
    if game[-4:] != '.csv':
        continue    
    game_data = pd.io.parsers.read_csv(game_dir + game)
    players = set(game_data['pid'])
    for p in players:
        print 'Checking...'
        if p in all_players:
            print p
        all_players[p] = 1

